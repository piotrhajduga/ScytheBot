# -*- coding: utf-8 -*-
password = None
nick = "igglybuff"
ident = "igglybuff"
name = "igglybuff pythonic IRC bot in development"
nickserv_passwd = None
host = "euroserv.fr.quakenet.org"
port = 6667
ssl = False
channels = [
        #"#inf.aei.polsl.pl",
        "#lobos",
		]
autorejoin = True
encoding = "utf-8"

import os.path
modules_paths = [
		os.path.expanduser("modules/")
		]
load_modules = [
		"admin",
		"jiggly",
		"ping",
		"parrot",
		"dice"
		]
block_modules = []

log_level = 'DEBUG'
log_file = None
log_format = '%(levelname)s|%(filename)s:%(lineno)s|%(message)s'
log_datefmt = '%H:%M:%S'
