import asynchat
import logging
import re
import socket
import ssl

logger = logging.getLogger(__name__)


class IRC(asynchat.async_chat):
    reply_names = {
        '001': 'RPL_WELCOME',
        '002': 'RPL_YOURHOST',
        '003': 'RPL_CREATED',
        '004': 'RPL_MYINFO',
        '005': 'RPL_BOUNCE',
        '251': 'RPL_LUSERCLIENT',
        '252': 'RPL_LUSEROP',
        '253': 'RPL_LUSERUNKNOWN',
        '254': 'RPL_LUSERCHANNELS',
        '255': 'RPL_LUSERME',
        '375': 'RPL_MOTDSTART',
        '372': 'RPL_MOTD',
        '376': 'RPL_ENDOFMOTD',
        '331': 'RPL_NOTOPIC',
        '332': 'RPL_TOPIC',
        '353': 'RPL_NAMREPLY',
        '366': 'RPL_ENDOFNAMES',
        '401': 'RPL_NOTICE',
    }

    def __init__(self, server, port, nick, realname, password=None,
                 use_ssl=False, encoding='utf-8'):
        self.encoding = encoding
        self.nick = nick
        sock = IRC._init_socket(server, port, use_ssl)
        asynchat.async_chat.__init__(self, sock=sock)
        self._authenticate(nick, realname, password, server)
        self.ibuffer = []
        self.set_terminator(b'\r\n')
        self.handlers = {
            'PING': IRC.handle_ping,
        }

    @staticmethod
    def _init_socket(server, port, use_ssl=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if use_ssl:
            sock = ssl.wrap_socket(sock)
        sock.connect((server, port))
        logger.info('Connected to %s:%s', server, port)
        return sock

    def _authenticate(self, nick, realname, password, server):
        if password:
            self.cmd(['PASS', password])
        self.cmd(['NICK', nick])
        self.cmd(['USER', nick, nick, server, realname])

    def collect_incoming_data(self, data):
        self.ibuffer.append(data)

    def found_terminator(self):
        def irc_split(s):
            logger.info('recv < %s' % s)
            (prefix, command, params) = re.match(r"""(:[^ ]* |)([a-zA-Z]+|[0-9]{3})(.*)""", s).groups()
            if len(prefix) > 0:
                prefix = prefix[1:-1]  # deleting ':' from the front and ' ' from the end
            command = command.strip()
            command = IRC.reply_names.get(command, command)
            params = params.split(' :')  # for the last parameter, the only one that can contain spaces
            params = params[0].split(' ')[1:] + [' :'.join(params[1:])]
            return (prefix, command, params)
        (prefix, command, params) = irc_split(b''.join(self.ibuffer).decode(self.encoding, 'replace'))
        #logger.debug('(prefix, command, params): %s)', (prefix, command, params))
        self.handlers.get(command, IRC.unhandled_reply_warning)(self, prefix, command, params)
        self.ibuffer = []

    def unhandled_reply_warning(self, prefix, command, params):
        pass

    def cmd(self, msg):
        msg_str = '%s :%s' % (
            ' '.join([str(s).replace(' ', '') for s in msg[:-1]]),
            msg[-1]
        )
        logger.info('send > %s' % msg_str)
        msg_str = '%s\r\n' % msg_str
        self.push(bytearray(msg_str.encode(self.encoding, 'replace')))

    def handle_ping(self, prefix, command, params):
        self.cmd(['PONG', params[0]])

    def quit(self):
        self.cmd(['QUIT'])
