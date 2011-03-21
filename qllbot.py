#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import sqlite3
import silc
from qllbot.Registry import Registry
from qllbot.Events import Events
from qllbot.Interpreter import Interpreter
from qllbot.QllSilcClient import QllSilcClient
from qllbot.core_events import *
from settings import *


class QllBot(QllSilcClient):
	def channel_message(self, sender, channel, flags, message):
		eventsys.call('channel_message', {'sender': sender, 'channel': channel, 'flags': flags, 'message': message})

	def private_message(self, sender, flags, message):
		eventsys.call('private_message', {'sender': sender, 'channel': '@PM', 'flags': flags, 'message': message})

	def running(self):
		client.connect_to_server('silcnet.org')
		self.logEvent('Running')

	def connected(self):
		self.logEvent('Connected')
		self.command_call('JOIN %s %s' % (CHANNEL, CHANNEL_PASSWORD))

	def disconnected(self, msg):
		self.logEvent('Disconnected: %s' % msg)

	def command_reply_join(self, channel, name, topic, hmac, x, y, users):
		eventsys.call('command_reply_join', {'channel': channel, 'name': name, 'topic': topic, 'hmac': hmac, 'x': x, 'y': y, 'users': users})
		self.logEvent('Joined channel %s' % name)
		if GREETING != '':
			self.send_channel_message(channel, GREETING)
			self.logMessage(USERNAME, GREETING, channel)

	def notify_join(self, user, channel):
		eventsys.call('notify_join', {'channel': channel, 'user': user})
		self.logEvent('User named %s joined channel %s' % (user.username, channel.channel_name))
	
	def keep_alive(self):
		self.command_call('INFO')
		#self.logEvent('Keep alive ping')


if __name__ == '__main__':
	if not os.path.isfile(PUBKEY_PATH) or not os.path.isfile(PRIVKEY_PATH):
		keys = silc.create_key_pair(PUBKEY_PATH, PRIVKEY_PATH, passphrase = PASSWORD)
	else:
		keys = silc.load_key_pair(PUBKEY_PATH, PRIVKEY_PATH, passphrase = PASSWORD)

	# initialize important objects
	client         = QllBot(keys, USERNAME, USERNAME, USERNAME)
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
	registry.client         = client
	registry.eventsys       = eventsys
	registry.cmdinterpreter = cmdinterpreter
	
	# set up modules and subscribe to basic events
	cmdinterpreter.load_modules(MODULES)
	eventsys.subscribe('channel_message', log_message)
	eventsys.subscribe('private_message', log_message)
	eventsys.subscribe('channel_message', interpret_message)

	# write database tables and initial data (if needed)
	if create_tables:
		eventsys.call('create_tables', {})
		eventsys.call('insert_into_created_tables', {})

	timer = 0

	while True:
		try:
			client.run_one()
			time.sleep(0.2)
			timer += 1
			# 20 seconds
			if timer >= 100:
				timer = 0
				client.keep_alive()
		except KeyboardInterrupt:
			break
	
	connection.commit()
	connection.close()
