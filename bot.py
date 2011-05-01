import irc

class Wrapper(object):
	def __init__(self, origobj):
		self.obj = origobj
	def __str__(self):
		return "Wrapped: " + str(self.obj)
	def __getattr__(self, attr):
		return getattr(self.obj, attr)

class Module(object):
	rule = None
	def __init__(self, bot, conf):
		self.conf = conf
	def run(self, bot, nick, msg):
		pass
	def unload(self):
		pass

class Bot(irc.IRC):
	pass
