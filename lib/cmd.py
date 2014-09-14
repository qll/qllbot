"""Manages all bot commands."""
import lib.irc


cmds = {}
private_cmds = {}


class CommandMessage(lib.irc.Message):
    def __init__(self, msg, cmd_char):
        super().__init__(msg.content, msg.private)
        self.cmd_char = cmd_char
        self.channel = msg.channel
        self.sender = msg.sender
        self.bot = None
        self.cmd = None
        self.params = None
        if msg.content.startswith(cmd_char):
            content = msg.content[1:]
            if ' ' in content:
                self.cmd, self.params = content.split(' ', 1)
            else:
                self.cmd = content

    def is_command(self):
        return self.cmd is not None


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
        return cmd_dict[cmd](msg)
