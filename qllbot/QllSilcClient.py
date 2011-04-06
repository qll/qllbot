#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import silc
from settings import *
from qllbot.Registry import *


registry = Registry()


class QllSilcClient(silc.SilcClient):
	def logMessage(self, user, message, channel):
		if isinstance(user, str):
			username = user
		else:
			username = user.username
		print LOG_MESSAGE_FORMAT % (channel, self.getCurrentTime(), username, message)

	def logEvent(self, message):
		print LOG_EVENT_FORMAT % (self.getCurrentTime(), message)

	def getCurrentTime(self):
		return time.strftime("%H:%M:%S", time.localtime())
	
	def channel_message(self, sender, channel, flags, message):
		registry.eventsys.call('channel_message', {'sender': sender, 'channel': channel, 'flags': flags, 'message': message})

	def private_message(self, sender, flags, message):
		registry.eventsys.call('private_message', {'sender': sender, 'channel': '@PM', 'flags': flags, 'message': message})

	def running(self):
		self.connect_to_server(SERVER)
		self.logEvent('Running')

	def connected(self):
		self.logEvent('Connected to %s' % SERVER)
		self.command_call('JOIN %s %s' % (CHANNEL, CHANNEL_PASSWORD))

	def disconnected(self, msg):
		self.logEvent('Disconnected: %s' % msg)
		self.logEvent('Attempting reconnect')
		self.connect_to_server(SERVER)

	def command_reply_join(self, channel, name, topic, hmac, x, y, users):
		registry.eventsys.call('command_reply_join', {'channel': channel, 'name': name, 'topic': topic, 'hmac': hmac, 'x': x, 'y': y, 'users': users})
		self.logEvent('Joined channel %s' % name)
		if GREETING != '':
			self.send_channel_message(channel, GREETING)
			self.logMessage(USERNAME, GREETING, channel)

	def notify_join(self, user, channel):
		registry.eventsys.call('join', {'channel': channel, 'user': user})
	
	def notify_leave(self, user, channel):
		registry.eventsys.call('leave', {'channel': channel, 'user': user})
	
	def notify_signoff(self, user, message):
		registry.eventsys.call('signoff', {'user': user, 'message': message})
	
	def notify_topic_set(self, ptype, user, channel, topic):
		registry.eventsys.call('topic_set', {'type': ptype, 'user': user, 'channel': channel, 'topic': topic})
	
	def notify_invite(self, channel, channel_name, user):
		registry.eventsys.call('invite', {'channel': channel, 'channel_name': channel_name, 'user': user})
	
	def notify_nick_change(self, old_user, new_user):
		registry.eventsys.call('nick_change', {'old_user': old_user, 'new_user': new_user})
	
	def notify_kicked(self, kicked, message, kicker, channel):
		registry.eventsys.call('kicked', {'kicked': kicked, 'message': message, 'kicker': kicker, 'channel': channel})
	
	def notify_motd(self, message):
		registry.eventsys.call('motd', {'message': message})
	
	def notify_server_signoff(self):
		registry.eventsys.call('server_signoff', {})
	
	def keep_alive(self):
		''' Keeps client alive. If nothing gets sent to the server for about 1 minute, pysilc looses connection. '''
		self.command_call('INFO')

