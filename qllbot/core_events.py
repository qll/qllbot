#!/usr/bin/env python
# -*- coding: utf-8 -*-
from basic_functions import send_message
from settings import *
from Registry import *


registry = Registry()


def interpret_message(param):
	''' Checks for commands in all messages and prints out the returned string. '''
	output = registry.cmdinterpreter.check(param['message'], param['sender'], param['channel'])
	if output != '' and output != None:
		send_message(param['channel'], output)

def log_message(param):
	''' Logs all messages in channels the bot joined and per private message to console. '''
	registry.client.log_message(param['sender'], param['message'], param['channel'])

def welcome(param):
	if param['user'].username == USERNAME and GREETING != '':
		send_message(param['channel'], GREETING)

def log_join_channel(param):
	''' Prints a text to console when a user joins a channel the bot resides in. '''
	registry.client.log_event('User named %s joined channel %s' % (param['user'].username, param['channel']))

def log_leave_channel(param):
	''' Prints a text to console when a user leaves a channel the bot resides in. '''
	registry.client.log_event('User named %s left channel %s' % (param['user'].username, param['channel']))

def join_invited_channel(param):
	''' Joins a channel the bot gets invited to (by his owner) '''
	if param['user'].username == OWNER:
		registry.client.command_call('JOIN %s' % param['channel_name'])	


subscribe('channel_message', log_message)
subscribe('private_message', log_message)
subscribe('channel_message', interpret_message)
subscribe('join', log_join_channel)
subscribe('leave', log_leave_channel)
subscribe('invite', join_invited_channel)

if GREETING != '':
	subscribe('join', welcome)
