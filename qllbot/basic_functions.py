#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib2
from Registry import Registry
from settings import *


registry = Registry()


def strip_tags(string):
	''' Strips tags from a string. Should not be used unless absolutely required. '''
	return re.sub(r'<[^>]*?>', '', string)

def get_username(obj):
	''' Makes sure the user is a string and not a SilcUser or IrcUser object '''
	if not isinstance(obj, basestring):
		return obj.username
	else:
		return obj

def get_channelname(obj):
	''' Makes sure the channel name is a string and not a SilcChannel object '''
	if not isinstance(obj, basestring):
		return obj.channel_name
	else:
		return obj

def send_message(channel, message, delay = False):
	''' Sends a message to a channel. '''
	registry.client.send_channel_message(channel, message, delay)
	registry.client.log_message(USERNAME, message, channel)

def send_private_message(user, message, delay = False):
	''' Sends a message to an user. '''
	registry.client.send_private_message(user, message, delay)
	registry.client.log_message(USERNAME, message, user)

def is_op(channel):
	''' Checks if the bot is op in that channel '''
	if channel in registry.channels.keys():
		return registry.channels[channel]
	return False

def shorten_url(url):
	''' Shortens an URL. Currently uses tinyurl.com. '''
	handle = urllib2.urlopen('http://tinyurl.com/api-create.php?url=%s' % url)
	return handle.read()

