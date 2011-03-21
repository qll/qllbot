#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import re
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import *
from qllbot.basic_functions import shorten_url
from qllbot.Registry import *
from settings import *


def get_feed(param):
	''' Returns a news feed (usage: #news bbc -> bbc news feed). Get available feeds with #news (without parameters). '''
	keys = NEWS_FEEDS.keys()
	if not param in keys:
		return 'Feed not in list. Loaded feeds: %s' % ', '.join(keys)

	handle = None
	try:
		handle = urllib2.urlopen(NEWS_FEEDS[param])
	except urllib2.HTTPError:
		return 'Did not find feed.'
	rss = ElementTree()
	try:
		rss.parse(handle)
	except ExpatError:
		return 'Malformed XML. This feed sucks! (Clean ATOM or RSS required!)'
	handle.close()

	title = rss.find('channel/title')
	if title == None:
		return 'Did not find any matching tags.'

	items   = ''
	counter = 0
	for item in rss.getiterator('item'):
		if counter >= NEWS_RESULTS:
			break
		counter += 1
		items   += '%s: %s\n' % (item.find('title').text.strip(), shorten_url(item.find('link').text))

	output = '[%s]\n%s' % (title.text.strip(), items[:-1])
	return output.encode('utf-8')


add_command('news', get_feed)
add_command('feed', get_feed)
