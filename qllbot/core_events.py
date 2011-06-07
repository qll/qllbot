#!/usr/bin/env python
# -*- coding: utf-8 -*-
from basic_functions import send_message, get_channelname
from settings import *
from Registry import *


registry = Registry()
registry.channels = {}


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

def get_op_from_userlist(param):
	''' Verifies if the bot has op status '''
	channel = get_channelname(param['channel'])
	op      = False
	for user in param['users']:
		if user == '@' + USERNAME:
			op = True
	registry.channels[channel] = op

def get_op_mode(param):
	''' Reacts if the bot gets or looses op status in a channel '''
	channel = get_channelname(param['channel'])
	if param['mode'] == '+o':
		registry.channels[channel] = True
	elif param['mode'] == '-o':
		registry.channels[channel] = False


subscribe('channel_message', log_message)
subscribe('private_message', log_message)
subscribe('channel_message', interpret_message)
subscribe('join', log_join_channel)
subscribe('leave', log_leave_channel)
subscribe('invite', join_invited_channel)
subscribe('users_response', get_op_from_userlist)
subscribe('mode', get_op_mode)

if GREETING != '':
	subscribe('join', welcome)
