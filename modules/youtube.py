import re
from urllib.request import urlopen
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
from lib.bot import Bot
from lib.events import subscribe


ATOM = 'http://www.w3.org/2005/Atom'


@subscribe('channel_message')
def display_youtube_video_title(sender, channel, message):
	""" Checks every message sent for a youtube link and displays title and uploader information """
	#http://youtu.be/Jdm6Fb65K0E
	client = Bot().client
	results = re.finditer(r'https?://(?:(?:www\.)?youtube\.com/watch\?.*?v=|youtu\.be/)(?P<id>[-_\w]{11})', message) 
	output = []
	for result in results:
		handle = None
		try:
			handle = urlopen('http://gdata.youtube.com/feeds/api/videos/{}?v=2'.format(result.group('id')))
		except Exception as error:
			client.say(channel, error)
		info = ElementTree()
		try:
			info.parse(handle)
		except ExpatError:
			client.say(channel, 'Error: Malformed XML.')
		handle.close()
		title    = info.findtext('{%s}title' % ATOM)
		uploader = info.findtext('{%s}author/{%s}name' % (ATOM, ATOM)) 
		if title != None and uploader != None:
			output.append("'{}' uploaded by {}".format(title, uploader))
	if output:
		# send message back to channel
		client.say(channel, '\n'.join(output))
	
