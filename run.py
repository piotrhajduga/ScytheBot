#!/usr/bin/env python3
import logging
import os
import sys
import imp
import traceback
import time
import irc
import bot

logger = logging.getLogger(__name__)

CONF = os.path.expanduser('~/.ircbot/config.py')

if __name__ == '__main__':
    try:
        config = imp.load_source('config', CONF)
    except:
        traceback.print_exc()
        sys.exit()
    while 1:
        ircbot = bot.Bot(config)
        try:
            ircbot.connect()
            ircbot.main_loop()
        except KeyboardInterrupt as exc:
            ircbot.quit()
            sys.exit()
        except irc.LostConnectionException as exc:
            ircbot.close()
            time.sleep(5)
            continue
        except irc.ConnectionFailureException as exc:
            logger.error('Cannot connect to the irc network')
            sys.exit()
        except BaseException as exc:
            traceback.print_exc()
            ircbot.close()
            sys.exit()
