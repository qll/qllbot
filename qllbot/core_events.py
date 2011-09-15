#!/usr/bin/env python
# -*- coding: utf-8 -*-
from basic_functions import send_message, get_channelname, get_username
from settings import *
from Registry import *


registry = Registry()
registry.channels = {}


def interpret_message(sender, channel, message):
	''' Checks for commands in all messages and prints out the returned string. '''
	output = registry.cmdinterpreter.check(message, sender, channel)
	if output != '' and output != None:
		send_message(channel, output)

def log_message(sender, channel, message):
	''' Logs all messages in channels the bot resides in to the console. '''
	registry.client.log_message(sender, message, channel)

def log_private_message(sender, message):
	''' Logs private messages. '''
	log_message(sender, '@PM', message)

def welcome(user, channel):
	''' Sends a welcome message to the channel. '''
	if get_username(user) == USERNAME and GREETING != '':
		send_message(channel, GREETING)

def log_join_channel(user, channel):
	''' Prints a text to console when a user joins a channel the bot resides in. '''
	registry.client.log_event('User named %s joined channel %s' % (user, channel))

def log_leave_channel(user, channel):
	''' Prints a text to console when a user leaves a channel the bot resides in. '''
	registry.client.log_event('User named %s left channel %s' % (user, channel))

def join_invited_channel(user, channel):
	''' Joins a channel the bot gets invited to (by his owner) '''
	if get_username(user) == OWNER:
		registry.client.command_call('JOIN %s' % channel)	

def get_op_from_userlist(channel, users):
	''' Verifies if the bot has op status '''
	op = False
	for user in users:
		if user == '@' + USERNAME:
			op = True
	registry.channels[channel] = op

def get_op_mode(user, channel, mode, who):
	''' Reacts if the bot gets or looses op status in a channel '''
	if USERNAME == who:
		if mode == '+o':
			registry.channels[channel] = True
		elif mode == '-o':
			registry.channels[channel] = False


subscribe('channel_message', log_message)
subscribe('private_message', log_private_message)
subscribe('channel_message', interpret_message)
subscribe('join', log_join_channel)
subscribe('leave', log_leave_channel)
subscribe('invite', join_invited_channel)
subscribe('users_response', get_op_from_userlist)
subscribe('mode', get_op_mode)

if GREETING != '':
	subscribe('join', welcome)
