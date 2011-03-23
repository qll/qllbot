#!/usr/bin/env python
# -*- coding: utf-8 -*-
from basic_functions import send_message
from Registry import *


registry = Registry()


def interpret_message(param):
	''' Checks for commands in all messages and prints out the returned string. '''
	output = registry.cmdinterpreter.check(param['message'], param['sender'], param['channel'])
	if output != '' and output != None:
		send_message(param['channel'], output)

def log_message(param):
	''' Logs all messages in channels the bot joined and per private message to console. '''
	registry.client.logMessage(param['sender'], param['message'], param['channel'])

def log_join_channel(param):
	''' Prints a text to console when a user joins a channel the bot resides in. '''
	registry.client.logEvent('User named %s joined channel %s' % (param['user'].username, param['channel'].channel_name))

def log_leave_channel(param):
	''' Prints a text to console when a user leaves a channel the bot resides in. '''
	registry.client.logEvent('User named %s left channel %s' % (param['user'].username, param['channel'].channel_name))


subscribe('channel_message', log_message)
subscribe('private_message', log_message)
subscribe('channel_message', interpret_message)
subscribe('notify_join', log_join_channel)
subscribe('notify_leave', log_leave_channel)
