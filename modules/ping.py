__module_class_names__ = ["Hello", "Interjection", "Ahello"]

from bot import Module
import random


def hello():
    greetings = (
        #'jiiigglypuffff...',
        #'jiggly!',
        #'JIGGLYPUFF!',
        #'JiGgLyPuFfIiIii',
        'Hey! Hi! Hello!',
        'Have a nice day!',
    )
    return random.choice(greetings)


class Hello(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i)\b(hi|hello|hey|siemk?a|cze[sś][ćc]|pozdr[a-zA-Z]+|y[o0]) +(?:%s|jiggly).*' % bot.config["nick"]

    def run(self, bot, params):
        bot.say(bot.target, hello())


class Interjection(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i)(%s[:,] *)?(%s|jiggly)(!+).*' % (bot.config["nick"], bot.config["nick"])

    def run(self, bot, params):
        bot.say(bot.target, hello())


class Ahello(Module):
    def __init__(self, bot, config):
        Module.__init__(self, bot, config)
        self.handler_type = "privmsg"
        self.rule = r'(?i)\b%s[:,] *(hey|hi|hello|siemk?a|cze[sś][cć]|pozdr|y[o0]).*' % bot.config["nick"]

    def run(self, bot, params):
        bot.say(bot.target, hello())
