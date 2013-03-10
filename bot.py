import asyncore
import irc
import logging
import pkgutil
import re
import socket
import sqlite3
import time
from contextlib import contextmanager
from exc import ConfigException
from threading import Thread, Timer

logger = logging.getLogger(__name__)


class WrappedBot(object):
    def __init__(self, origobj):
        self.obj = origobj
        self.sender = None
        self.target = None
        self.line = None
        self.match = None
        self.cmd = None
        self.params = None

    def __str__(self):
        return "Wrapped: " + str(self.obj)

    def __getattr__(self, attr):
        return getattr(self.obj, attr)


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
    def __init__(self, bot, config):
        self.rule = None
        self.config = {}
        self.config['threadable'] = config.get("thredeable", False)
        if self.config['threadable']:
            self.config['thread_timeout'] = config.get("thread_timeout", 5.0)

    def run(self, bot, params):
        pass

    def unload(self):
        pass


class Bot(object):
    def __init__(self, config):
        self.config = {}
        self.set_config(config)
        logger.debug('Modules database path = %s',
                     self.config['modules_database_path'])
        self.modules = {
            # 'type': [(pack_name, regexp, module)...]
            'privmsg': [],
            'kick': [],
        }
        self.load_modules()
        self.irc = None

    def handle_privmsg(self, _irc, prefix, command, params):
        sender = prefix
        nick = prefix.split('!', 1)[0]
        msg = str(params[-1])
        channel = params[0]
        for mdl in self.modules["privmsg"]:
            match = mdl[1].match(msg)
            if match is None:
                continue
            logger.debug("Matching module: %s" % mdl[2].__class__)
            obj = WrappedBot(self)
            obj.sender = sender
            obj.target = channel
            obj.line = msg
            obj.match = match
            if mdl[2].config['threadable']:
                timeout = mdl[2].config['thread_timeout']
                run_in_background(timeout)(mdl[2].run)(obj, (nick, msg))
            else:
                mdl[2].run(obj, (nick, msg))

    def handle_notice(self, _irc, prefix, command, params):
        logger.debug('(prefix, command, params): %s)', (prefix, command, params))
        if prefix == self.config['host'] and params[0] == self.config['nick']:
            for chan in self.config['channels']:
                self.irc.cmd(['JOIN', chan])

    def say(self, target, msg):
        self.irc.cmd(['PRIVMSG', target, msg])

    def connect(self):
        cfg = self.config
        self.irc = irc.IRC(
            cfg['host'],
            cfg['port'],
            cfg['nick'],
            cfg['realname'],
            cfg['password'],
            cfg['ssl'],
            cfg['encoding']
        )
        self.irc.handlers['PRIVMSG'] = self.handle_privmsg
        self.irc.handlers['NOTICE'] = self.handle_notice

    def main(self):
        while True:
            try:
                self.connect()
                asyncore.loop()
            except socket.error as exc:
                logger.error('Problem connecting: %(errno)s: %(strerror)s' % {
                    'errno': exc.errno,
                    'strerror': exc.strerror,
                })
            except KeyboardInterrupt as exc:
                self.close()
                raise exc
            time.sleep(4)

    @contextmanager
    def get_db(self):
        db = sqlite3.connect(self.config['modules_database_path'])
        yield db
        db.commit()
        db.close()

    def close(self):
        if self.irc is not None:
            self.irc.quit()

    def load_modules(self):
        logger.debug('Loading modules from directories:\n%s',
                     self.config['modules_paths'])
        paths = self.config['modules_paths']
        modules = {
            'load': self.config['load_modules'],
            'block': self.config['block_modules'],
        }
        for (importer, name, _) in pkgutil.iter_modules(paths):
            logger.debug('Checking module: %s', name)
            if name in modules['load'] and name not in modules['block']:
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
                         pkgutil.iter_modules(self.modules_paths))
        for (importer, name, _) in modules:
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

    @staticmethod
    def prepare_module_config(config):
        prepared = {}
        for key in config:
            if not isinstance(config[key][0], config[key][1]):
                raise ConfigException('config option %s needs %s, but %s given'
                                      % (key, config[key][1], config[key][0]))
            else:
                prepared[key] = config[key][0]
        return prepared

    def set_config(self, conf):
        essentials = ('host', 'port', 'nick', 'realname')
        defaults = {
            'password': None,
            'ssl': False,
            'encoding': 'utf8',
            'modules_paths': ['/modules'],
            'modules_database_path': '.db_modules.sqlite3',
            'load_modules': [],
            'block_modules': [],
            'channels': [],
        }
        try:
            for key in essentials:
                self.config[key] = getattr(conf, key)
        except AttributeError as exc:
            logger.error('Missing or incorrect configuration: %s', str(exc))
            raise exc
        for key, value in defaults.items():
            self.config[key] = getattr(conf, key, value)
