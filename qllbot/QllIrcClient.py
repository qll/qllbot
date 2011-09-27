#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket, re
from settings import *
from qllbot.QllClient import QllClient
from qllbot.IrcUser   import IrcUser
from qllbot.Registry  import Registry


# IRC max message size (specified in RFC)
MAX_MESSAGE_SIZE = 512


registry = Registry()
events   = registry.eventsys


class QllIrcClient(QllClient):
	''' Implements an IRC client from ground up with a nonblocking socket (currently). '''

	# entries in following format: (event_name, sent_by_user?, regular_expression)
	irc_regex = (
		('channel_message', True,  r'PRIVMSG (?P<channel>#.+?) :(?P<message>.*)'),
		('private_message', True,  r'PRIVMSG .+? :(?P<message>.*)'), 
		('join',            True,  r'JOIN :{0,1}(?P<channel>#.+)'),
		('leave',           True,  r'PART :{0,1}(?P<channel>#.+)'),
		('quit',            True,  r'QUIT :(?P<message>.*)'),
		('invite',          True,  r'INVITE .+? :(?P<channel>#.+)'),
		('mode',            True,  r'MODE (?P<channel>#.+?) (?P<mode>.+?) (?P<user>.+)'),
		('topic',           True,  r'TOPIC (?P<channel>#.+?) :(?P<topic>.*)'),
		('kicked',          True,  r'KICK (?P<channel>#.+?) (?P<kicked>.+?) :(?P<message>.*)'),
		('join_users',      False, r':.+? [\d]+ .+? [@=]{1} (?P<channel>#.+?) :(?P<users>.+)'),
		('join_topic',      False, r':.+? [\d]+ .+? (?P<channel>#.+?) :(?P<topic>(?!End of /NAMES list\.).*)'),
		# internally used events
		('nickname_in_use', False, r':.+? [\d]+ \* .+? :Nickname is already in use\.'),
		('ping',            False, r'PING (?P<pong>.*)')
	)
	regex_user = r':(?P<nick>.*?)!~(?P<name>.*?)@(?P<host>.*?) '

	def __init__(self):
		self.buffer = ''
		self.irc    = None
		self.commands = []
		self.iteration_counter = 0
	
	def run(self):
		''' Starts the client '''
		self.running()
	
	def found_terminator(self, response):
		''' Called when a \r\n was found. Checks for IRC commands. '''
		for event, has_sender, regex in self.irc_regex:
			if has_sender:
				regex = self.regex_user + regex
			result = re.match(regex, response)
			if result:
				parameters = []
				startindex = 1
				if has_sender:
					sender = self.create_IrcUser(result.group('nick'), result.group('name'), result.group('host'))
					parameters.append(sender)
					startindex = 4
				for i in range(startindex, len(result.groups()) + 1):
					parameters.append(result.group(i))
				events.call(event, *parameters)
				return

	def run_one(self):
		''' Checks if the socket recieved some data '''
		try:
			self.buffer += self.irc.recv(512)
		except socket.error:
			pass # this is expected behaviour with nonblocking sockets!

		if self.buffer != '':
			if DEBUG:
				print(self.buffer)
			strings = self.buffer.split('\r\n')
			# buffer unfinished messages
			if strings[len(strings) - 1] != '':
				self.buffer = strings.pop()
			else:
				self.buffer = ''
				
			for string in strings:
				try:
					string = string.decode('utf-8', 'replace').strip()
					if string != '':
						self.found_terminator(string)
				except UnicodeDecodeError:
					print('Error: UnicodeDecodeError')

		# flooding prevention
		self.iteration_counter += 1
		if self.iteration_counter >= 5:
			self.command_iteration()
			self.iteration_counter = 0

	def command_call(self, command, delay = False):
		''' Sends an IRC command '''
		if isinstance(command, unicode):
			command = command.encode('utf-8')
		if not delay:
			try:
				self.irc.send('%s\r\n' % command)
			except socket.error:
				self.disconnected()
		else:
			self.commands.append(command)
	
	def command_iteration(self):
		if len(self.commands) > 0:
			command = self.commands.pop(0)
			try:
				self.irc.send('%s\r\n' % command)
			except socket.error:
				self.disconnected()

	def connect_to_server(self, server, port = 6667):
		''' Connects to a IRC Server '''
		if PORT != '':
			port = PORT
		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.irc.connect((server, port))
		self.irc.setblocking(0)
		self.command_call('NICK %s' % registry.username)
		self.command_call('USER %s %d %d :%s' % (registry.username, 0, 0, REALNAME))
		self.connected_to_server()

	def send_channel_message_event(self, channel, username, message):
		event = 'send_private_message'
		if channel.startswith('#'):
			event = 'send_channel_message'
		events.call(event, username, channel, message)

	def send_channel_message(self, channel, message, delay = False):
		''' Sends a message to a channel '''
		for line in message.split('\n'):
			# max message length of IRC = 512 (with \r\n)
			if len(line) > (MAX_MESSAGE_SIZE - 2):
				self.command_call('PRIVMSG %s :%s' % (channel, line[:(MAX_MESSAGE_SIZE - 2)]), delay)
				self.send_channel_message_event(channel, registry.username, line)
				self.send_channel_message(line[(MAX_MESSAGE_SIZE - 1):])
			else:
				self.command_call('PRIVMSG %s :%s' % (channel, line), delay)
				self.send_channel_message_event(channel, registry.username, line)
	
	def send_private_message(self, user, message, delay = False):
		self.send_channel_message(user, message, delay)
	
	def set_topic(self, channel, topic):
		if registry.channels[channel].is_op(registry.username):
			self.command_call('TOPIC %s :%s' % (channel, topic))

	def create_IrcUser(self, nickname, realname, host):
		user = IrcUser()
		user.nickname = nickname
		user.username = nickname
		user.realname = realname
		user.host     = host
		return user

