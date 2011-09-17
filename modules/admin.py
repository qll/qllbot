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

def op_owner(user, channel):
	''' Automatically gives a joining owner the +o mode if the bot has sufficient rights. '''
	if get_username(user) == OWNER and registry.channels[channel].is_op(registry.username):
			registry.client.command_call('MODE %s +o %s' % (channel, OWNER))


add_command('quit', quit)
if AUTO_OP_OWNER:
	subscribe('join', op_owner)

