#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time, sqlite3
from qllbot.Registry import Registry
from qllbot.Events import Events
from qllbot.Interpreter import Interpreter
from settings import *


if not os.path.isdir(CACHE):
	os.mkdir(CACHE, 0750)

# initialize important objects
cmdinterpreter = Interpreter()
registry       = Registry()
eventsys       = Events()
if COMMAND_TOKEN != '':
	cmdinterpreter.commandtoken = COMMAND_TOKEN

# initialize database
create_tables = False
if not os.path.isfile(DATABASE_PATH):
	create_tables = True
connection = sqlite3.connect(DATABASE_PATH)

# make globally available
registry.db             = connection
registry.eventsys       = eventsys
registry.cmdinterpreter = cmdinterpreter

# get client
if PROTOCOL == 'SILC':
	import silc
	from qllbot.QllSilcClient import QllSilcClient
	if not os.path.isfile(PUBKEY_PATH) or not os.path.isfile(PRIVKEY_PATH):
		keys = silc.create_key_pair(PUBKEY_PATH, PRIVKEY_PATH, passphrase = PASSWORD)
	else:
		keys = silc.load_key_pair(PUBKEY_PATH, PRIVKEY_PATH, passphrase = PASSWORD)
	client = QllSilcClient(keys, USERNAME, USERNAME, REALNAME)
elif PROTOCOL == 'IRC':
	from qllbot.QllIrcClient import QllIrcClient
	client = QllIrcClient()
else:
	print('Error: Unknown protocol (SILC or IRC possible).')
	sys.exit(1)
registry.client = client

# import core events (logging, interpreter) and load modules
import qllbot.core_events
cmdinterpreter.load_modules(MODULES)

# write database tables and initial data (if needed)
if create_tables:
	eventsys.call('create_tables', {})
	eventsys.call('insert_into_created_tables', {})

try:
	client.run()
	timer = 0
	while True:
		client.run_one()
		time.sleep(0.2)
		
		if SEND_KEEP_ALIVE:
			timer += 1
			# 20 seconds
			if timer >= 100:
				timer = 0
				client.keep_alive()
except KeyboardInterrupt:
	sys.exit()
finally:
	connection.commit()
	connection.close()

