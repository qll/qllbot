"""IRC protocol implementation."""
import re


MAX_MSG_LEN = 512  # maximum IRC message length (with \r\n)


_irc_regex = (
    (
        'channel_message', '_handle_channel_message',
        r'%(user)s PRIVMSG (?P<channel>#[^ ]+) :(?P<msg>.*)'
    ), (
        'private_message', '_handle_private_message',
        r'%(user)s PRIVMSG [^ ]+ :(?P<msg>.*)'
    ), (
        'join', '_handle_join',
        r'%(user)s JOIN :{0,1}(?P<channel>#[^\s]+)'
    ), (
        'part', '_handle_part',
        r'%(user)s PART :{0,1}(?P<channel>#[^\s]+)'
    ), (
        'quit', '_handle_quit',
        r'%(user)s QUIT :(?P<msg>.*)'
    ), (
        'invite', '_handle_invite',
        r'%(user)s INVITE [^ ]+ :(?P<channel>#[^ ]+)'
    ), (
        'mode', '_handle_mode',
        r'%(user)s MODE (?P<channel>#[^ ]+) (?P<mode>[^ ]+) (?P<receiver>.+)'
    ), (
        'topic', '_handle_topic',
        r'%(user)s TOPIC (?P<channel>#[^ ]+) :(?P<topic>.*)'
    ), (
        'kick', '_handle_kick',
        r'%(user)s KICK (?P<channel>#[^ ]+) (?P<kicked>[^ ]+) :(?P<msg>.*)'
    ), (
        'nick', '_handle_nick',
        r'%(user)s NICK :(?P<new_nick>[^ ]+)'
    ), (
        'join_users', '_handle_join_users',
        r':[^ ]+ \d+ [^ ]+ [@=] (?P<channel>#[^ ]+) :(?P<users>.+)'
    ), (
        'join_topic', '_handle_join_topic',
        r':[^ ]+ \d+ [^ ]+ (?P<channel>#[^ ]+) :(?P<topic>(?!End of /NAMES).*)'
    ),
    # internally used events
    (
        'nickname_in_use', None,
        r':[^ ]+ \d+ \* [^ ]+ :Nickname is already in use\.'
    ),
    (
        'ping', None,
        r'PING (?P<code>.*)'
    ),
    (
        'pong', None,
        r':[^ ]+ PONG [^ ]+ :(?P<code>.+)'
    ),
)
_user_regex = r':(?P<nick>[^!]+)!~?(?P<ident>[^@]+)@(?P<host>[^ ]+)'


# compile all regexes
_irc_regex = tuple((n, f, re.compile(r % {'user': _user_regex}))
                   for n, f, r in _irc_regex)


_users = {}  # store all already seen users with their meta information
_channels = {}  # stores all already seen channels with their meta information


class User(object):
    def __init__(self, nick, ident='', host=''):
        self.nick = nick
        self.ident = ident
        self.host = host

    def __eq__(self, user):
        if isinstance(user, User):
            return self.nick == user.nick
        if isinstance(user, str):
            return self.nick == user
        return False

    def __ne__(self, user):
        return not self.__eq__(user)

    def __str__(self):
        return self.nick


class Channel(object):
    def __init__(self, name, topic=''):
        self.name = name
        self.topic = topic
        self.users = []
        self.ops = []
        self.voiced = []

    def part(self, user):
        if user in self.users:
            self.users.remove(user)
        if user in self.ops:
            self.ops.remove(user)
        if user in self.voiced:
            self.voiced.remove(user)

    def __eq__(self, channel):
        if isinstance(channel, Channel):
            return self.name == channel.name
        if isinstance(channel, str):
            return self.name == channel
        return False

    def __ne__(self, channel):
        return not self.__eq__(channel)

    def __str__(self):
        return self.name


class Message(object):
    def __init__(self, msg, sender=None, channel=None, private=False):
        self.content = msg
        self.sender = sender
        self.channel = channel
        self.private = private

    def __str__(self):
        return self.content


def identify(nick, host):
    """Return IRC commands which identify the bot to the server."""
    fmt = {'nick': nick, 'host': host}
    return 'NICK %(nick)s\r\nUSER %(nick)s %(host)s 0 :%(nick)s' % fmt


def join(channel, password=''):
    """Return command to join an IRC channel."""
    return 'JOIN %s %s' % (channel, password)


def ping(code):
    return 'PING %s' % code


def password(pw):
    return 'PASS %s' % pw


def pong(code):
    return 'PONG %s' % code


def say(channel, msg):
    """Convert msg to valid IRC PRIVMSG commands."""
    if not isinstance(msg, str):
        msg = str(msg)
    output = ''
    for line in msg.split('\n'):
        rest = ''
        if len(line) > (MAX_MSG_LEN - 2):
            rest = line[MAX_MSG_LEN - 1:]
            line = line[:MAX_MSG_LEN - 2]
        output += 'PRIVMSG %s :%s\r\n' % (channel, line)
        if rest:
            output += say(channel, rest)
    return output


def say_to(user, msg):
    """Sends a private message to another user."""
    return say(user, msg)


def quit(msg=''):
    """Return a valid QUIT message with an optional reason."""
    return 'QUIT :%s' % msg


def parse(msg):
    """Parses an IRC message using regular expressions."""
    for event, func, regex in _irc_regex:
        m = regex.match(msg)
        if m:
            dict_ = m.groupdict()
            if func is not None:
                dict_ = globals()[func](**dict_)
            return event, dict_
    return None, None


# IRC handling functions
def _fold_sender(func):
    """Fold the nick, ident and host parameters to a single User object.

    Decorator which checks the internal user cache for the user and returns it.
    If the user did not exist before it will create a new User object.
    """
    def _wrap(nick='', ident='', host='', **kwargs):
        if nick not in _users:
            _users[nick] = User(nick, ident, host)
        if not _users[nick].ident:  # may not be known yet
            _users[nick].ident = ident
            _users[nick].host = host
        return func(sender=_users[nick], **kwargs)
    return _wrap


def _fold_channel(func):
    """Fold the channel name into a Channel object.

    Decorator which checks the internal channel cache for the channel and
    returns it. If the channel did not exist before it will create a new
    Channel object.
    """
    def _wrap(channel='', **kwargs):
        if channel not in _channels:
            _channels[channel] = Channel(channel)
        return func(channel=_channels[channel], **kwargs)
    return _wrap


@_fold_sender
@_fold_channel
def _handle_channel_message(sender=None, channel=None, msg=''):
    return {'msg': Message(msg, sender=sender, channel=channel)}


@_fold_sender
@_fold_channel
def _handle_private_message(sender=None, channel=None, msg=''):
    return {'msg': Message(msg, sender=sender, channel=channel, private=True)}


@_fold_sender
@_fold_channel
def _handle_join(sender=None, channel=None):
    if sender not in channel.users:
        channel.users.append(sender)
    return {'sender': sender, 'channel': channel}


@_fold_sender
@_fold_channel
def _handle_part(sender=None, channel=None):
    channel.part(sender)
    return {'sender': sender, 'channel': channel}


@_fold_sender
def _handle_quit(sender=None, msg=''):
    for channel in _channels.values():
        channel.part(sender)
    return {'sender': sender, 'msg': msg}


@_fold_sender
@_fold_channel
def _handle_invite(**kwargs):
    return kwargs


@_fold_sender
@_fold_channel
def _handle_mode(sender=None, channel=None, mode='', receiver=''):
    if receiver in _users:
        if mode == '+o' and _users[receiver] not in channel.ops:
            channel.ops.append(_users[receiver])
        elif mode == '-o' and _users[receiver] in channel.ops:
            channel.ops.remove(_users[receiver])
        elif mode == '+v' and _users[receiver] not in channel.voiced:
            channel.voiced.append(_users[receiver])
        elif mode == '-v' and _users[receiver] in channel.voiced:
            channel.voiced.remove(_users[receiver])
    return {'sender': sender, 'channel': channel, 'mode': mode,
            'receiver': receiver}


@_fold_sender
@_fold_channel
def _handle_topic(sender=None, channel=None, topic=''):
    old_topic = channel.topic
    channel.topic = topic
    return {'sender': sender, 'channel': channel, 'old_topic': old_topic,
            'new_topic': topic}


@_fold_sender
@_fold_channel
def _handle_kick(sender=None, channel=None, kicked='', msg=''):
    if kicked not in _users:
        raise IndexError('Never heard of the kicked user %s.' % kicked)
    channel.part(_users[kicked])
    return {'sender': sender, 'channel': channel, 'kicked': _users[kicked],
            'msg': msg}


@_fold_sender
def _handle_nick(sender=None, new_nick=''):
    old_nick = sender.nick
    sender.nick = new_nick
    _users[new_nick] = sender
    del _users[old_nick]
    return {'sender': sender, 'old_nick': old_nick, 'new_nick': new_nick}


@_fold_channel
def _handle_join_users(channel=None, users=''):
    """Populates the channel users and ops lists."""
    for nick in users.split(' '):
        op = nick.startswith('@')
        voice = nick.startswith('+')
        if op or voice:
            nick = nick[1:]
        if nick not in _users:
            _users[nick] = User(nick)
        if _users[nick] not in channel.users:
            channel.users.append(_users[nick])
        if op and _users[nick] not in channel.ops:
            channel.ops.append(_users[nick])
        if voice and _users[nick] not in channel.voiced:
            channel.voiced.append(_users[nick])
    return {'channel': channel, 'users': users}


@_fold_channel
def _handle_join_topic(channel=None, topic=''):
    """Populates channel topics."""
    channel.topic = topic
    return {'channel': channel, 'topic': topic}
