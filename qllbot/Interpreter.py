#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Interpreter():
	commands = {}
	
	commandtoken = '#'
	
	current_sender = None
	
	current_channel = None
	
	def check(self, message, sender, channel):
		self.current_sender  = sender
		self.current_channel = channel
		if message[:1] == self.commandtoken:
			command = message[1:].strip().split(' ', 1)
			if command[0] in self.commands:
				if len(command) > 1:
					# parameters are given
					return self.commands[command[0]](command[1]);
				# no parameters given
				return self.commands[command[0]]('');
		return ''

	def add_command(self, command, function):
		self.commands[command] = function

	def load_modules(self, modules):
		for module in modules:
			__import__('modules.%s' % module)

