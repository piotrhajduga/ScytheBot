# -*- coding: utf-8 -*-
password = None
nick = "scythebot"
ident = "scythebot"
name = "scythebot pythonic IRC bot in development"
nickserv_passwd = None
<<<<<<< HEAD
host = "clanserver4u.de.quakenet.org"
port = 6667
ssl = False
channels = [
        "#test"
        ]
=======
host = "host.com"
port = 6667
ssl = False
channels = [
		"#test"
		]
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac
autorejoin = True
encoding = "utf-8"

import os.path
modules_paths = [
<<<<<<< HEAD
        os.path.expanduser("~/.ircbot/modules/")
        ]
load_modules = [
        "admin",
        "jiggly",
        "ping",
        "parrot",
        "dice"
        ]
=======
		os.path.expanduser("~/.ircbot/modules/")
		]
load_modules = [
		"admin",
		"jiggly",
		"ping",
		"parrot",
		"dice"
		]
>>>>>>> 72f9bbe5365e0d1edec3d6b195b1a19936db43ac
block_modules = []
