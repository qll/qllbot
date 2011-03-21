#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import re
from xml.dom import minidom
from qllbot.Registry import *
from qllbot.basic_functions import strip_tags, send_message


def display_youtube_video_title(param):
	''' Checks every message sent for a youtube link and displays title and uploader information '''
	results = re.finditer(r'http://(www\.)?youtube\.com/watch\?.*?v=(?P<id>[-_\w]{11})', param['message'])
	output = ''
	for result in results:
		handle = urllib2.urlopen('http://gdata.youtube.com/feeds/api/videos/%s?v=2' % result.group('id'))
		dom    = minidom.parse(handle)
		handle.close()
		# get video title
		for node in dom.getElementsByTagName('title'):
			output += '\'%s\'' % strip_tags(node.toxml())
		# get uploader name
		for node in dom.getElementsByTagName('name'):
			output += ' uploaded by %s\n' % strip_tags(node.toxml())
	if output != '':
		# strip last \n in output and encode in utf-8
		output = output[:-1].encode('utf-8')
		# send message back to channel
		send_message(param['channel'], output)


subscribe('channel_message', display_youtube_video_title)
