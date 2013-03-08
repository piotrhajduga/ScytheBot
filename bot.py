import logging
import irc
import pkgutil
import re
import time
import sqlite3
from contextlib import contextmanager
from threading import Timer, Thread

logger = logging.getLogger(__name__)


class Wrapper(object):
    def __init__(self, origobj):
        self.obj = origobj

    def __str__(self):
        return "Wrapped: " + str(self.obj)

    def __getattr__(self, attr):
        return getattr(self.obj, attr)


class ConfigException(BaseException):
    pass


def noop(*args, **kwargs):
    pass


def run_per_minute(max_runs_per_m, run_if_too_often):
    def decorate(func):
        def run(*args, **kwargs):
            if run.__last_minute == int(time.time()) / 60:
                run.__runs_last_minute += 1
                if max_runs_per_m >= run.__runs_last_minute:
                    return func(*args, **kwargs)
                else:
                    return run_if_too_often(*args, **kwargs)
            else:
                run.__runs_last_minute = 0
                run.__last_minute = int(time.time()) / 60
                return func(*args, **kwargs)
        run.__last_minute = time.time()
        run.__runs_last_minute = 0
        return run
    return decorate


def run_in_background(timeout=None):
    def decorate(func):
        def run(*args, **kwargs):
            timer = False

            def f_and_timer(*args, **kwargs):
                func(*args, **kwargs)
                if timer:
                    timer.cancel()

            logger.debug('Starting background thread with timeout %s', timeout)
            thread = Thread(target=f_and_timer, args=args, kwargs=kwargs)

            def stop():
                logger.debug('Stopping thread %s', thread)
                thread.terminate()

            if timeout is not None:
                timer = Timer(timeout, stop)
                timer.start()

            thread.start()
            return thread
        return run
    return decorate


class Module(object):
    rule = None

    def __init__(self, bot, config):
        self.config = config
        self.config["threadable"] = config.get("thredeable", False)
        if self.config["threadable"]:
            self.config["thread_timeout"] = config.get("thread_timeout", 5.0)

    def run(self, bot, params):
        pass

    def unload(self):
        pass


class Bot(irc.IRC):
    modules = dict()  # { "type" : ("pack_name", "regexp", "module") }

    def __init__(self, config):
        irc.IRC.__init__(self, config)
        from os.path import expanduser, expandvars
        self.config["modules_paths"] = [expanduser(expandvars(path))
                                        for path in config.modules_paths]
        self.config["modules_database_path"] = expanduser(
            expandvars(config.modules_database_path))
        logger.debug('Modules database path = %s',
                     self.config["modules_database_path"])
        self.config["load_modules"] = config.load_modules
        self.config["block_modules"] = config.block_modules
        self.config["channels"] = config.channels
        self.modules["privmsg"] = list()
        self.modules["cmd"] = list()
        self.modules["kick"] = list()
        self.load_modules()

    @contextmanager
    def get_db(self):
        db = sqlite3.connect(self.config["modules_database_path"])
        yield db
        db.commit()
        db.close()

    def close(self):
        irc.IRC.close(self)

    def load_modules(self):
        logger.debug('Loading modules from directories:\n%s',
                     self.config["modules_paths"])
        for (importer, name, ispkg) in \
                pkgutil.iter_modules(self.config["modules_paths"]):
            logger.debug('Checking module: %s', name)
            if name in self.config["load_modules"] \
                    and name not in self.config["block_modules"]:
                try:
                    self.load_module_with_importer(importer, name)
                    logger.debug('Loaded module: %s', name)
                except BaseException:
                    logger.exception('Cannot load: %s', name)
            else:
                logger.debug('Module not marked to be loaded: %s', name)

    def load_module_with_importer(self, importer, pack_name, load_modules=None):
        logger.debug('Loading modules from pack: %s', pack_name)
        loader = importer.find_module(pack_name)
        module_pack = loader.load_module(pack_name)
        module_names = module_pack.__module_class_names__
        logger.debug('Modue names: %s', ', '.join(module_names))
        for module_name in module_names:
            if load_modules is None or module_name in load_modules:
                module = getattr(module_pack, module_name)
                try:
                    logger.debug('Trying: %s', module)
                    obj = module(self, self.prepare_module_config(
                        getattr(module_pack, '__module_config__', {})))
                    if obj:
                        mdl = (pack_name, re.compile(obj.rule), obj)
                        if not hasattr(obj, "handler_type"):
                            obj.handler_type = "privmsg"
                        if self.modules[obj.handler_type] is None:
                            self.modules[obj.handler_type] = list()
                        self.modules[obj.handler_type].insert(0, mdl)
                except BaseException:
                    logger.exception('Cannot load %s from %s',
                                     module_name, pack_name)

    def load_module(self, pack_name, load_modules=None):
        modules = filter(lambda m: m[1] == pack_name,
                         pkgutil.iter_modules(self.config["modules_paths"]))
        for (importer, name, ispkg) in modules:
            try:
                self.load_module_with_importer(importer, name,
                                               load_modules=load_modules)
            except BaseException:
                logger.exception('Cannot load %s', name)

    def unload_module(self, pack_name, module_name=None):
        modules = list()
        for k in self.modules:
            modules.extend(filter(lambda m: m[0] == pack_name
                           and (module_name is not None
                           or m[2].__class__.__name__ == module_name),
                           self.modules[k]))
        for mdl in modules:
            logger.info('Unloading %s.%s', mdl[0], mdl[2])
            self.modules[mdl[2].handler_type].remove(mdl)
            mdl[2].unload()

    def prepare_module_config(self, config):
        prepared = {}
        for key in config:
            if not isinstance(config[key][0], config[key][1]):
                raise ConfigException('config option %s needs %s, but %s given'
                                      % (key, config[key][1], config[key][0]))
            else:
                prepared[key] = config[key][0]
        return prepared

    def handle_cmd(self, sender, cmd, params):
        for mdl in self.modules["cmd"]:
            match = mdl[1].match("%s :%s" % (cmd, params))
            if match is None:
                continue
            logger.debug("Matching module: %s" % mdl[2].__class__)
            obj = Wrapper(self)
            obj.sender = sender
            obj.cmd = cmd
            obj.params = params
            obj.match = match
            mdl[2].run(obj, (cmd, params))

    def handle_privmsg(self, sender, target, msg):
        if not msg:
            return
        dont_do = list()
        for mdl in self.modules["privmsg"]:
            if mdl in dont_do:
                return
            dont_do.append(mdl)
            match = mdl[1].match(msg)
            if match is None:
                continue
            logger.debug("Matching module: %s" % mdl[2].__class__)
            obj = Wrapper(self)
            obj.sender = sender
            obj.target = target
            obj.line = msg
            obj.match = match
            if mdl[2].config['threadable']:
                timeout = mdl[2].config['thread_timeout']
                run_in_background(timeout)(mdl[2].run)(obj, (sender, msg))
            else:
                mdl[2].run(obj, (sender, msg))
