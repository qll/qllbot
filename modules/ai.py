import lib.cmd
import lib.event
import lib.irc
import random
import settings


GREETINGS = ('hi', 'hey ho', 'yoyo!', 'sup\'')


@lib.event.subscribe('join')
def say_hello(bot=None, sender=None, channel=None):
    """Greets the channel when joining it."""
    if sender == settings.NICKNAME:
        bot.send(lib.irc.say(channel, random.choice(GREETINGS)))
