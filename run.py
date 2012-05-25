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
        b = bot.Bot(config)
        try:
            b.connect()
            b.main_loop()
        except KeyboardInterrupt as e:
            b.quit()
            sys.exit()
        except irc.ConnectionError as e:
            b.quit()
            time.sleep(5)
            continue
        except:
            traceback.print_exc()
            b.quit()
            sys.exit()
