import lib.event
import lib.irc
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree
import xml.parsers.expat


API_URI = 'http://gdata.youtube.com/feeds/api/videos/%(id)s?v=2'


NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'mrss': 'http://search.yahoo.com/mrss/',
}


@lib.event.subscribe('channel_message')
def display_youtube_metadata(bot=None, msg=None):
    """Checks every message for youtube links and displays meta information."""
    if 'nospoiler' in msg.content:
        return
    matches = re.finditer(r'https?://(?:(?:www\.)?youtube\.com/watch\?.*?v='
                          '|youtu\.be/)(?P<id>[-_\w]{11})', msg.content)
    output = []
    for match in matches:
        info = xml.etree.ElementTree.ElementTree()
        with urllib.request.urlopen(API_URI % match.groupdict()) as h:
            info.parse(h)
        title = info.findtext('{%(atom)s}title' % NS)
        uploader = info.findtext('{%(atom)s}author/{%(atom)s}name' % NS)
        if title is None or uploader is None:
            raise Exception('Cannot find either title and/or uploader.')
        duration = info.find('{%(mrss)s}group/{%(mrss)s}content' % NS)
        duration = int(duration.get('duration', '0'))
        hours = duration // 3600
        minutes = (duration - hours * 3600) // 60
        seconds = duration - hours * 3600 - minutes * 60
        output.append('%s [%02d:%02d:%02d] (by %s)' % (title, hours, minutes,
                                                       seconds, uploader))
    if output:
        # send message back to channel
        bot.send(lib.irc.say(msg.channel, '\n'.join(output)))
