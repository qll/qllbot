#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from settings import *


class QllClient():
	''' Common functionality between the SILC and the IRC client. '''
	def log_message(self, user, message, channel):
		if isinstance(user, str):
			username = user
		else:
			username = user.username
		print(LOG_MESSAGE_FORMAT % (channel, self.get_current_time(), username, message))

	def log_event(self, message):
		print(LOG_EVENT_FORMAT % (self.get_current_time(), message))

	def get_current_time(self):
		return time.strftime("%H:%M:%S", time.localtime())

	def running(self):
		self.log_event('Running (%s-Mode)' % PROTOCOL)
		self.connect_to_server(SERVER)

	def connected_to_server(self):
		self.log_event('Connected to %s' % SERVER)
		self.log_event('Using %s as nickname' % USERNAME)
		for channel, password in CHANNELS.iteritems():
			self.command_call('JOIN %s %s' % (channel, password)) 

	def connected(self):
		self.connected_to_server()

	def disconnected(self, msg):
		self.log_event('Disconnected: %s' % msg)
		self.log_event('Attempting reconnect')
		self.connect_to_server(SERVER)
	
	def keep_alive(self):
		''' Keeps client alive. If nothing gets sent to the server for about 1 minute, pysilc looses connection. '''
		self.command_call('INFO')

