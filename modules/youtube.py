import re
from urllib.request import urlopen
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError
from lib.bot import Bot
from lib.events import subscribe


ATOM = 'http://www.w3.org/2005/Atom'
MRSS = 'http://search.yahoo.com/mrss/'


@subscribe('channel_message')
def display_youtube_video_title(sender, channel, message):
	""" Checks every message sent for a youtube link and displays title and uploader information """
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
		title    = info.findtext('{{{0}}}title'.format(ATOM))
		uploader = info.findtext('{{{0}}}author/{{{0}}}name'.format(ATOM)) 
		duration = int(info.find('{{{0}}}group/{{{0}}}content'.format(MRSS)).get('duration', '0'))
		hours = duration // 3600
		minutes = (duration - hours * 3600) // 60
		seconds = duration - hours * 3600 - minutes * 60
		if title != None and uploader != None:
			output.append('{0} [{1:02d}:{2:02d}:{3:02d}] (by {4})'.format(
				title, hours, minutes, seconds, uploader
			))
	if output:
		# send message back to channel
		client.say(channel, '\n'.join(output))
	
