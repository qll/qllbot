#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import *
from qllbot.Logger          import Logger
from qllbot.basic_functions import get_username

class ConsoleLogger(Logger):
	def log_message(self, user, message, channel):
		print(LOG_MESSAGE_FORMAT % {
			'channel':  channel,
			'time':     self.get_current_time(),
			'username': get_username(user),
			'message':  message
		})

	def log_event(self, message):
		print(LOG_EVENT_FORMAT % {
			'time':    self.get_current_time(),
			'event':   message
		})

