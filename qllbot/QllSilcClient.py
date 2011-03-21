#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import silc
from settings import *

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

