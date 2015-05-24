import lib.event
import lib.irc
import re
import urllib.error
import urllib.request
import settings
import json


API_URI = ('https://www.googleapis.com/youtube/v3/videos?id=%s'
           '&part=contentDetails,snippet&key=' + settings.YOUTUBE_API_KEY)


@lib.event.subscribe('channel_message')
def display_youtube_metadata(bot=None, msg=None):
    """Checks every message for youtube links and displays meta information."""
    if 'nospoiler' in msg.content:
        return
    matches = re.finditer(r'https?://(?:(?:www\.)?youtube\.com/watch\?.*?v='
                          '|youtu\.be/)(?P<id>[-_\w]{11})', msg.content)
    output = []
    ids = [match.group('id') for match in matches]
    with urllib.request.urlopen(API_URI % ','.join(ids)) as h:
        data = json.loads(h.read().decode("utf-8"))
    for vid in data["items"]:
        duration = re.search(
            r'PT((?P<hours>\d{1,2})H)?(?P<minutes>\d{1,2})'
             'M(?P<seconds>\d{1,2})S', vid["contentDetails"]["duration"])
        params = {k: int(v) for k, v in duration.groupdict(default=0).items()}
        params["title"] = vid["snippet"]["title"]
        params["uploader"] = vid["snippet"]["channelTitle"]
        output.append(
            '%(title)s [%(hours)02d:%(minutes)02d:%(seconds)02d] '
            '(by %(uploader)s)' % params)
    if output:
        # send message back to channel
        bot.send(lib.irc.say(msg.channel, '\n'.join(output)))
