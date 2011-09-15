#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Singleton import Singleton

class Events(Singleton):
	events = {}
	
	def subscribe(self, event, function):
		if event in self.events:
			self.events[event].append(function)
		else:
			self.events[event] = [function,]
	
	def call(self, event, *param):
		if event in self.events:
			for function in self.events[event]:
				function(*param)
