#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from qllbot.Registry import *
from qllbot.basic_functions import get_username, send_message
from settings import *


registry = Registry()


def quit(param):
	''' Shuts down the bot. Only possible if you are the owner of the bot! '''
	if OWNER == get_username(registry.cmdinterpreter.current_sender):
		send_message(registry.cmdinterpreter.current_channel, 'Goodbye :)')
		sys.exit()
	else:
		return u'You are not allowed to shut me down D:<'


add_command('quit', quit)
