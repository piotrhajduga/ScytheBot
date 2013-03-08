# -*- coding: utf-8 -*-
__module_class_names__ = [
    'Swear',
    'Sing',
    'RememberSong',
    'Yeah'
]

import logging
import random
import sqlite3
from bot import Module
from modules.admin import is_authorised

logger = logging.getLogger(__name__)


def create_tables(bot):
    query = '''CREATE TABLE IF NOT EXISTS sing
        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
            lyric TEXT NOT NULL)'''
    with bot.get_db() as db:
        db.execute(query)


class Swear(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = '(?i){0}(:|,) ?.*(dup(?:i|a|o)|pierd(?:a|o)l|jeb(?:aj|a?n)|chuj|ciul|kurw).*'.format(
            bot.config["nick"])

    def run(self, bot, params):
        choices = (
            'and I\'m like: fuck youuuu!',
            'can\'t touch me!',
            'I\'m a T.N.T!',
            'HALT! HAMMERZEIT!',
            'nie klnij kmiocie!',
            'mwuahahahahahaha!'
        )
        bot.say(bot.target, '{0}: {1}'.format(
            bot.sender.split("!")[0], random.choice(choices)))


class RememberSong(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,] *?(?:remember song|pami[ęe]taj piosenk[ęe]) *(.*)' % bot.config['nick']
        create_tables(bot)

    def run(self, bot, params):
        with bot.get_db() as db:
            authorised = is_authorised(db, bot.sender)
        if not authorised:
            logger.warn("Unauthorized attempt to teach a lyric")
            return
        query = 'INSERT INTO sing (lyric) VALUES (?)'
        logger.debug('groups: %s', bot.match.groups())
        lyric = bot.match.groups()[0].strip()
        with bot.get_db() as db:
            db.execute(query, (lyric,))
        bot.say(bot.target, 'I just learnt: %s' % lyric)


class Sing(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"(?i){0}[,:].*?(sing|(ś|s)piew|piosenk|song).*".format(
            bot.config["nick"])
        create_tables(bot)

    def run(self, bot, params):
        query = 'SELECT lyric FROM sing ORDER BY RANDOM() LIMIT 1'
        with bot.get_db() as db:
            db.row_factory = sqlite3.Row
            row = db.execute(query).fetchone()
            bot.say(bot.target, row['lyric'])


class Yeah(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i){0}[,:] ?ye+a+h.*'.format(bot.config["nick"])

    def run(self, bot, params):
        bot.say(bot.target, '{0}: {1}'.format(
            bot.sender.split("!")[0], 'oh yeah!'))
