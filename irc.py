import asynchat
import logging
import re
import socket
import ssl
from itertools import chain

logger = logging.getLogger(__name__)


class IRC(asynchat.async_chat):
    patterns = {
        'cmd': re.compile('^\:([^ ]+)[ ]+([^ ]+)[ ]+\:?([^ ].*)?$'),
        'privmsg': re.compile('^\:([^ ]+)[ ]+PRIVMSG[ ]+([^ ]+)[ ]+\:?([^ ].*)?$'),
        'kick': re.compile('^\:([^ ]+)[ ]+KICK[ ]+\:?([^ ].*)?$'),
        'ping': re.compile('^PING[ ]+\:?([^ ].*)?$'),
    }

    def __init__(self, server, port, nick, realname, password=None,
                 use_ssl=False, encoding='utf-8'):
        self.encoding = encoding
        self.nick = nick
        sock = IRC._init_socket(server, port, use_ssl)
        asynchat.async_chat.__init__(self, sock=sock)
        self._authenticate(nick, realname, password)
        self.ibuffer = []
        self.set_terminator(b'\r\n')

    @staticmethod
    def _init_socket(server, port, use_ssl=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if use_ssl:
            sock = ssl.wrap_socket(sock)
        sock.connect((server, port))
        logger.info('Connected to %s:%s', server, port)
        return sock

    def _authenticate(self, nick, realname, password):
        if password:
            self.cmd(['PASS', password])
        logger.info(
            "Identifying as %s (user:%s,name:%s)",
            nick, 0, realname
        )
        self.cmd(['NICK', nick])
        self.cmd(['USER', nick, 0, '*', realname])

    def collect_incoming_data(self, data):
        self.ibuffer.append(data)

    def found_terminator(self):
        line = b''.join(self.ibuffer).decode(self.encoding, 'replace')
        self.dispatch(line)

    def dispatch(self, msg):
        match = self.patterns['cmd'].match(msg)
        if match:
            sender = match.groups()[0]
            cmd = match.groups()[1]
            params = match.groups()[2]
            self.handle_cmd(sender, cmd, params)
        match = self.patterns['privmsg'].match(msg)
        if match:
            sender = match.groups()[0]
            target = match.groups()[1]
            params = match.groups()[2]
            self.handle_privmsg(sender, target, params)
            return
        match = self.patterns['kick'].match(msg)
        if match:
            params = match.groups()[1]
            self.handle_kick(params)
            return
        match = self.patterns['ping'].match(msg)
        if match:
            params = match.groups()[0]
            self.handle_ping(params)
            return

    def cmd(self, msg):
        msg = ' '.join(chain(
            map(lambda s: str(s).replace(' ', ''), msg[:-1]),
            [(':%s' if ' ' in str(msg[-1]) else '%s') % str(msg[-1])]
        ))
        logger.info('sending > %s' % msg)
        msg = '%s\r\n' % msg
        self.push(bytearray(msg.encode(self.encoding, 'replace')))

    def say(self, target, msg):
        self.cmd(['PRIVMSG', target, msg])

    def handle_kick(self, params):
        pass

    def handle_ping(self, params):
        self.cmd(['PONG', params])

    def handle_privmsg(self, sender, target, params):
        pass

    def handle_cmd(self, sender, cmd, params):
        if cmd == 'NOTICE' and not self.connected:
            self.connected = True

    def quit(self):
        self.cmd(['QUIT'])
        self.close()

    def close(self):
        pass
