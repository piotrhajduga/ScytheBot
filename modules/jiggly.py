# -*- coding: utf-8 -*-
__module_class_names__ = [
    'Swear',
    'Sing',
    'Yeah'
    ]

from bot import Module
import random

class Swear(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = '(?i){0}(:|,) ?.*(dup(?:i|a|o)|pierd(?:a|o)l|jeb(?:aj|a?n)|chuj|ciul|kurw).*'.format(
                bot.config["nick"])

    def run(self, bot, params):
        choices = ('and I\'m like: fuck youuuu!',
                'can\'t touch me!',
                'I\'m a T.N.T!',
                'HALT! HAMMERZEIT!',
                'nie klnij kmiocie!',
                'mwuahahahahahaha!'
                )
        bot.say(bot.target, '{0}: {1}'.format(
            bot.sender.split("!")[0], random.choice(choices)))

class Sing(Module): 
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"(?i){0}[,:].*?(sing|(ś|s)piew|piosenk|song).*".format(
                bot.config["nick"])
        self.create_tables(bot)

    def create_tables(self, bot):
        query = '''CREATE TABLE IF NOT EXISTS sing
            (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
             lyric TEXT NOT NULL)'''
        with bot.get_db() as db:
            db.execute(query)

    def run(self, bot, params):
        query = 'SELECT lyric FROM sing ORDER BY RANDOM() LIMIT 1'
        with bot.get_db() as db:
            row = db.execute(query).fetchone()
        if row:
            bot.say(bot.target, '{0}: {1}'.format(
                bot.sender.split("!")[0], row['lyric']))

class Yeah(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i){0}[,:] ?ye+a+h.*'.format(bot.config["nick"])

    def run(self, bot, params):
        bot.say(bot.target, '{0}: {1}'.format(
            bot.sender.split("!")[0], 'oh yeah!'))
