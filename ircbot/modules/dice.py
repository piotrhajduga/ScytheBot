# -*- coding: utf-8 -*-
__module_class_names__ = ['Roll']

from bot import Module
import random, os.path

class Roll(Module):
<<<<<<< HEAD
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = '(?i)%s(:|,) *(?:roll)? *([0-9]*)(?:d|k)([0-9]+).*' % bot.config["nick"]

    def run(self, bot, params):
        try:
            n = int(bot.match.groups()[1])
        except:
            n = 1
        d = int(bot.match.groups()[2])
        if n>20 or d>100:
            bot.say(bot.target, bot.sender.split("!")[0] + ": cannot handle these numbers, sorry bro... :(")
            return
        roll = "%dd%d" % (n,d)
        result = ", ".join(["%d" % random.randint(1,d) for i in range(n)])
        bot.say(bot.target, roll + ": " + result )
=======
	def __init__(self, bot, config):
		Module.__init__(self, bot, config)
		self.handler_type = "privmsg"
		self.rule = '(?i)%s(:|,) *(?:roll)? *([0-9]*)(?:d|k)([0-9]+).*' % bot.config["nick"]

	def run(self, bot, params):
		try:
			n = int(bot.match.groups()[1])
		except:
			n = 1
		d = int(bot.match.groups()[2])
		if n>20 or d>100:
			bot.say(bot.target, bot.sender.split("!")[0] + ": cannot handle these numbers, sorry bro... :(")
			return
		roll = "%dd%d" % (n,d)
		result = ", ".join(["%d" % random.randint(1,d) for i in range(n)])
		bot.say(bot.target, roll + ": " + result )
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac
