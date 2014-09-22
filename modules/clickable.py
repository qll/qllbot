import lib.event
import lib.irc
import re


LINK = re.compile(r' ((?:[\w\-]+\.)*[\w\-]+\.[a-zA-Z]+\/[^\s]*) ')


@lib.event.subscribe('channel_message')
def make_links_clickable(bot=None, msg=None):
    """Checks every message for unclickable links and makes them clickable."""
    matches = LINK.finditer(' %s ' % msg.content)
    output = ['http://%s' % m.group(1) for m in matches]
    if output:
        # send message back to channel
        bot.send(lib.irc.say(msg.channel, 'Clickable: %s' % ' '.join(output)))
