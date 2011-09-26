#!/usr/bin/env python
# -*- coding: utf-8 -*-
from time import time, localtime
from copy import deepcopy
from settings import *
from qllbot.Registry import *
from qllbot.basic_functions import get_username, get_channelname, send_private_message


registry = Registry()

# intializing global var (stores online users)
# layout: 
# {username: {channelname: time_joined}, ...}
registry.history_seen = {}


def create_seen_tables():
	registry.db.execute('CREATE TABLE seen (user TEXT, channel TEXT, time INTEGER)')

def seen_joined_channel(channel, users):
	''' Gets USER command replys and checks for new users '''
	for user in users.split(' '):
		add_to_seen(user, channel)

def seen_write_changes():
	''' Writes changes to the database (when the bot quits). '''
	iterator = deepcopy(registry.history_seen)
	for user, channels in iterator.iteritems():
		for channel in channels:
			remove_from_seen(user, channel)

def add_to_seen(user, channel):
	''' Adds a user to the global seen dictionary '''
	user = get_username(user)
	
	# remove op status from nicknames
	if user.startswith('@'):
		user = user[1:]
	
	if not user in registry.history_seen.keys():
		registry.history_seen[user] = {channel: time()}
	else:
		if not channel in registry.history_seen[user].keys():
			registry.history_seen[user][channel] = time()

def remove_from_seen(user, channel):
	''' Removes an user from registry.history_seen and writes him/her to the database. '''
	user = get_username(user)
	
	if user in registry.history_seen.keys():
		if not channel in registry.history_seen[user].keys():
			# something went wrong :O
			return
		
		registry.history_seen[user].pop(channel)
		if len(registry.history_seen[user]) != 0 or user == registry.username:
			# user just left one channel the bot resides in
			return
		
		c = registry.db.cursor()
		c.execute('SELECT time FROM seen WHERE user = ?', (user,))
		if c.fetchone() == None:
			c.execute('INSERT INTO seen VALUES (?, ?, ?)', (user, channel, time()))
		else:
			c.execute(
				'UPDATE seen SET channel = ?, time = ? WHERE user = ?',
				(channel, time(), user)
			)
		registry.history_seen.pop(user)

def kicked_from_seen(user, channel, kicker, message):
	remove_from_seen(user, channel)

def left_server(user, message):
	iterator = deepcopy(registry.history_seen)
	for channel, timestamp in iterator[get_username(user)].iteritems():
		remove_from_seen(user, channel)

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
		diff = time() - row[0]
		if diff <= 3600:
			minutes = round(diff / 60)
			if minutes == 0:
				ftime = '%d seconds ago' % (round(diff))
			elif minutes == 1:
				ftime = '%d minute ago' % (minutes)
			else:
				ftime = '%d minutes ago' % (minutes)
		else:
			ftime  = time.strftime('%H:%M on %d.%m.%Y', localtime(row[0]))
		return 'I have seen %s %s in %s.' % (param, ftime, row[1])
	else:
		return 'I have never seen this nickname.'


subscribe('create_tables',  create_seen_tables)
subscribe('join_users',     seen_joined_channel)
subscribe('pre_exit',       seen_write_changes)
subscribe('join',           add_to_seen)
subscribe('leave',          remove_from_seen)
subscribe('kicked',         kicked_from_seen)
subscribe('quit',           left_server)

add_command('seen', seen)
