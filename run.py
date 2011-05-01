import os,sys,imp,traceback,time
import irc,bot

CONF = os.path.expanduser('~/.scythebot/config.py')
if __name__=="__main__":
	try: config = imp.load_source('config',CONF)
	except:
		traceback.print_exc()
		sys.exit()
	b = bot.Bot(config)
	while 1:
		try:
			b.connect()
			b.main_loop()
		except KeyboardInterrupt:
			b.quit()
			sys.exit()
		except irc.ConnectionError:
			b.quit()
			time.sleep(5)
			b = bot.Bot(config)
			b.connect()
			continue
		except:
			traceback.print_exc()
			continue
