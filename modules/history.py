#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from settings import *
from copy import deepcopy
from qllbot.Registry import *
from qllbot.basic_functions import get_username, get_channelname, send_private_message


registry = Registry()

# intializing global var (stores online users)
# layout: 
# {username: {channelname: time_joined}, ...}
registry.history_seen = {}


def create_seen_tables(param):
	registry.db.execute('CREATE TABLE seen (user TEXT, channel TEXT, time INTEGER)')

def seen_joined_channel(param):
	''' Gets USER command replys and checks for new users '''
	for user in param['users']:
		add_to_seen({'user': user, 'channel': param['channel']})

def seen_write_changes(param):
	''' Writes changes to the database (when the bot quits). '''
	iterator = deepcopy(registry.history_seen)
	for user, channels in iterator.iteritems():
		for channel in channels:
			remove_from_seen({'user': user, 'channel': channel})

def add_to_seen(param):
	''' Adds a user to the global seen dictionary '''
	user    = get_username(param['user'])
	channel = get_channelname(param['channel'])
	
	# remove op status from nicknames
	if user.startswith('@'):
		user = user[1:]
	
	# store into dictionary
	if not user in registry.history_seen:
		registry.history_seen[user] = {channel: time.time()}
	else:
		if not channel in registry.history_seen[user].keys():
			registry.history_seen[user][channel] = time.time()

def remove_from_seen(param):
	''' Removes an user from registry.history_seen and writes him/her to the database. '''
	# todo: write leave event for irc
	user    = get_username(param['user'])
	channel = get_channelname(param['channel'])
	
	# the bot should not write itsself into the database
	if user != USERNAME and user in registry.history_seen.keys():
		if not channel in registry.history_seen[user].keys():
			# something went wrong :O
			return
		
		registry.history_seen[user].pop(channel)
		if len(registry.history_seen[user]) != 0:
			# user just left one channel the bot resides in
			return
		
		c = registry.db.cursor()
		c.execute('SELECT time FROM seen WHERE user = ?', (user,))
		if c.fetchone() == None:
			c.execute('INSERT INTO seen VALUES (?, ?, ?)', (user, channel, time.time()))
		else:
			c.execute(
				'UPDATE seen SET channel = ?, time = ? WHERE user = ?',
				(channel, time.time(), user)
			)
		registry.history_seen.pop(user)

def seen(param):
	''' Returns the last time a user was seen online (by this bot). '''
	if param == '':
		return 'This command just makes sense in combination with a username (e.g. #seen qllbot).'
	
	if param in registry.history_seen:
		return 'User currently online (%s).' % (', '.join(registry.history_seen[param].keys()))
	
	c = registry.db.cursor()
	c.execute('SELECT time, channel FROM seen WHERE user = ?', (param,))
	row = c.fetchone()
	if row != None:
		diff = time.time() - row[0]
		if diff <= 3600:
			minutes = round(diff / 60)
			if minutes == 0:
				ftime = '%d seconds ago' % (round(diff))
			elif minutes == 1:
				ftime = '%d minute ago' % (minutes)
			else:
				ftime = '%d minutes ago' % (minutes)
		else:
			ftime  = time.strftime('%H:%M on %d.%m.%Y', time.localtime(row[0]))
		return 'I have seen %s %s in %s.' % (param, ftime, row[1])
	else:
		return 'I have never seen this nickname.'

def create_history_tables(param):
	registry.db.execute('CREATE TABLE history (user TEXT, channel TEXT, time INTEGER, message TEXT, event INTEGER)')

def add_history_message(param):
	registry.db.execute(
		'INSERT INTO history VALUES (?, ?, ?, ?, 0)',
		(get_username(param['sender']), get_channelname(param['channel']), time.time(), param['message'])
	)

def add_history_event(user, channel, message):
	registry.db.execute(
		'INSERT INTO history VALUES (?, ?, ?, ?, 1)',
		(get_username(user), get_channelname(channel), time.time(), message)
	)

def add_history_event_join(param):
	add_history_event(param['user'], param['channel'], 'joined the channel')

def add_history_event_leave(param):
	add_history_event(param['user'], param['channel'], 'left the channel')

def get_history(param):
	''' Sends a private message to you with all messages written while you were offline. '''
	user    = get_username(registry.cmdinterpreter.current_sender)
	channel = get_channelname(registry.cmdinterpreter.current_channel)

	c = registry.db.cursor()
	c.execute(
		'SELECT time FROM seen WHERE user = ? AND channel = ?',
		(user, channel)
	)
	
	if c != None:
		tfrom = c.fetchone()[0]
	
		c.execute(
			'SELECT * FROM history WHERE time > ? AND time < ? ORDER BY time ASC',
			(tfrom, registry.history_seen[user][channel])
		)
		result = ''
		for row in c:
			ftime  = time.strftime('%H:%M:%S', time.localtime(row[2]))
			if row[4] != 1:
				# normal message
				result += '(%s) %s: %s\n' % (ftime, row[0], row[3])
			else:
				# event
				result += '* (%s) %s %s\n' % (ftime, row[0], row[3])
		send_private_message(registry.cmdinterpreter.current_sender, result[:-1])


subscribe('create_tables', create_seen_tables)
subscribe('users_response', seen_joined_channel)
subscribe('pre_exit', seen_write_changes)
subscribe('join', add_to_seen)
subscribe('leave', remove_from_seen)
add_command('seen', seen)

subscribe('create_tables', create_history_tables)
subscribe('channel_message', add_history_message)
subscribe('send_channel_message', add_history_message)
subscribe('join', add_history_event_join)
subscribe('leave', add_history_event_leave)
add_command('history', get_history)
