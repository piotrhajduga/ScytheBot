import irc
import pkgutil, re, traceback
import time
from threading import Timer
from threading2 import Thread

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
            if run.__last_minute == int(time.time())/60:
                run.__runs_last_minute += 1
                if max_runs_per_m >= run.__runs_last_minute:
                    return func(*args, **kwargs)
                else:
                    return run_if_too_often(*args, **kwargs)
            else:
                run.__runs_last_minute = 0
                run.__last_minute = int(time.time())/60
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

            print( 'starting bg thread with timeout %s' % timeout )
            thread = Thread( target = f_and_timer, args=args, kwargs=kwargs )

            def stop():
                print( 'stopping thread %s' % thread )
                thread.terminate()

            if timeout != None:
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
    def __init__(self, config):
        irc.IRC.__init__(
                self,
                config.nick,
                config.ident,
                config.name,
                config.host,
                config.port,
                config.ssl,
                config.password,
                config.encoding
                )
        self.config["modules_paths"] = config.modules_paths
        self.config["load_modules"] = config.load_modules
        self.config["block_modules"] = config.block_modules
        self.config["channels"] = config.channels
        self.modules = dict() # { "type" : ("pack_name", "regexp", "module") }
        self.modules["privmsg"] = list()
        self.modules["cmd"] = list()
        self.modules["kick"] = list()
        self.load_modules()
    
    def load_modules(self):
        for (importer, name, ispkg) in \
                pkgutil.iter_modules(self.config["modules_paths"]):
            if name in self.config["load_modules"] \
                    and name not in self.config["block_modules"]:
                try:
                    self.load_module_with_importer(importer, name)
                except BaseException as exc:
                    self.verbose_msg("Cannot load %s:\n%s" % (name, exc))
    
    def load_module_with_importer(self, importer, pack_name, \
            load_modules=None):
        self.verbose_msg("Loading modules from %s" % pack_name)
        loader = importer.find_module(pack_name)
        module_pack = loader.load_module(pack_name)
        module_names = module_pack.__module_class_names__
        self.verbose_msg('%s' % ', '.join(module_names))
        for module_name in module_names:
            if load_modules is None or module_name in load_modules:
                module = getattr(module_pack, module_name)
                try:
                    self.verbose_msg('    %s' % module)
                    obj = module(self, self.prepare_module_config( \
                            getattr(module_pack, '__module_config__', {})))
                    if obj:
                        mdl = (pack_name, re.compile(obj.rule), obj)
                        if not hasattr(obj,"handler_type"):
                            obj.handler_type = "privmsg"
                        if self.modules[obj.handler_type] is None:
                            self.modules[obj.handler_type] = list()
                        self.modules[obj.handler_type].insert(0, mdl)
                except BaseException as exc:
                    self.verbose_msg('Cannot load %s from %s:\n%s\n' \
                            % (module_name, pack_name, exc))
                    traceback.print_exc()

    def load_module(self, pack_name, load_modules=None):
        modules = filter(lambda m: m[1] == pack_name,
                pkgutil.iter_modules(self.config["modules_paths"]))
        for (importer, name, ispkg) in modules:
            try:
                self.load_module_with_importer(importer, name, \
                        load_modules=load_modules)
            except BaseException as e:
                self.verbose_msg('Cannot load %s:\n%s' % (name, e))
                traceback.print_exc()
    
    def unload_module(self, pack_name, module_name=None):
        modules = list()
        for k in self.modules:
            modules.extend(filter(lambda m: m[0] == pack_name \
                    and (module_name == None \
                    or m[2].__class__.__name__ == module_name), \
                    self.modules[k]))
        for mdl in modules:
            self.verbose_msg('Unloading %s.%s' % (mdl[0], mdl[2]))
            self.modules[mdl[2].handler_type].remove(mdl)
            mdl[2].unload()
    
    def prepare_module_config(self, config):
        prepared = {}
        for key in config:
            if not isinstance(config[key][0], config[key][1]):
                raise ConfigException('config option %s needs %s, \
                        but %s given' \
                        % (key, config[key][1], config[key][0]))
            else:
                prepared[key] = config[key][0]
        return prepared
    
    def handle_cmd(self, sender, cmd, params):
        for mdl in self.modules["cmd"]:
            match = mdl[1].match("%s :%s" % (cmd, params))
            if match is None:
                continue
            self.verbose_msg("\t%s: match!" % mdl[2].__class__)
            try:
                obj = Wrapper(self)
                obj.sender = sender
                obj.cmd = cmd
                obj.params = params
                obj.match = match
                mdl[2].run(obj, (cmd, params))
            except BaseException:
                self.verbose_msg("error ! something went wrong")
                traceback.print_exc()

    def handle_privmsg(self, sender, target, msg):
        dont_do = list()
        for mdl in self.modules["privmsg"]:
            if mdl in dont_do:
                return
            dont_do.append(mdl)
            match = mdl[1].match(msg)
            if match is None:
                continue
            self.verbose_msg("\t%s: match!" % mdl[2].__class__)
            try:
                obj = Wrapper(self)
                obj.sender = sender
                obj.target = target
                obj.line = msg
                obj.match = match
                if mdl[2].config['threadable']:
                    run_in_background(mdl[2].config['thread_timeout']) \
                            (mdl[2].run) \
                            (obj, (sender, msg))
                else:
                    mdl[2].run( obj, (sender, msg))
            except BaseException:
                self.verbose_msg("error ! something went wrong")
                traceback.print_exc()

#    def handle_kick(self, params):
#        for mdl in self.modules["kick"]:
#            match = mdl[1].match(msg)
#            if match is None:
#                continue
#            self.verbose_msg("\t%s: match!" % mdl[2].__class__)
#            try:
#                obj = Wrapper(self)
#                obj.params = params
#                obj.match = match
#                mdl[2].run(obj, (sender, msg))
#            except BaseException:
#                self.verbose_msg("error ! something went wrong")
#                traceback.print_exc()
