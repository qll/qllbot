#!/usr/bin/env python
# -*- coding: utf-8 -*-
import silc
from qllbot.QllClient import QllClient


class QllSilcClient(QllClient, silc.SilcClient):
	def __init__(self, keys, username, user, realname):
		self.keys     = keys
		self.username = username
		self.user     = user
		self.realname = realname
	
	def run(self):
		''' Starts the client '''
		silc.SilcClient.__init__(self, self.keys, self.username, self.user, self.realname)
