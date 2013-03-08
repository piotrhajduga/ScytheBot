# -*- coding: utf-8 -*-
password = None
nick = "scythebot"
ident = "scythebot"
name = "scythebot pythonic IRC bot in development"
nickserv_passwd = None
host = "euroserv.fr.quakenet.org"
port = 6667
ssl = False
channels = [
    "#lobos",
]
autorejoin = True
encoding = "utf-8"

modules_paths = ['modules/']
load_modules = [
    "admin",
    "jiggly",
    "ping",
    "parrot",
    "dice",
]
block_modules = []
modules_database_path = 'modules_data.sqlite3'

log_level = 'DEBUG'
log_file = None
log_format = '%(levelname)s|%(filename)s:%(lineno)s|%(message)s'
log_datefmt = None

cooldown = 5
