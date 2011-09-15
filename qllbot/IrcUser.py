#!/usr/bin/env python
# -*- coding: utf-8 -*-

class IrcUser():
	''' This class exists to stay close to the SILC implementation which uses SilcUser objects. '''
	username = ''

	nickname = ''
	
	realname = ''
	
	hostname = ''
	
	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		return u'%s' % self.username

