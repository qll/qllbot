"""
Contains code to handle commands.
"""
from lib.bot import Bot
from settings import OWNER


commands = {}
pm_commands = {}
owner_commands = []
sender = ''		# current sender
channel = ''	# current channel
pm_sender = ''	# current sender of pm
is_pm = False	# is the current command reacting to a pm


def command(alias = [], commands = commands):
	def decorator(function, alias = alias, commands = commands):
		if isinstance(alias, str):
			alias = (alias,)
		commands[function.__name__] = function
		for a in alias:
			commands[a] = function
		return function
	return decorator


def pm_command(alias = []):
	return command(alias, pm_commands)


def owner_command():
	def decorator(function):
		owner_commands.append(function.__name__)
		return function
	return decorator


def execute_command(sender, command, param = None, commands = commands):
	if command in commands:
		if command in owner_commands:
			if sender.nickname != OWNER:
				return 'You are not allowed to execute this command D:<'
		try:
			if param:
				return commands[command](param);
			return commands[command]('');
		except Exception as e:
			return "If you're happy and you know it: Exception!\n{}".format(e)
	return ''


def execute_pm_command(sender, command, param = None):
	return execute_command(sender, command, param, pm_commands)


def set_sender(user):
	global sender
	sender = user


def set_pm_sender(sender):
	global pm_sender
	pm_sender = sender


def set_channel(chan):
	global channel
	channel = chan


def get_sender():
	return sender


def get_channel():
	return channel


def get_pm_sender():
	return pm_sender

