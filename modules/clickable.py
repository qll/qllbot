import lib.events
import lib.irc
import re


@lib.events.subscribe('channel_message')
def make_links_clickable(bot=None, msg=None):
    """Checks every message for unclickable links and makes them clickable."""
    matches = re.finditer(r'\w+\.[a-zA-Z]+\/[^\s]*', msg.content)
    output = ['http://%s' % m.group(0) for m in matches]
    if output:
        # send message back to channel
        bot.send(lib.irc.say(msg.channel, 'Clickable: %s' % ' '.join(output)))
