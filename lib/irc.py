"""
IRC specific implementation details.
"""
import re
import lib.events
import lib.logging as log


# IRC max message size (specified in RFC)
MAX_MESSAGE_SIZE = 512


class Client:
	""" The client side logic the bot uses to communicate with IRC. """

	_irc_regex = (
		('channel_message', r'{user} PRIVMSG (?P<channel>#.+?) :(?P<message>.*)'),
		('private_message', r'{user} PRIVMSG .+? :(?P<message>.*)'), 
		('join',            r'{user} JOIN :{0,1}(?P<channel>#.+)'),
		('leave',           r'{user} PART :{0,1}(?P<channel>#.+)'),
		('quit',            r'{user} QUIT :(?P<message>.*)'),
		('invite',          r'{user} INVITE .+? :(?P<channel>#.+)'),
		('mode',            r'{user} MODE (?P<channel>#.+?) (?P<mode>.+?) (?P<user>.+)'),
		('topic',           r'{user} TOPIC (?P<channel>#.+?) :(?P<topic>.*)'),
		('kicked',          r'{user} KICK (?P<channel>#.+?) (?P<kicked>.+?) :(?P<message>.*)'),
		('nick_change',     r'{user} NICK :(?P<nickname>.+)'),
		('join_users',      r':.+? [\d]+ .+? [@=]{1} (?P<channel>#.+?) :(?P<users>.+)'),
		('join_topic',      r':.+? [\d]+ .+? (?P<channel>#.+?) :(?P<topic>(?!End of /NAMES list\.).*)'),
		# internally used events
		('nickname_in_use', r':.+? [\d]+ \* .+? :Nickname is already in use\.'),
		('ping',            r'PING (?P<pong>.*)')
	)
	_user_regex = r':(?P<nick>.*?)!~(?P<ident>.*?)@(?P<host>.*?)'

	def __init__(self, bot, nickname, realname, ident, password):
		""" Compiles all regexes and takes nickname, ident and password. """
		self._irc_regex = tuple((n, re.compile(r.replace('{user}', self._user_regex))) for n, r in self._irc_regex)
		self._bot = bot 
		self.nickname = nickname
		self.realname = realname
		self.ident = ident
		self.password = password
		# filled by core events
		self.channels = {}
	
	def identify(self, host):
		""" Identifies the Client with the server. """
		self._bot.send('NICK ' + self.nickname)
		self._bot.send('USER {0} {1} {2} :{3}'.format(self.ident, host, 0, self.realname))
		log.system('Identifying as {0}'.format(self.nickname))
	
	def join(self, channel, password = ''):
		""" Joins IRC channel. """
		self._bot.send('JOIN {0} {1}'.format(channel, password))
	
	def pong(self, code):
		self._bot.send('PONG ' + code)
	
	def say(self, channel, message):
		""" Says something in a IRC channel. """
		if not isinstance(message, str):
			message = str(message)
		if not isinstance(channel, str):
			channel = str(channel)
		for line in message.split('\n'):
			rest = ''
			# max message length of IRC = 512 (with \r\n)
			if len(line) > (MAX_MESSAGE_SIZE - 2):
				rest = line[MAX_MESSAGE_SIZE - 1:]
				line = line[:MAX_MESSAGE_SIZE - 2]
			self._bot.send('PRIVMSG {} :{}'.format(channel, line))
			lib.events.call('channel_message', [User(self.nickname, self.ident), channel, line])
			if rest:
				self.say(channel, rest)
	
	def pm(self, user, message):
		""" Sends a PM to a user. """
		self.say(user, message)

	def set_topic(self, channel, topic):
		""" Sets the topic in the channel if the bot resides in this channel and is operator. """
		if channel in self.channels and self.nickname in self.channels[channel].ops:
			self._bot.send('TOPIC {} :{}'.format(channel, topic))
			self.channels[channel].topic = topic

	def parse(self, response):
		""" Called when a \\r\\n was found. Checks for IRC commands. """
		for event, regex in self._irc_regex:
			result = regex.match(response)
			if result:
				parameters = []
				index = 1
				if set(('nick', 'ident', 'host')) <= set(result.groupdict()):
					parameters.append(
						User(result.group('nick'), result.group('ident'), result.group('host'))
					)
					index = 4
				for i in range(index, len(result.groups()) + 1):
					parameters.append(result.group(i))
				lib.events.call(event, parameters)
				return


class User:
	def __init__(self, nickname = '', ident = '', hostname = ''):
		self.nickname = nickname 
		self.ident = ident
		self.hostname = hostname
	
	def __str__(self):
		return self.nickname


class Channel:
	def __init__(self, name, topic = ''):
		self.users = {}
		self.ops = []
		self.voiced = []
		self.name = name
		self.topic = topic
	
	def remove_user(self, user):
		""" Since removing a user is not a trivial task, this method will help. """
		if user.nickname in self.users:
			self.users.pop(user.nickname)
		if user.nickname in self.ops:
			self.ops.remove(user.nickname)
		if user.nickname in self.voiced:
			self.voiced.remove(user.nickname)

	def is_op(self, user):
		""" Shortcut to check if a user is an operator in this channel. """
		return True if user.nickname in self.ops else False
	
	def is_voiced(self, user):
		""" Shortcut to check if a user is voiced in this channel. """
		return True if user.nickname in self.voiced else False
	
	def __str__(self):
		return self.name
