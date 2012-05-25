# -*- coding: utf-8 -*-
password = None
nick = "scythebot"
ident = "scythebot"
name = "scythebot pythonic IRC bot in development"
nickserv_passwd = None
host = "host"
port = 6667
ssl = False
channels = [
        "#channel"
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

log_level = 'INFO'
log_file = None
log_format = '%(asctime)s - %(levelname)s - %(message)s'
