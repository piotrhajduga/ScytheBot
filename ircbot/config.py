# -*- coding: utf-8 -*-
password = None
nick = "scythebot"
ident = "scythebot"
name = "scythebot pythonic IRC bot in development"
nickserv_passwd = None
host = "clanserver4u.de.quakenet.org"
port = 6667
ssl = False
channels = [
		"#test"
		]
autorejoin = True
encoding = "utf-8"

import os.path
modules_paths = [
		os.path.expanduser("~/.ircbot/modules/")
		]
load_modules = [
		"admin",
		"jiggly",
		"ping",
		"parrot",
		"dice"
		]
block_modules = []
