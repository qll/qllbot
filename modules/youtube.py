#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2, re
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import *
from qllbot.Registry import *
from qllbot.static_vars import *
from qllbot.basic_functions import send_message


def display_youtube_video_title(sender, channel, message):
	''' Checks every message sent for a youtube link and displays title and uploader information '''
	results = re.finditer(r'http://(www\.)?youtube\.com/watch\?.*?v=(?P<id>[-_\w]{11})', message) 
	output = u''
	for result in results:
		handle = None
		try:
			handle = urllib2.urlopen('http://gdata.youtube.com/feeds/api/videos/%s?v=2' % result.group('id'))
		except urllib2.HTTPError:
			send_message(u'Error: Cannot open Youtube API.')

		info = ElementTree()
		try:
			info.parse(handle)
		except ExpatError:
			send_message(u'Error: Malformed XML.')
		handle.close()

		title    = info.findtext('{%s}title' % ATOM)
		uploader = info.findtext('{%s}author/{%s}name' % (ATOM, ATOM)) 
		if title != None and uploader != None:
			output += u"'%s' uploaded by %s\n" % (title, uploader)

	if output != u'':
		# strip last \n in output
		output = output[:-1]
		# send message back to channel
		send_message(channel, output)


subscribe('channel_message', display_youtube_video_title)
