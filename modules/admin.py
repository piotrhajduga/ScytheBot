# -*- coding: utf-8 -*-
__module_class_names__ = [
        "Auth",
        "Deauth",
        "Autojoin",
        "Join",
        "Part",
        "Nick",
        "Send",
        "Msg",
        "Reload",
        "CoreDump",
        ]

from bot import Module
import traceback
import hashlib
import logging

logger = logging.getLogger(__name__)

def is_authorised(db, sender):
    query = 'SELECT * FROM admins WHERE sender=?'
    rowcount = len(db.execute(query, (sender,)).fetchall())
    return rowcount

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
        self.create_tables(bot)

    def create_tables(self, bot):
        query = '''CREATE TABLE IF NOT EXISTS admins
            (id INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
             nick TEXT NOT NULL,
             sender TEXT,
             pass TEXT NOT NULL)'''
        bot.modules_database.cursor().execute(query)
    
    def run(self, bot, params):
        if is_authorised(bot.modules_database, bot.sender):
            bot.say(bot.sender.split("!")[0],"You already are authorized.")
            return
        username = bot.match.groups()[0]
        password = bot.match.groups()[1].encode(bot.config["encoding"])
        password = hashlib.md5(password).hexdigest()
        query = 'UPDATE admins SET sender=? WHERE nick=? AND pass=?'
        bot.modules_database.cursor().execute(query,
                (bot.sender, username, password))
        if is_authorised(bot.modules_database, bot.sender):
            bot.say(bot.sender.split("!")[0],"Succesfully authorized.")
        else:
            bot.say(bot.sender.split("!")[0],"Unable to authorize.")

class Deauth(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.deauth$"

    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            bot.say(bot.sender.split("!")[0],"You are not authorized.")
            return
        query = 'UPDATE admins SET sender="" WHERE sender=?'
        bot.modules_database.cursor().execute(query, (bot.sender,))
        if bot.modules_database.cursor().rowcount:
            bot.say(bot.sender.split("!")[0],"Succesfully deauthorized.")
        else:
            bot.say(bot.sender.split("!")[0],"Unable to deauthorize.")

class Join(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.join (\#[^ ]+)"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        bot.msg("JOIN %s" % bot.match.groups()[0])
        bot.say(bot.match.groups()[0], "Hello!")
        #bot.say(bot.match.groups()[0], "I have been told to join this channel by %s" % params[0])

class Part(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.part (\#[^ ]+)"
    
    def run(self, bot, params):
        if not is_authorised(bot.sender):
            return
        bot.msg("PART %s" % bot.match.groups(0))

class Nick(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.nick ([^ ]+)"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        bot.conf.nick = bot.match.group(0)
        bot.msg("NICK %s" % bot.match.groups(0))

class Msg(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.msg (\#[^ ]+)[ ]+([^ ].*)"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        bot.say(bot.match.group(1), bot.match.group(2))

class Send(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"\.send[ ]+([^ ].*)"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        bot.msg(bot.match.groups()[0])

class Reload(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.(reload|unload)[ ]+([^ ]+)$"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        mn = bot.match.groups()[1]
        nick = params[0].split("!")[0]
        try:
            bot.unload_module(mn)
        except:
            bot.say(nick, "Unloading of module %s FAILED!" % mn)
            traceback.print_exc()
        else:
            bot.say(nick, "Unloading of module %s SUCCESSFUL!" % mn)
        if bot.match.groups()[0]=='unload':
            return
        try:
            bot.load_module(mn)
        except:
            bot.say(nick, "Reloading of module %s FAILED!" % mn)
            traceback.print_exc()
        else:
            bot.say(nick, "Reloading of module %s SUCCESSFUL!" % mn)

class CoreDump(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r"^\.core_dump$"
    
    def run(self, bot, params):
        if not is_authorised(bot.modules_database, bot.sender):
            return
        for k in bot.modules:
            print(k)
            for m in bot.modules[k]:
                print("\t%s" % m[2])
