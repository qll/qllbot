"""
Contains functions that wrap some of Python's logging module functionalities.

This module requires you to set up the logging module manually or with the
set_up_logging function.
"""
import logging
import time
from settings import *


def set_up_logging():
	""" 
	Sets up Python's logging module. We will handle timestamps and stuff
	manually and we just want logging for its thread-safety and easy usage.
	"""
	cfg = {'level': logging.DEBUG, 'format': '%(message)s'}
	if LOG_TO_FILE:
		cfg['filename'] = LOG_FILE
	logging.basicConfig(**cfg)


def message(nickname, channel, message):
	""" Logs IRC chat messages. """
	if LOG_MESSAGES == 1 or (LOG_MESSAGES == 2 and not LOG_TO_FILE):
		logging.info(
			LOG_MSG_FMT.format(
				nick    = nickname,
				channel = channel,
				message = message,
				time    = time.strftime(LOG_TIME_FMT)
			)
		)


def event(description):
	""" Logs IRC events, like join, leave, invite and so on. """
	if LOG_EVENTS == 1 or (LOG_EVENTS == 2 and not LOG_TO_FILE):
		logging.info(
			LOG_EVNT_FMT.format(
				event = description,
				time  = time.strftime(LOG_TIME_FMT)
			)
		)


def system(description):
	""" Logs system events, like connect, disconnect and so on. """
	if LOG_SYSTEM == 1 or (LOG_SYSTEM == 2 and not LOG_TO_FILE):
		logging.warning(
			LOG_SSTM_FMT.format(
				event = description,
				time  = time.strftime(LOG_TIME_FMT)
			)
		)


def debug(message):
	""" Logs debug messages. """
	if DEBUG:
		logging.debug(message)


def exception(description):
	""" Only wraps logging.exception to prevent unnecessary imports in other modules. """
	logging.exception(description)

