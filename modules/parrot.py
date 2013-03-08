# -*- coding: utf-8 -*-
__module_class_names__ = [
    'RememberLess', 'RememberMore',
    'TalkLess', 'TalkMore',
    'RememberSaying', 'SaySaying',
    'RememberYT', 'SayYT',
    'Dump'
]

import logging
import random
import re
import sqlite3
from bot import Module
from modules.admin import is_authorised

logger = logging.getLogger(__name__)

CHANCES = {'remember': 6, 'say': 2, 'thank': 10}
CHOICES = (
    "I love you!",
    "<3",
    ":*",
    "you know that I know..."
)


def create_tables(bot):
    with bot.get_db() as db:
        query = '''CREATE TABLE IF NOT EXISTS parrot_yt_links
            (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
                link TEXT NOT NULL UNIQUE)'''
        db.execute(query)
        query = '''CREATE TABLE IF NOT EXISTS parrot_sayings
            (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
                saying TEXT NOT NULL UNIQUE)'''
        db.execute(query)


def query_data(bot, query):
    with bot.get_db() as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()
        try:
            cur.execute(query)
            return cur.fetchall()
        finally:
            cur.close()


class RememberLess(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,].*?(remember|pami[ęe]taj).*(mniej|less).*' % bot.config["nick"]

    def run(self, bot, params):
        key = 'remember'
        CHANCES[key] = random.randint(1, CHANCES[key])
        logger.info('CHANCES[%s] lowered to: %d', key, CHANCES[key])
        bot.say(bot.target, "I won't be remembering so much from now on")


class RememberMore(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,].*?(remember|pami[ęe]taj).*(wi[ęe]cej|more).*' % bot.config["nick"]

    def run(self, bot, params):
        key = 'remember'
        CHANCES[key] = random.randint(
            CHANCES[key],
            random.randint(CHANCES[key], 100)
        )
        logger.info('CHANCES[%s]: %d', key, CHANCES[key])
        bot.say(bot.target, "More things stay in my memory from now")


class TalkLess(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,].*?(talk|m[óo]w|speak).*(mniej|less).*' % bot.config["nick"]

    def run(self, bot, params):
        for key in ['say', 'thank']:
            CHANCES[key] = random.randint(1, CHANCES[key])
        logger.info('CHANCES lowered to: %s', CHANCES)
        bot.say(bot.target, "ok... I'll keep it down...")


class TalkMore(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,].*?(talk|m[óo]w|speak).*(wi[ęe]cej|more).*' % bot.config["nick"]

    def run(self, bot, params):
        for key in ['say', 'thank']:
            CHANCES[key] = random.randint(
                CHANCES[key],
                random.randint(CHANCES[key], 100)
            )
        logger.info('CHANCES raised to: %s', CHANCES)
        bot.say(bot.target, "haha!")


class RememberSaying(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'.*?(?:[a-zA-Z0-9_.,=?-]+?[:,])? *(.*)'
        create_tables(bot)

    def run(self, bot, params):
        if random.randint(1, 100) > CHANCES['remember']:
            return
        regexp = r'.*(https?\://).*'
        if re.match(regexp, bot.line):
            return
        regexp = r'[.-_/\\].*'
        if re.match(regexp, bot.line):
            return
        saying = bot.match.groups()[0]
        query = 'INSERT INTO parrot_sayings (saying) VALUES (?)'
        with bot.get_db() as db:
            db.execute(query, (saying,))
        if random.randint(1, 100) <= CHANCES['thank']:
            bot.say(bot.target, "Remembered!")
            return
        if random.randint(1, 100) > CHANCES['say']:
            return
        bot.say(bot.target, '{0}: {1}'.format(
            bot.sender.split("!")[0], random.choice(CHOICES)))


class SaySaying(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'([a-zA-Z0-9_.,=?-]+?[:,])?.*'

    def run(self, bot, params):
        modifier = 0
        if bot.match.group(0) and (bot.config["nick"] in bot.match.group(0)):
            modifier = 34
        if random.randint(1, 100) > (CHANCES['say'] + modifier):
            return
        query = 'SELECT saying FROM parrot_sayings ORDER BY RANDOM() LIMIT 1'
        with bot.get_db() as db:
            row = db.execute(query).fetchone()
        if row:
            bot.say(bot.target, '{0}: {1}'.format(
                bot.sender.split("!")[0], row[0]))


class RememberYT(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'.*(http\://[a-z0-9]+\.youtube\.[a-z]+/watch\?v=[a-zA-Z0-9\-_\+\,\.]+)\&?.*'
        create_tables(bot)

    def run(self, bot, params):
        link = bot.match.group(1)
        query = 'SELECT * FROM parrot_yt_links WHERE link=? LIMIT 1'
        with bot.get_db() as db:
            cur = db.cursor()
            rowcount = len(cur.execute(query, (link,)).fetchall())
            cur.close()
        if rowcount:
            return
        query = 'INSERT INTO parrot_yt_links (link) VALUES (?)'
        with bot.get_db() as db:
            db.execute(query, (link,))
        if random.randint(1, 100) > CHANCES['thank']:
            return
        choices = (
            "I love you!", "<3", ":*",
            "you know that I know...",
            "stupido!", "tell me about it",
            "I bet you don't know what is going to happen next..."
        )
        bot.say(bot.target, bot.sender.split("!")[0] + ": " + random.choice(choices))


class SayYT(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'%s[:,].*?(link|jutub|tube|film).*' % bot.config["nick"]

    def run(self, bot, params):
        query = 'SELECT link FROM parrot_yt_links ORDER BY RANDOM() LIMIT 1'
        with bot.get_db() as db:
            row = db.execute(query).fetchone()
        message = row[0] if row else "sorry, don't know any..."
        bot.say(bot.target, message)


class Dump(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.config["threadable"] = True
        self.config["thread_timeout"] = 1.0
        self.handler_type = "privmsg"
        self.rule = r'\.dump'
        create_tables(bot)

    def run(self, bot, params):
        with bot.get_db() as db:
            authorised = is_authorised(db, bot.sender)
        if not authorised:
            logger.warn("Unauthorized attempt to dump the database")
            return
        sender = bot.sender.split('!', 1)[0]
        logger.info("yt_links:")
        query = 'SELECT * FROM parrot_yt_links'
        yt_links = query_data(bot, query)
        bot.say(sender, '%d links to youtube' % len(yt_links))
        for row in yt_links:
            logger.debug(row.keys())
            logger.info("%d: %s", row['id'], row['link'])
        logger.info("sayings:")
        query = 'SELECT * FROM parrot_sayings'
        sayings = query_data(bot, query)
        bot.say(sender, '%d sayings' % len(sayings))
        for row in sayings:
            logger.info("%d: %s", row['id'], row['saying'])
