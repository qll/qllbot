import lib.cmd
import lib.event
import lib.irc
import settings
import sys


@lib.event.subscribe('invite')
def join_on_invite(bot=None, sender=None, channel=None):
    """If the bot owner invites the bot to a channel, it will join."""
    if sender == settings.OWNER:
        bot.send(lib.irc.join(channel))


@lib.event.subscribe('private_message')
def snitch(bot=None, priv_msg=None):
    """Tells the OWNER if the bot is contacted via PM and the exact content."""
    if priv_msg.sender != settings.OWNER:
        snitch_msg = '%s said to me: %s' % (priv_msg.sender, priv_msg.content)
        bot.send(lib.irc.say_to(settings.OWNER, snitch_msg))


@lib.cmd.command()
def quit(msg):
    """Shuts down the bot. Only possible if you are the owner of the bot!"""
    if msg.sender != settings.OWNER:
        return 'I would love to but you are not my owner...'
    text = 'Goodbye :)'
    response = (lib.irc.say_to(msg.sender, text) if msg.private else
                lib.irc.say(msg.channel, text))
    msg.bot.send(response)
    msg.bot.disconnect()
    sys.exit()


@lib.cmd.command()
def say(msg):
    """Echoes the given string in the specified channel (#say channel text)."""
    if msg.sender != settings.OWNER:
        return 'Since you are not my owner, I say nay.'
    try:
        channel, message = msg.params.split(' ', 1)
        msg.bot.send(lib.irc.say(channel, message))
    except ValueError:
        return 'Incorrect format. Try #say channel text.'
