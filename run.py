#!/usr/bin/env python3
import os,sys,imp,traceback,time
import irc,bot

<<<<<<< HEAD
CONF = os.path.expanduser('~/.ircbot/config.py')
=======
CONF = os.path.expanduser('~/ircbot/config.py')
>>>>>>> a18a08a889d0e64c664daa9f83b81e9e6f2afcfa
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
