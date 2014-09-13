import lib.cmd


@lib.cmd.command()
def commands(msg):
    """Return all available commands."""
    cmd_dict = lib.cmd.private_cmds if msg.private else lib.cmd.cmds
    return 'Available commands: %s' % ', '.join(cmd_dict)


# @lib.cmd.command()
# def help(msg):
#     """Prints usage information for a command (#help help -> this text)."""
#     param = msg.content.split(' ', 1)[1]
#     if param == '':
#         return 'Type in #commands for a list of commands or #help [command] for help concerning a command.'
#     cmdlist = lib.commands.pm_commands if lib.commands.is_pm else lib.commands.commands
#     if param in cmdlist:
#         return '#{}: {}'.format(param, cmdlist[param].__doc__)
#     return 'Command not found.'
