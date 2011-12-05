# -*- coding: utf-8 -*-
__module_class_names__ = [
<<<<<<< HEAD
    'Swear',
    'Sing',
    'Yeah'
    ]
=======
	'Swear',
	'Sing',
	'Yeah'
	]
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac

from bot import Module
import random, os.path

INPUT_FILE = os.path.expanduser("~/.ircbot/modulefiles/sing.in")

class Swear(Module):
<<<<<<< HEAD
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = '(?i)' + bot.config["nick"] + '(:|,) ?.*(dup(?:i|a|o)|pierd(?:a|o)l|jeb(?:aj|a?n)|chuj|ciul|kurw).*'

    def run(self, bot, params):
        choices = ('and I\'m like: fuck youuuu!',
                'can\'t touch me!',
                'I\'m a T.N.T!',
                'HALT! HAMMERZEIT!',
                'nie klnij kmiocie!',
                'mwuahahahahahaha!'
                )
        bot.say(bot.target, bot.sender.split("!")[0] + ': ' + random.choice(choices))

class Sing(Module): 
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"(?i)%s[,:].*?(sing|(ś|s)piew|piosenk|song).*" % bot.config["nick"]
        self.songs = []
        with open(INPUT_FILE,"rt") as f:
            for line in f:
                self.songs.append(line)


    def run(self, bot, params):
        bot.say(bot.target, bot.sender.split("!")[0] + ': ' + random.choice(self.songs))

class Yeah(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i)%s[,:] ?ye+a+h.*' % bot.config["nick"]

    def run(self, bot, params):
        bot.say(bot.target, bot.sender.split("!")[0] + ': ' + 'oh yeah!')
=======
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = '(?i)' + bot.config["nick"] + '(:|,) ?.*(dup(?:i|a|o)|pierd(?:a|o)l|jeb(?:aj|a?n)|chuj|ciul|kurw).*'

	def run(self, bot, params):
		choices = ('and I\'m like: fuck youuuu!',
				'can\'t touch me!',
				'I\'m a T.N.T!',
				'HALT! HAMMERZEIT!',
				'nie klnij kmiocie!',
				'mwuahahahahahaha!'
				)
		bot.say(bot.target, bot.sender.split("!")[0] + ': ' + random.choice(choices))

class Sing(Module): 
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r"(?i)%s[,:].*?(sing|(ś|s)piew|piosenk|song).*" % bot.config["nick"]
		self.songs = []
		with open(INPUT_FILE,"rt") as f:
			for line in f:
				self.songs.append(line)


	def run(self, bot, params):
		bot.say(bot.target, bot.sender.split("!")[0] + ': ' + random.choice(self.songs))

class Yeah(Module):
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = r'(?i)%s[,:] ?ye+a+h.*' % bot.config["nick"]

	def run(self, bot, params):
		bot.say(bot.target, bot.sender.split("!")[0] + ': ' + 'oh yeah!')
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac
