#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Channel():
	name = ''

	mode = ''

	topic = ''

	# contains following info: {'username': True/False (is op), ...}
	users = {}

	def __init__(self, name):
		self.name = name
	
	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return u'%s' % self.name

	def add_user(self, username):
		if username.startswith('@'):
			self.users[username[1:]] = True
		else:
			self.users[username] = False

	def remove_user(self, username):
		if username in self.users.keys():
			del self.users[username]
	
	def op(self, username):
		self.users[username] = True
	
	def deop(self, username):
		self.users[username] = False
	
	def is_op(self, username):
		if self.exists(username):
			return self.users[username]
		else:
			return False
	
	def exists(self, username):
		if username in self.users.keys():
			return True
		else:
			return False
