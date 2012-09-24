import time as time_module
from lib.commands import command, pm_command, owner_command
from lib.bot import Bot


@pm_command()
@command()
def time(param):
	""" Returns current date and time in following format: dayname, day.month.year, hour:minute:second. """
	return time_module.strftime('%A, %d.%m.%Y, %H:%M:%S', time_module.localtime())


@pm_command()
@owner_command()
def say(param):
	''' Echoes the given string to the submitted channel (#say [channel] [text]). '''
	client = Bot().client
	param = param.split(' ', 1)
	if len(param) < 2 or param[0] not in client.channels:
		return 'Incorrect format or channel not known to bot. Try #say [channel] [text].'
	client.say(param[0], param[1])
	return ''

