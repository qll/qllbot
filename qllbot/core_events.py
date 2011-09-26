#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Channel import Channel
from basic_functions import *
from settings import *
from Registry import *


registry = Registry()
# contains following mapping: {channelname: Channel object}
registry.channels = {}


def pong(code):
	registry.client.command_call('PONG ' + code)


def log_message(sender, channel, message):
	registry.logger.log_message(sender, message, channel)

def log_private_message(sender, message):
	log_message(sender, '@PM', message)

def log_join_channel(user, channel):
	registry.logger.log_event('User named %s joined channel %s' % (user, channel))

def log_leave_channel(user, channel):
	registry.logger.log_event('User named %s left channel %s' % (user, channel))

def log_kicked(user, channel, kicked, message):
	registry.logger.log_event('User named %s kicked %s from %s (%s)' % (user, kicked, channel, message))

def log_topic(user, channel, topic):
	registry.logger.log_event('%s changed topic to %s in %s' % (user, topic, channel))


def parse_userlist(channel, users):
	''' Parses the whole userlist and saves the channel to registry.channels. '''
	if not channel in registry.channels.keys():
		registry.channels[channel] = Channel(channel)
	for user in users.split(' '):
		registry.channels[channel].add_user(user)

def add_to_userlist(user, channel):
	if channel in registry.channels.keys():
		registry.channels[channel].add_user(get_username(user))

def remove_from_userlist(user, channel):
	if channel in registry.channels.keys():
		if get_username(user) == registry.username:
			# bot left channel
			registry.channels.pop(channel)
		else:
			registry.channels[channel].remove_user(get_username(user))

def kicked_from_userlist(user, channel, kicked, message):
	remove_from_userlist(user, channel)

def check_for_op(user, channel, mode, who):
	if mode.find('+o') != -1:
		registry.channels[channel].op(who)
		if AUTO_OP_OWNER and who == registry.username and not registry.channels[channel].is_op(OWNER):
			registry.client.command_call('MODE %s +o %s' % (channel, OWNER))
	elif mode.find('-o') != -1:
		registry.channels[channel].deop(who)


def interpret_message(sender, channel, message):
	''' Checks for commands in all messages and sends the returned string to the channel. '''
	output = registry.cmdinterpreter.check(message, sender, channel)
	if output != '' and output != None:
		send_message(channel, output)

def join_invited_channel(user, channel):
	''' Joins a channel the bot gets invited to (by his owner) '''
	if get_username(user) == OWNER:
		registry.client.command_call('JOIN %s' % channel)

def modify_nickname():
	''' 
		If a nickname is already in use, change the nickname to something else.
		Here I use a simple algorithm to add a number at the end of the name.
	'''
	registry.logger.log_event('Nickname already taken')
	registry.username += '1'
	registry.client.command_call('NICK %s' % registry.username)
	registry.client.command_call('USER %s %d %d :%s' % (registry.username, 0, 0, REALNAME))
	registry.client.connected_to_server()

def welcome(user, channel):
	''' Sends a welcome message to the channel. '''
	if get_username(user) == registry.username and GREETING != '':
		send_message(channel, GREETING)

def op_owner(user, channel):
	''' Automatically gives a joining owner the +o mode if the bot has sufficient rights. '''
	if get_username(user) == OWNER and registry.channels[channel].is_op(registry.username):
			registry.client.command_call('MODE %s +o %s' % (channel, OWNER))


subscribe('ping', pong)

subscribe('channel_message',      log_message)
subscribe('send_channel_message', log_message)
subscribe('send_private_message', log_message)
subscribe('private_message',      log_private_message)
subscribe('join',                 log_join_channel)
subscribe('leave',                log_leave_channel)
subscribe('kicked',               log_kicked)
subscribe('topic',                log_topic)

subscribe('users_response',  parse_userlist)
subscribe('join',            add_to_userlist)
subscribe('leave',           remove_from_userlist)
subscribe('kicked',          kicked_from_userlist)
subscribe('mode',            check_for_op)

subscribe('channel_message', interpret_message)
subscribe('invite',          join_invited_channel)
subscribe('nickname_in_use', modify_nickname)

if AUTO_OP_OWNER:
	subscribe('join', op_owner)
if GREETING != '':
	subscribe('join', welcome)
