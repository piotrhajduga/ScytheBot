import logging
import socket
import ssl
import re

logger = logging.getLogger(__name__)


class LostConnectionException(BaseException):
    def __str__(self):
        return "Disconnected!"


class ConnectionFailureException(Exception):
    pass


class BadConfigurationException(Exception):
    pass


class IRC(object):
    def __init__(self, config):
        self.connected = False
        self.buffer = str()
        self.irc = None
        self.config = None
        self.set_config(config)
        self.patterns = dict()
        self.dispatcher_prepare()

    def set_config(self, config):
        self.config = dict()
        try:
            self.config["host"] = config.host
            self.config["port"] = config.port or 6667
            self.config["ssl"] = config.ssl
            self.config["nick"] = config.nick
            self.config["ident"] = config.ident
            self.config["name"] = config.name
            self.config["password"] = config.password
            self.config["encoding"] = config.encoding or "utf-8"
        except Exception:
            logger.error('Bad configuration')
            raise BadConfigurationException()

    def connect(self):
        try:
            self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.config["ssl"]:
                self.irc = ssl.wrap_socket(self.irc)
            self.irc.connect((self.config["host"], self.config["port"]))
            logger.info("Connected to %s:%s", self.config["host"], self.config["port"])
            if self.config["password"]:
                self.msg("PASS %s" % self.config["password"])
            logger.info(
                "Identifying as %s (user:%s,name:%s)",
                self.config["nick"], self.config["ident"], self.config["name"])
            self.msg("NICK %s" % self.config["nick"])
            self.msg(
                "USER %s %s %s :%s" % (self.config["ident"],
                self.config["host"], self.config["nick"], self.config["name"]))
        except socket.error:
            logger.exception('Error connecting to the socket')
            raise ConnectionFailureException()

    def dispatcher_prepare(self):
        self.patterns["cmd"] = r"^\:([^ ]+)[ ]+([^ ]+)[ ]+\:?([^ ].*)?$"
        self.patterns["privmsg"] = r"^\:([^ ]+)[ ]+PRIVMSG[ ]+([^ ]+)[ ]+\:?([^ ].*)?$"
        self.patterns["kick"] = r"^\:([^ ]+)[ ]+KICK[ ]+\:?([^ ].*)?$"
        self.patterns["ping"] = r"^PING[ ]+\:?([^ ].*)?$"
        for ptrn in self.patterns:
            self.patterns[ptrn] = re.compile(self.patterns[ptrn])

    def dispatch(self, msg):
        match = self.patterns["cmd"].match(msg)
        if match:
            sender = match.groups()[0]
            cmd = match.groups()[1]
            params = match.groups()[2]
            self.handle_cmd(sender, cmd, params)
        match = self.patterns["privmsg"].match(msg)
        if match:
            sender = match.groups()[0]
            target = match.groups()[1]
            params = match.groups()[2]
            self.handle_privmsg(sender, target, params)
            return
        match = self.patterns["kick"].match(msg)
        if match:
            params = match.groups()[1]
            self.handle_kick(params)
            return
        match = self.patterns["ping"].match(msg)
        if match:
            params = match.groups()[0]
            self.handle_ping(params)
            return

    def main_loop(self):
        while 1:
            try:
                read = self.irc.recv(512)
                if not read:
                    raise LostConnectionException()
                self.buffer = self.buffer + read.decode(self.config["encoding"])
                temp = self.buffer.split("\n")
                self.buffer = temp.pop()
                for line in temp:
                    line = line.rstrip()
                    logger.info("read < %s" % line)
                    self.dispatch(line)
            except UnicodeDecodeError:
                logger.warn('Cannot decode incoming string')
            except socket.error:
                logger.exception('Socket error.')
                raise LostConnectionException()

    def msg(self, msg):
        logger.info("sending > %s" % msg)
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
        if cmd == "NOTICE" and not self.connected:
            self.connected = True

    def quit(self):
        self.msg("QUIT")
        self.close()

    def close(self):
        pass
