#!/usr/bin/env python3
import os,sys,imp,traceback,time
import irc,bot

CONF = os.path.expanduser('~/.ircbot/config.py')
if __name__=="__main__":
    try: config = imp.load_source('config',CONF)
    except:
        traceback.print_exc()
        sys.exit()
    while 1:
        try:
            b = bot.Bot(config)
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
