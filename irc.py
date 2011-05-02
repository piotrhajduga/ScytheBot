import socket, ssl, imp
import re, traceback

class ConnectionError(BaseException):
	def __str__(self):
		return "Disconnected!"

class IRC(object):
	def __init__(self, nick, ident, name, host, port=6667, ssl=False, password=None, encoding="utf-8"):
		self.connected = False
		self.buffer = ""
		self.irc = ""
		self.dispatcher_prepare()
		self.config = dict()
		self.config["host"] = host
		self.config["port"] = port
		self.config["ssl"] = ssl
		self.config["nick"] = nick
		self.config["ident"] = ident
		self.config["name"] = name
		self.config["password"] = password
		self.config["encoding"] = encoding

	def connect(self):
		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.config["ssl"]:
			self.irc = ssl.wrap_socket(self.irc)
		self.irc.connect((self.config["host"], self.config["port"]))
		self.verbose_msg("Connected to %s:%s" % (self.config["host"], self.config["port"]))
		if self.config["password"]:
			self.msg("PASS %s" % self.config["password"])
		self.verbose_msg("Identifying as %s (user:%s,name:%s)" % (self.config["nick"],self.config["ident"],self.config["name"]))
		self.msg("NICK %s" % self.config["nick"])
		self.msg("USER %s %s %s :%s" % (self.config["ident"], self.config["host"], self.config["nick"], self.config["name"]))
		self.verbose_msg("function # returning from connect()")
	
	def quit(self):
		self.irc.msg("QUIT")
		self.irc.close()

	def dispatcher_prepare(self):
		self.patterns = dict()
		self.patterns["cmd"] = r"^\:([^ ]+)[ ]+([^ ]+)[ ]+\:?([^ ].*)?$"
		self.patterns["privmsg"] = r"^\:([^ ]+)[ ]+PRIVMSG[ ]+([^ ]+)[ ]+\:?([^ ].*)?$"
		self.patterns["kick"] = r"^\:([^ ]+)[ ]+KICK[ ]+\:?([^ ].*)?$"
		self.patterns["ping"] = r"^PING[ ]+\:?([^ ].*)?$"
		for p in self.patterns:
			self.patterns[p] = re.compile(self.patterns[p])

	def dispatch(self, msg):
		m = self.patterns["cmd"].match(msg)
		if m:
			sender = m.groups()[0]
			cmd = m.groups()[1]
			params = m.groups()[2]
			self.handle_cmd(sender,cmd,params)
		m = self.patterns["privmsg"].match(msg)
		if m:
			sender = m.groups()[0]
			target = m.groups()[1]
			params = m.groups()[2]
			self.handle_privmsg(sender,target,params)
			return
		m = self.patterns["kick"].match(msg)
		if m:
			params = m.groups()[1]
			self.handle_kick(params)
			return
		m = self.patterns["ping"].match(msg)
		if m:
			params = m.groups()[0]
			self.handle_ping(params)
			return
	
	def main_loop(self):
		while 1:
			try:
				read = self.irc.recv(512)
				if not read:
					raise ConnectionError()
				self.buffer = self.buffer + read.decode(self.config["encoding"])
				temp = self.buffer.split("\n")
				self.buffer = temp.pop()
				for line in temp:
					line = line.rstrip()
					self.verbose_msg("read < %s" % line)
					self.dispatch(line)
			except KeyboardInterrupt as e:
				raise e
			except ConnectionError as e:
				raise e
			except:
				self.msg("error ! unhandled exception")
				traceback.print_exc()
	
	def verbose_msg(self, msg):
		print("<> %s" % msg)
	
	def msg(self, msg):
		self.verbose_msg("sending > %s" % msg)
		msg = "%s\r\n" % msg
		self.irc.send(msg.encode(self.config["encoding"]))
	
	def say(self, target, msg):
		self.msg("PRIVMSG %s :%s" % (target, msg))
	
	def handle_kick(self, params):
		pass

	def handle_ping(self, params):
		self.msg("PONG :%s" % params)

	def handle_privmsg(self, sender, target, params):
		pass

	def handle_cmd(self, sender, cmd, params):
		if cmd=="NOTICE" and self.connected==False:
			self.connected = True

	def quit(self):
		self.msg("QUIT")
		self.irc.close()
