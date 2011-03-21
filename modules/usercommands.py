#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import *
from qllbot.Registry import *
from qllbot.basic_functions import send_message


registry = Registry()


def create_usercommands_tables(param):
	registry.db.execute('CREATE TABLE usercommands (user TEXT, channel TEXT, command TEXT, value TEXT)')

def save(param):
	''' Saves a usercommand. Example: #save foo bar. !foo -> bar '''
	if param == '':
		return 'Empty user command.'
	command = param.split(' ', 1)
	if len(command) < 2:
		return 'Empty value for command.'
	
	# check if command already exists (UPDATE), else INSERT
	c = registry.db.cursor()
	c.execute('SELECT * FROM usercommands WHERE command = ? AND channel = ?', (command[0].decode('utf-8'), str(registry.cmdinterpreter.current_channel)))
	# c.rowcount does not work as expected, so we use this to determine if there already is a usercommand like that
	for row in c:
		c.execute(
			'UPDATE usercommands SET user = ?, value = ? WHERE command = ? AND channel = ?',
			(str(registry.cmdinterpreter.current_sender.username), command[1].decode('utf-8'), command[0].decode('utf-8'), str(registry.cmdinterpreter.current_channel))
		)
		return
	
	# new command: INSERT
	registry.db.execute(
		'INSERT INTO usercommands VALUES (?, ?, ?, ?)',
		(str(registry.cmdinterpreter.current_sender.username), str(registry.cmdinterpreter.current_channel), command[0].decode('utf-8'), command[1].decode('utf-8'))
	)

def interpret_usercommand(param):
	if param['message'][:1] == USERCOMMANDS_TOKEN:
		command = param['message'][1:].strip()
		c = registry.db.cursor()
		c.execute('SELECT * FROM usercommands WHERE command = ? AND channel = ?', (command.decode('utf-8'), str(param['channel'])))
		for row in c:
			send_message(param['channel'], row[3].encode('utf-8'))


subscribe('create_tables', create_usercommands_tables)
subscribe('channel_message', interpret_usercommand)
add_command('save', save)
