# -*- coding: utf-8 -*-
__module_class_names__ = [
<<<<<<< HEAD
        "Auth",
        "Autojoin",
        "Join",
        "Part",
        "Nick",
        "Send",
        "Msg",
        "Reload",
        "CoreDump",
        ]
=======
		"Auth",
		"Autojoin",
		"Join",
		"Part",
		"Nick",
		"Send",
		"Msg",
		"Reload",
		"CoreDump",
		]
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac

from bot import Module
import traceback,os.path
import pickle,hashlib

FNAME_A = os.path.expanduser('~/.ircbot/modulefiles/bot_admins.pickle')
bot_admins = list() # ("nick", md5("password"), "nick!username@host")

class Autojoin(Module):
<<<<<<< HEAD
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "cmd"
        self.rule = r"376.*"
    
    def run(self, bot, params):
        for chan in bot.config["channels"]:
            bot.msg("JOIN %s" % chan)
            #bot.say(chan, "Hello!")

class Auth(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.auth[ ]+([^ ]+)[ ]+([^ ]+)$"
        global bot_admins
        try:
            bot_admins = pickle.Unpickler(open(FNAME_A,'rb')).load()
        except EOFError:
            bot.verbose_msg("error ! cannot load administrators data")
    
    def run(self, bot, params):
        global bot_admins
        if bot.sender in [x[2] for x in bot_admins]:
            bot.say(bot.sender.split("!")[0],"You already are authorized.")
            return
        username = bot.match.groups()[0]
        password = bot.match.groups()[1].encode(bot.config["encoding"])
        password = hashlib.md5(password).hexdigest()
        for x in bot_admins:
            print("%s,%s == %s,%s" % (username,password,x[0],x[1]))
            if (username,password) == (x[0],x[1]):
                x[2] = bot.sender
                bot.say(bot.sender.split("!")[0],"Succesfully authorized.")
                pickle.Pickler(open(FNAME_A,'wb')).dump(bot_admins)
                return
            bot.say(bot.sender.split("!")[0],"Unable to authorize.")

class Join(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.join (\#[^ ]+)"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        bot.msg("JOIN %s" % bot.match.groups()[0])
        bot.say(bot.match.groups()[0], "Hello!")
        #bot.say(bot.match.groups()[0], "I have been told to join this channel by %s" % params[0])

class Part(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.part (\#[^ ]+)"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        bot.msg("PART %s" % bot.match.groups(0))

class Nick(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.nick ([^ ]+)"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        bot.conf.nick = bot.match.group(0)
        bot.msg("NICK %s" % bot.match.groups(0))

class Msg(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.msg (\#[^ ]+)[ ]+([^ ].*)"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        bot.say(bot.match.group(1),bot.match.group(2))

class Send(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.send[ ]+([^ ].*)"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        bot.msg(bot.match.groups()[0])

class Reload(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.(reload|unload)[ ]+([^ ]+)$"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        mn = bot.match.groups()[1]
        nick = params[0].split("!")[0]
        try:
            bot.unload_module(mn)
        except:
            bot.say(nick, "Unloading of module %s FAILED!" % mn)
            traceback.print_exc()
        else:
            bot.say(nick, "Unloading of module %s SUCCESSFUL!" % mn)
        if bot.match.groups()[0]=='unload':
            return
        try:
            bot.load_module(mn)
        except:
            bot.say(nick, "Reloading of module %s FAILED!" % mn)
            traceback.print_exc()
        else:
            bot.say(nick, "Reloading of module %s SUCCESSFUL!" % mn)

class CoreDump(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.core_dump$"
    
    def run(self, bot, params):
        if bot.sender not in [x[2] for x in bot_admins]:
            return
        #bot.say(bot.sender.split("!")[0],"yeah!")
        for k in bot.modules:
            print(k)
            for m in bot.modules[k]:
                print("\t%s" % m[2])
=======
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "cmd"
		self.rule = r"376.*"
	
	def run(self, bot, params):
		for chan in bot.config["channels"]:
			bot.msg("JOIN %s" % chan)
			#bot.say(chan, "Hello!")

class Auth(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"^\.auth[ ]+([^ ]+)[ ]+([^ ]+)$"
		global bot_admins
		try:
			bot_admins = pickle.Unpickler(open(FNAME_A,'rb')).load()
		except EOFError:
			bot.verbose_msg("error ! cannot load administrators data")
	
	def run(self, bot, params):
		global bot_admins
		if bot.sender in [x[2] for x in bot_admins]:
			bot.say(bot.sender.split("!")[0],"You already are authorized.")
			return
		username = bot.match.groups()[0]
		password = bot.match.groups()[1].encode(bot.config["encoding"])
		password = hashlib.md5(password).hexdigest()
		for x in bot_admins:
			print("%s,%s == %s,%s" % (username,password,x[0],x[1]))
			if (username,password) == (x[0],x[1]):
				x[2] = bot.sender
				bot.say(bot.sender.split("!")[0],"Succesfully authorized.")
				pickle.Pickler(open(FNAME_A,'wb')).dump(bot_admins)
				return
			bot.say(bot.sender.split("!")[0],"Unable to authorize.")

class Join(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"\.join (\#[^ ]+)"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		bot.msg("JOIN %s" % bot.match.groups()[0])
		bot.say(bot.match.groups()[0], "Hello!")
		#bot.say(bot.match.groups()[0], "I have been told to join this channel by %s" % params[0])

class Part(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"\.part (\#[^ ]+)"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		bot.msg("PART %s" % bot.match.groups(0))

class Nick(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"\.nick ([^ ]+)"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		bot.conf.nick = bot.match.group(0)
		bot.msg("NICK %s" % bot.match.groups(0))

class Msg(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"\.msg (\#[^ ]+)[ ]+([^ ].*)"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		bot.say(bot.match.group(1),bot.match.group(2))

class Send(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"\.send[ ]+([^ ].*)"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		bot.msg(bot.match.groups()[0])

class Reload(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"^\.(reload|unload)[ ]+([^ ]+)$"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		mn = bot.match.groups()[1]
		nick = params[0].split("!")[0]
		try:
			bot.unload_module(mn)
		except:
			bot.say(nick, "Unloading of module %s FAILED!" % mn)
			traceback.print_exc()
		else:
			bot.say(nick, "Unloading of module %s SUCCESSFUL!" % mn)
		if bot.match.groups()[0]=='unload':
			return
		try:
			bot.load_module(mn)
		except:
			bot.say(nick, "Reloading of module %s FAILED!" % mn)
			traceback.print_exc()
		else:
			bot.say(nick, "Reloading of module %s SUCCESSFUL!" % mn)

class CoreDump(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"^\.core_dump$"
	
	def run(self, bot, params):
		if bot.sender not in [x[2] for x in bot_admins]:
			return
		#bot.say(bot.sender.split("!")[0],"yeah!")
		for k in bot.modules:
			print(k)
			for m in bot.modules[k]:
				print("\t%s" % m[2])
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac
