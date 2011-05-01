import os,sys,imp,traceback,time
import irc

CONF = os.path.expanduser('~/.scythebot/config.py')
if __name__=="__main__":
	try: config = imp.load_source('config',CONF)
	except:
		traceback.print_exc()
		sys.exit()
	c = config
	c.nick = "igglybuff"
	c.name = "igglybuff IRC bot"
	c.ident = "igglybuff"
	bot = irc.IRC(c.nick, c.ident, c.name, c.host, c.port, c.ssl, c.password, c.encoding)
	while 1:
		try:
			bot.connect()
			bot.main_loop()
		except KeyboardInterrupt:
			bot.quit()
			sys.exit()
		except irc.ConnectionError:
			bot.quit()
			time.sleep(5)
			bot = irc.IRC(c.nick, c.ident, c.name, c.host, c.port, c.ssl, c.password, c.encoding)
			bot.connect()
			continue
		except:
			traceback.print_exc()
			continue
