# -*- coding: utf-8 -*-
__module_class_names__ = [
    "Auth", "Deauth",
    "Autojoin", "Join", "Part",
    "Nick",
    "Send",
    "Msg",
    "Reload",
    "CoreDump",
]

import hashlib
import logging
import sqlite3
from bot import Module
from contextlib import closing

logger = logging.getLogger(__name__)


def create_tables(bot):
    query = '''CREATE TABLE IF NOT EXISTS admins
        (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
            nick TEXT NOT NULL,
            sender TEXT,
            pass TEXT NOT NULL)'''
    with bot.get_db() as db:
        db.execute(query)


def is_authorised(bot):
    query = 'SELECT * FROM admins WHERE sender=?'
    with bot.get_db() as db:
        with closing(db.cursor()) as cur:
            cur.execute(query, (bot.sender,))
            return len(cur.fetchall())


class Autojoin(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "cmd"
        self.rule = r"376.*"

    def run(self, bot, params):
        for chan in bot.config["channels"]:
            bot.msg("JOIN %s" % chan)


class Auth(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.auth[ ]+([^ ]+)[ ]+([^ ]+)$"
        create_tables(bot)

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if authorised:
            bot.say(bot.sender.split("!")[0], "You already are authorized.")
            return
        username = bot.match.groups()[0]
        password = bot.match.groups()[1].encode(bot.config["encoding"])
        password = hashlib.md5(password).hexdigest()
        query = 'UPDATE admins SET sender=? WHERE nick=? AND pass=?'
        with bot.get_db() as db:
            db.execute(query, (bot.sender, username, password))
        if is_authorised(bot):
            bot.say(bot.sender.split("!")[0], "Succesfully authorized.")
        else:
            bot.say(bot.sender.split("!")[0], "Unable to authorize.")


class Deauth(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.deauth$"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        with bot.get_db() as db:
            db.row_factory = sqlite3.Row
            with closing(db.cursor()) as cur:
                query = 'UPDATE admins SET sender="" WHERE sender=?'
                cur.execute(query, (bot.sender,))
        if is_authorised(bot):
            bot.say(bot.sender.split("!")[0], "Unable to deauthorize.")
        else:
            bot.say(bot.sender.split("!")[0], "Succesfully deauthorized.")


class Join(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.join (\#[^ ]+)"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        bot.msg("JOIN %s" % bot.match.groups()[0])
        bot.say(bot.match.groups()[0], "Hello!")


class Part(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.part (\#[^ ]+)"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        bot.msg("PART %s" % bot.match.groups(0))


class Nick(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.nick ([^ ]+)"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        bot.conf.nick = bot.match.group(0)
        bot.msg("NICK %s" % bot.match.groups(0))


class Msg(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.msg (\#[^ ]+)[ ]+([^ ].*)"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        bot.say(bot.match.group(1), bot.match.group(2))


class Send(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.send[ ]+([^ ].*)"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        bot.msg(bot.match.groups()[0])


class Reload(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.(reload|unload)[ ]+([^ ]+)$"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        mn = bot.match.groups()[1]
        nick = params[0].split("!")[0]
        try:
            bot.unload_module(mn)
            bot.say(nick, "Unloading of module %s SUCCESSFUL!" % mn)
        except BaseException as exc:
            logger.exception(str(exc))
            bot.say(nick, "Unloading of module %s FAILED!" % mn)
        if bot.match.groups()[0] == 'unload':
            return
        try:
            bot.load_module(mn)
            bot.say(nick, "Reloading of module %s SUCCESSFUL!" % mn)
        except BaseException as exc:
            logger.exception(str(exc))
            bot.say(nick, "Reloading of module %s FAILED!" % mn)


class CoreDump(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.core_dump$"

    def run(self, bot, params):
        authorised = is_authorised(bot)
        if not authorised:
            bot.say(bot.sender.split("!")[0], "You are not authorized.")
            return
        for k in bot.modules:
            print(k)
            for m in bot.modules[k]:
                print("\t%s" % m[2])
