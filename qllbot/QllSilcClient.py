#!/usr/bin/env python
# -*- coding: utf-8 -*-
import silc
from qllbot.QllClient import QllClient


class QllSilcClient(QllClient, silc.SilcClient):
	def command_reply_join(self, channel, name, topic, hmac, x, y, users):
		registry.eventsys.call('command_reply_join', {'channel': channel, 'name': name, 'topic': topic, 'hmac': hmac, 'x': x, 'y': y, 'users': users})
		self.log_event('Joined channel %s' % name)
		if GREETING != '':
			self.send_channel_message(channel, GREETING)
			self.log_message(USERNAME, GREETING, channel)

