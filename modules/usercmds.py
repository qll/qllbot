import contextlib
import lib.cmd
import lib.event
import lib.irc


USERCMD_CHAR = '!'


_user_cmds = {}  # storage for all user commands during runtime


@lib.event.subscribe('new_db')
def create_usercmds_schema(db=None):
    """Creates the usercmds SQLite schema."""
    db.execute('CREATE TABLE usercmds (cmd TEXT PRIMARY KEY, response TEXT)')
    db.commit()


@lib.event.subscribe('connected')
def fetch_usercmds(bot=None):
    """Fetches all user commands at the start of the bot."""
    with contextlib.closing(bot.db.cursor()) as c:
        c.execute('SELECT cmd, response FROM usercmds')
        for cmd, response in c:
            _user_cmds[cmd] = response


@lib.event.subscribe('channel_message')
def invoke_usercmd(bot=None, msg=None):
    if msg.content.startswith(USERCMD_CHAR) and msg.content[1:] in _user_cmds:
        bot.send(lib.irc.say(msg.channel, _user_cmds[msg.content[1:]]))


@lib.cmd.command(alias=['usercmd'])
def cmd(msg):
    """Creates or changes an user command (#usercmd name response)."""
    if not msg.params or ' ' not in msg.params:
        return 'Usage: #usercmd name response'
    cmd, response = msg.params.split(' ', 1)
    if cmd in _user_cmds:
        msg.bot.db.execute('UPDATE usercmds SET response=? WHERE cmd=?',
                           (response, cmd))
    else:
        msg.bot.db.execute('INSERT INTO usercmds VALUES (?, ?)',
                           (cmd, response))
    msg.bot.db.commit()
    _user_cmds[cmd] = response
    return 'User command stored. Usage: %s%s' % (USERCMD_CHAR, cmd)


@lib.cmd.command()
def listcmds(msg):
    """Lists all user commands."""
    if not _user_cmds:
        return 'Nope. No commands yet. Add one!'
    return ', '.join('!%s' % k for k in _user_cmds)


@lib.cmd.command()
def delcmd(msg):
    """Delete a user command (#delcmd name)"""
    if not msg.params:
        return 'Usage: #delcmd name'
    cmd = msg.params
    if cmd not in _user_cmds:
        return 'Command not found. Wanna list them all? #listcmds'
    msg.bot.db.execute('DELETE FROM usercmds WHERE cmd=?', (cmd,))
    msg.bot.db.commit()
    del _user_cmds[cmd]
    return 'Command %s deleted. Bye bye' % cmd
