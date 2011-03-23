#!/usr/bin/env python
# -*- coding: utf-8 -*-
from basic_functions import send_message
from Registry import *
from settings import *


registry = Registry()


def interpret_message(param):
	''' Subscribed to the channel_message event. '''
	output = registry.cmdinterpreter.check(param['message'], param['sender'], param['channel'])
	if output != '' and output != None:
		send_message(param['channel'], output)

def log_message(param):
	''' Subscribed to the channel_message and private_message event. '''
	registry.client.logMessage(param['sender'], param['message'], param['channel'])

def log_join_channel(param):
	registry.client.logEvent('User named %s joined channel %s' % (param['user'].username, param['channel'].channel_name))

def log_leave_channel(param):
	registry.client.logEvent('User named %s left channel %s' % (param['user'].username, param['channel'].channel_name))


subscribe('channel_message', log_message)
subscribe('private_message', log_message)
subscribe('channel_message', interpret_message)
subscribe('notify_join', log_join_channel)
subscribe('notify_leave', log_leave_channel)
