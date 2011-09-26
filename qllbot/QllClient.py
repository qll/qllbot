#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import *
from qllbot.Registry import Registry


registry = Registry()


class QllClient():
	''' Common functionality between the SILC and the IRC client. '''
	def running(self):
		registry.logger.log_event('Running (%s-Mode)' % PROTOCOL)
		self.connect_to_server(SERVER)

	def connected_to_server(self):
		registry.logger.log_event('Connected to %s' % SERVER)
		registry.logger.log_event('Using %s as nickname' % registry.username)
		for channel, password in CHANNELS.iteritems():
			self.command_call('JOIN %s %s' % (channel, password)) 

	def connected(self):
		self.connected_to_server()

	def disconnected(self, msg):
		registry.logger.log_event('Disconnected: %s' % msg)
		registry.eventsys.call('disconnect')
		registry.logger.log_event('Attempting reconnect')
		self.connect_to_server(SERVER)
	
	def keep_alive(self):
		''' Keeps client alive. If nothing gets sent to the server for about 1 minute, pysilc looses connection. '''
		self.command_call('INFO')

