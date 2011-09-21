#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time
from settings import *
from qllbot.Registry import *
from qllbot.Logger import Logger
from qllbot.basic_functions import get_username, get_channelname


db = Registry().db


class DbLogger(Logger):
	def log_message(self, user, message, channel):
		db.execute(
			'INSERT INTO log VALUES (?, ?, ?, ?, 0)',
			(get_username(user), get_channelname(channel), time(), message)
		)

		if DB_LOGGER_CONSOLE:
			print(LOG_MESSAGE_FORMAT % {
				'channel':  channel,
				'time':     self.get_current_time(),
				'username': get_username(user),
				'message':  message
			})

	def log_event(self, message):
		db.execute(
			'INSERT INTO log VALUES (?, ?, ?, ?, 1)',
			('', '', time(), message)
		)
		
		if DB_LOGGER_CONSOLE:
			print(LOG_EVENT_FORMAT % {
				'time':    self.get_current_time(),
				'event':   message
			})


def create_log_tables():
	db.execute('CREATE TABLE log (user TEXT, channel TEXT, time INTEGER, message TEXT, event INTEGER)')


subscribe('create_tables', create_log_tables)
