import sys
from lib.bot import Bot
from lib.commands import command, pm_command, owner_command, get_channel


@command()
@pm_command()
@owner_command()
def quit(param):
	""" Shuts down the bot. Only possible if you are the owner of the bot! """
	Bot().client.say(get_channel(), 'Goodbye :)')
	sys.exit()

