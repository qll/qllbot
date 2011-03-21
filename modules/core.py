#!/usr/bin/env python
# -*- coding: utf-8 -*-
from settings import *
from qllbot.Registry import *


registry = Registry()


def get_version(param):
	''' Returns the version qllbot currently runs on. '''
	return 'qllbot Version %s' % VERSION

def get_loaded_commands(param):
	''' Returns all loaded commands. '''
	output = 'Loaded commands:\n'
	return output + ', '.join(registry.cmdinterpreter.commands)

def get_help(param):
	''' Prints out the documentation string for a given command (e.g. #help help -> this text). '''
	if param == '':
		return 'Type in #commands for a list of commands or #help [command] for help concerning a command.'
	if param in registry.cmdinterpreter.commands:	
		return '#%s: %s' % (param, registry.cmdinterpreter.commands[param].__doc__)
	return 'Command not found.'


add_command('version', get_version)
add_command('commands', get_loaded_commands)
add_command('help', get_help)
