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

modules_paths = ['~/.scythebot/modules/',]
load_modules = [
        "admin",
        "jiggly",
        "ping",
        "parrot",
        "dice",
        ]
block_modules = []
modules_database_path = '~/.scythebot/modules_data.sqlite3'

log_level = 'DEBUG'
log_file = None
log_format = '%(levelname)s|%(filename)s:%(lineno)s|%(message)s'
log_datefmt = '%H:%M:%S'

cooldown = 5
