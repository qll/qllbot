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

def get_username(instance):
	''' Makes sure the user is a string and not a SilcUser or IrcUser object '''
	if not isinstance(instance, str):
		return instance.username
	else:
		return instance

def get_channelname(instance):
	''' Makes sure the channel name is a string and not a SilcChannel object '''
	if not isinstance(instance, str):
		return instance.channel_name
	else:
		return instance

def send_message(channel, message):
	''' Sends a message to a channel. '''
	registry.client.send_channel_message(channel, message.decode('utf-8'))
	registry.client.log_message(USERNAME, message, channel)

def shorten_url(url):
	''' Shortens an URL. Currently uses tinyurl.com. '''
	handle = urllib2.urlopen('http://tinyurl.com/api-create.php?url=%s' % url)
	return handle.read()

