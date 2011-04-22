#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from settings import *
from qllbot.Registry import *


registry = Registry()


class QllClient():

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
	
	def channel_message(self, sender, channel, flags, message):
		registry.eventsys.call('channel_message', {'sender': sender, 'channel': channel, 'flags': flags, 'message': message})

	def private_message(self, sender, flags, message):
		registry.eventsys.call('private_message', {'sender': sender, 'channel': '@PM', 'flags': flags, 'message': message})

	def notify_send_channel_message(self, channel, message):
		registry.eventsys.call('send_channel_message', {'sender': USERNAME, 'channel': channel, 'flags': None, 'message': message})
	
	def notify_send_private_message(self, reciever, message):
		registry.eventsys.call('send_private_message', {'sender': USERNAME, 'reciever': reciever, 'flags': None, 'message': message})

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
	
	def notify_users_response(self, channel, users):
		registry.eventsys.call('users_response', {'channel': channel, 'users': users})
	
	def keep_alive(self):
		''' Keeps client alive. If nothing gets sent to the server for about 1 minute, pysilc looses connection. '''
		self.command_call('INFO')

