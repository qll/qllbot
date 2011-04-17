#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from settings import *
from qllbot.Registry import *
from qllbot.basic_functions import get_username, get_channelname


registry = Registry()

# intializing global var (stores online users)
registry.history_seen = {}


def create_seen_tables(param):
	registry.db.execute('CREATE TABLE seen (user TEXT, channel TEXT, time INTEGER)')

def seen_joined_channel(param):
	''' Gets USER command replys and checks for new users '''
	for user in param['users']:
		add_to_seen({'user': user, 'channel': param['channel']})

def seen_write_changes(param):
	''' Writes changes to the database (when the bot quits). '''
	iterator = registry.history_seen.copy()
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
		registry.history_seen[user] = [channel]
	else:
		if not channel in registry.history_seen[user]:
			registry.history_seen[user].append(channel)

def remove_from_seen(param):
	''' Removes an user from registry.history_seen and writes him/her to the database. '''
	# todo: write leave event for irc
	user    = get_username(param['user'])
	channel = get_channelname(param['channel'])
	
	# the bot should not write itsself into the database
	if user != USERNAME and user in registry.history_seen.keys():
		if not channel in registry.history_seen[user]:
			# something went wrong :O
			return
		
		registry.history_seen[user].remove(channel)
		if len(registry.history_seen[user]) != 0:
			# user just left one channel the bot resides in
			return
		
		c = registry.db.cursor()
		c.execute('SELECT time FROM seen WHERE user = ?', (user,))
		user_exists = False
		for row in c:
			user_exists = True
		if not user_exists:
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
		return 'User currently online (%s).' % (', '.join(registry.history_seen[param]))
	
	result = 'Never seen this nickname.'
	c = registry.db.cursor()
	c.execute('SELECT time, channel FROM seen WHERE user = ?', (param,))
	for row in c:
		diff = time.time() - row[0]
		if diff <= 3600:
			minutes = round(diff / 60)
			if minutes == 0:
				ftime = 'just left %d seconds ago' % (round(diff))
			elif minutes == 1:
				ftime = 'was seen %d minute ago' % (minutes)
			else:
				ftime = 'was seen %d minutes ago' % (minutes)
		else:
			ftime  = time.strftime('%H:%M on %d.%m.%Y', time.localtime(row[0]))
		result = '%s %s in %s.' % (param, ftime, row[1])
	return result
	

subscribe('create_tables', create_seen_tables)
subscribe('users_response', seen_joined_channel)
subscribe('pre_exit', seen_write_changes)
subscribe('join', add_to_seen)
subscribe('leave', remove_from_seen)
add_command('seen', seen)
