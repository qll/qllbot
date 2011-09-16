#!/usr/bin/env python
# -*- coding: utf-8 -*-
import silc
from qllbot.Registry import Registry
from qllbot.QllClient import QllClient


events = Registry().eventsys


class QllSilcClient(QllClient, silc.SilcClient):
	def __init__(self, keys, username, user, realname):
		self.keys     = keys
		self.username = username
		self.user     = user
		self.realname = realname
	
	def run(self):
		''' Starts the client '''
		silc.SilcClient.__init__(self, self.keys, self.username, self.user, self.realname)
	
	def channel_message(self, sender, channel, flags, message):
		events.call('channel_message', sender, channel, message)

	def private_message(self, sender, flags, message):
		events.call('private_message', sender, message)

	def notify_send_channel_message(self, channel, message):
		events.call('send_channel_message', USERNAME, channel, message)
	
	def notify_send_private_message(self, reciever, message):
		events.call('send_private_message', USERNAME, reciever, message)

	def notify_join(self, user, channel):
		events.call('join', user, channel)
	
	def notify_leave(self, user, channel):
		events.call('leave', user, channel)
	
	def notify_invite(self, channel, channel_name, user):
		events.call('invite', user, channel)

	def notify_kicked(self, kicked, message, kicker, channel):
		events.call('kicked', kicker, channel, kicked, message)
