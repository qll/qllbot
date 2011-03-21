#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Registry import Registry
from basic_functions import send_message
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

