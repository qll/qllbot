import lib.cmd


@lib.cmd.command()
def commands(msg):
    """Return all available commands."""
    cmd_dict = lib.cmd.private_cmds if msg.private else lib.cmd.cmds
    return 'Available commands: %s' % ', '.join(cmd_dict)


@lib.cmd.command()
def help(msg):
    """Prints usage information for a command (#help help -> this text)."""
    if not msg.params:
        return ('Type in %(cmdc)scommands for a list of commands or '
                '%(cmdc)shelp [command] for help concerning a command.' %
                {'cmdc': msg.cmd_char})
    cmd_dict = lib.cmd.private_cmds if msg.private else lib.cmd.cmds
    if msg.params in cmd_dict:
        return '%s%s: %s' % (msg.cmd_char, msg.params,
                             cmd_dict[msg.params].__doc__)
    return 'Command %s%s not found.' % (msg.cmd_char, msg.params)
