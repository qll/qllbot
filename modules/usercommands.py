#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import *
from qllbot.Registry import *
from qllbot.basic_functions import send_message, get_username, get_channelname


registry = Registry()


def create_usercommands_tables():
	registry.db.execute('CREATE TABLE usercommands (user TEXT, channel TEXT, command TEXT, value TEXT)')

def save(param):
	''' Saves a usercommand. Example: #save foo bar. !foo -> bar '''
	if param == '':
		return u'Empty user command.'
	command = param.split(' ', 1)
	if len(command) < 2:
		return u'Empty value for command.'
	
	# check if command already exists (UPDATE), else INSERT
	c = registry.db.cursor()
	c.execute('SELECT user FROM usercommands WHERE command = ? AND channel = ?', (command[0], get_channelname(registry.cmdinterpreter.current_channel)))
	# c.rowcount does not work as expected, so we use this to determine if there already is a usercommand like that
	for row in c:
		c.execute(
			'UPDATE usercommands SET user = ?, value = ? WHERE command = ? AND channel = ?',
			(get_username(registry.cmdinterpreter.current_sender.username), command[1], command[0], get_channelname(registry.cmdinterpreter.current_channel))
		)
		return u'Usercommand updated. Execute with !%s' % command[0]
	
	# new command: INSERT
	registry.db.execute(
		'INSERT INTO usercommands VALUES (?, ?, ?, ?)',
		(get_username(registry.cmdinterpreter.current_sender.username), get_channelname(registry.cmdinterpreter.current_channel), command[0], command[1])
	)
	return u'Usercommand saved. Execute with !%s' % command[0]

def interpret_usercommand(sender, channel, message):
	if message[:1] == USERCOMMANDS_TOKEN:
		command = message[1:].strip()
		c = registry.db.cursor()
		c.execute('SELECT * FROM usercommands WHERE command = ? AND channel = ?', (command, get_channelname(channel)))
		for row in c:
			send_message(channel, row[3])


subscribe('create_tables',   create_usercommands_tables)
subscribe('channel_message', interpret_usercommand)
add_command('save', save)
