#!/usr/bin/env python
# -*- coding: utf-8 -*-

class IrcUser():
	username = ''
	
	nickname = ''
	
	realname = ''
	
	hostname = ''
	
	server = ''
	
	def __str__(self):
		return self.username

