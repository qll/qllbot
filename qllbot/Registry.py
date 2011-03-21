#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Singleton import Singleton


class Registry(Singleton):
	''' Something like the registry pattern '''
	pass


def add_command(command, function):
	''' Shortcut to registry.cmdinterpreter.add_command() '''
	registry = Registry()
	registry.cmdinterpreter.add_command(command, function)

def subscribe(event, function):
	''' Shortcut to registry.eventsys.subscribe() '''
	registry = Registry()
	registry.eventsys.subscribe(event, function)
