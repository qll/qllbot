"""IRC protocol implementation."""
import lib.events
import re


MAX_MSG_LEN = 512  # maximum IRC message length (with \r\n)


_irc_regex = (
    (
        'channel_message',
        r'%(user)s PRIVMSG (?P<channel>#[^ ]+) :(?P<msg>.*)'
    ), (
        'private_message',
        r'%(user)s PRIVMSG [^ ]+ :(?P<priv_msg>.*)'
    ), (
        'join',
        r'%(user)s JOIN :{0,1}(?P<channel>#[^\s]+)'
    ), (
        'leave',
        r'%(user)s PART :{0,1}(?P<channel>#[^\s]+)'
    ), (
        'quit',
        r'%(user)s QUIT :(?P<msg>.*)'
    ), (
        'invite',
        r'%(user)s INVITE [^ ]+ :(?P<channel>#[^ ]+)'
    ), (
        'mode',
        r'%(user)s MODE (?P<channel>#[^ ]+) (?P<mode>[^ ]+) (?P<receiver>.+)'
    ), (
        'topic',
        r'%(user)s TOPIC (?P<channel>#[^ ]+) :(?P<topic>.*)'
    ), (
        'kicked',
        r'%(user)s KICK (?P<channel>#[^ ]+) (?P<kicked>[^ ]+) :(?P<msg>.*)'
    ), (
        'nick_change',
        r'%(user)s NICK :(?P<nickname>[^ ]+)'
    ), (
        'join_users',
        r':[^ ]+ \d+ [^ ]+ [@=] (?P<channel>#[^ ]+) :(?P<users>.+)'
    ), (
        'join_topic',
        r':[^ ]+ \d+ [^ ]+ (?P<channel>#[^ ]+) :(?P<topic>(?!End of /NAMES).*)'
    ),
    # internally used events
    (
        'nickname_in_use',
        r':[^ ]+ \d+ \* [^ ]+ :Nickname is already in use\.'
    ),
    (
        'ping',
        r'PING (?P<code>.*)'
    ),
    (
        'pong',
        r':[^ ]+ PONG [^ ]+ :(?P<code>.+)'
    ),
)
_user_regex = r':(?P<nick>[^!]+)!~?(?P<ident>[^@]+)@(?P<host>[^ ]+)'


# compile all regexes
_irc_regex = tuple((n, re.compile(r % {'user': _user_regex}))
                   for n, r in _irc_regex)


class User(object):
    def __init__(self, nick, ident='', host=''):
        self.nick = nick
        self.ident = ident
        self.host = host

    def __eq__(self, user):
        print(self)
        print(user)
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
    def __init__(self, name):
        self.name = name

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
    def __init__(self, msg, private=False):
        self.content = msg
        self.private = private
        self.channel = None
        self.sender = None

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


def _build_msg(dict_, key, private=False):
    dict_[key] = Message(dict_[key], private)
    if 'sender' in dict_:
        dict_[key].sender = dict_['sender']
        del dict_['sender']
    if 'channel' in dict_:
        dict_[key].channel = dict_['channel']
        del dict_['channel']


def parse(msg):
    """Parses an IRC message using regular expressions."""
    for event, regex in _irc_regex:
        m = regex.match(msg)
        if m:
            d = m.groupdict()
            if 'nick' in d:
                d['sender'] = User(d['nick'], d['ident'], d['host'])
                del d['nick'], d['ident'], d['host']
            if 'channel' in d:
                d['channel'] = Channel(d['channel'])
            if 'msg' in d:
                _build_msg(d, 'msg')
            if 'priv_msg' in d:
                _build_msg(d, 'priv_msg', True)
            return event, d
    return None, None
