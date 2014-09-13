"""Manages all bot commands."""


cmds = {}
private_cmds = {}


class command(object):
    """Decorator defining a bot command.

    The alias parameter takes a str or list of aliases. If the command should
    not be available via private msg, invoke the decorator with private=False.
    """

    def __init__(self, alias=None, private=True):
        self.alias = alias
        self.private = private

    def __call__(self, function):
        if self.alias is None:
            alias = (function.__name__,)
        elif isinstance(alias, str):
            alias = (function.__name__, alias)
        else:
            alias.append(function.__name__)
        for name in alias:
            cmds[name] = function
            if self.private:
                private_cmds[name] = function
        return function


def execute(cmd, msg, private=False):
    """Execute command or private command."""
    cmd_dict = private_cmds if private else cmds
    if cmd in cmd_dict:
        try:
            return cmd_dict[cmd](msg)
        except Exception:
            _log.exception('Exception in command %s:' % cmd)
            return 'Well done - an exception occured! Logs will tell you more.'
