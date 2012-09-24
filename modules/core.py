import lib.commands
from lib.commands import command, pm_command


@command()
@pm_command()
def commands(param):
	""" Returns all loaded commands. """
	output = 'Loaded commands:\n'
	return output + ', '.join(lib.commands.pm_commands if lib.commands.is_pm else lib.commands.commands)


@command()
@pm_command()
def help(param):
	""" Prints out the documentation string for a given command (e.g. #help help -> this text). """
	if param == '':
		return 'Type in #commands for a list of commands or #help [command] for help concerning a command.'
	cmdlist = lib.commands.pm_commands if lib.commands.is_pm else lib.commands.commands
	if param in cmdlist:
		return '#{}: {}'.format(param, cmdlist[param].__doc__)
	return 'Command not found.'

