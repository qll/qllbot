#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, socket
from re import match
from settings import *
from qllbot.QllClient import QllClient
from qllbot.IrcUser import IrcUser
from qllbot.Registry import Registry


# constants which should not be changed
MAX_MESSAGE_SIZE = 512


# event system
events = Registry().eventsys


class QllIrcClient(QllClient):
	def __init__(self):
		self.buffer = ''
		self.irc    = None
		self.commands = []
		self.iteration_counter = 0
	
	def run(self):
		''' Starts the client '''
		self.running()
	
	
	def found_terminator(self, response):
		''' Interprets IRC commands. '''
		re_user = r':(?P<nick>.*?)!~(?P<name>.*?)@(?P<host>.*?) '

		# channel message
		regex = match(re_user + r'PRIVMSG (?P<channel>#.+?) :(?P<message>.*)', response)
		if (regex):
			sender = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('channel_message', {'sender': sender, 'channel': regex.group('channel'), 'flags': '', 'message': regex.group('message')})
			return
		# private message
		regex = match(re_user + r'PRIVMSG .+? :(?P<message>.*)', response)
		if (regex):
			sender = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('private_message', {'sender': sender, 'channel': '@PM', 'flags': '', 'message': regex.group('message')})
			return
		# user joined channel
		regex = match(re_user + r'JOIN (?P<channel>#.+)', response)
		if (regex):
			user = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('join', {'channel': regex.group('channel'), 'user': user})
			return
		# user left channel
		regex = match(re_user + r'PART (?P<channel>#.+)', response)
		if (regex):
			user = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('leave', {'channel': regex.group('channel'), 'user': user})
			return
		# PING
		regex = match(r'PING (?P<pong>.*)', response)
		if (regex):
			self.command_call('PONG ' + regex.group('pong'))
			return
		# channel invite
		regex = match(re_user + r'INVITE .+? :(?P<channel>#.+)', response)
		if (regex):
			user = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('invite', {'channel': regex.group('channel'), 'user': user})
			return
		# mode command
		regex = match(re_user + r'MODE (?P<channel>#.+) (?P<mode>.+?) (?P<user>.+?)', response)
		if (regex):
			user = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('mode', {'from': user, 'user': regex.group('user'), 'channel': regex.group('channel'), 'mode': regex.group('mode')})
			return
		# users command (issued when joining a channel)
		regex = match(r':.+? [\d]+ .+? [@=]{1} (?P<channel>#.+) :(?P<users>.+)', response)
		if (regex):
			events.call('users_response', {'channel': regex.group('channel'), 'users': regex.group('users').split(' ')})
			return
		# kicked from channel
		regex = match(re_user + r'KICK (?P<channel>#.+?) (?P<kicked>.+?) :(?P<message>.*)', response)
		if (regex):
			user = self.create_IrcUser(regex.group('nick'), regex.group('name'), regex.group('host'))
			events.call('kicked', {'kicked': regex.group('kicked'), 'message': regex.group('message'), 'kicker': user, 'channel': regex.group('channel')})
			return
		# unknown message
		#print(response)

	def run_one(self):
		''' Checks if the socket recieved some data '''
		try:
			self.buffer += self.irc.recv(512)
		except socket.error:
			pass
		if self.buffer != '':
			# debug
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

		# done here, because we want to prevent flooding
		self.iteration_counter += 1
		if self.iteration_counter >= 5:
			self.command_iteration()
			self.iteration_counter = 0

	def command_call(self, command, delay = False):
		''' Sends an IRC command '''
		if isinstance(command, unicode):
			command = command.encode('utf-8')
		if not delay:
			self.irc.send('%s\r\n' % command)
		else:
			self.commands.append(command)
	
	def command_iteration(self):
		if len(self.commands) > 0:
			command = self.commands.pop(0)
			self.irc.send('%s\r\n' % command)

	def connect_to_server(self, server, port = 6667):
		''' Connects to a IRC Server '''
		if PORT != '':
			port = PORT
		self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.irc.connect((server, port))
		self.irc.setblocking(0)
		self.command_call('NICK %s' % USERNAME)
		self.command_call('USER %s %d %d :%s' % (USERNAME, 0, 0, REALNAME))
		self.connected_to_server()

	def send_channel_message(self, channel, message, delay = False):
		''' Sends a message to a channel '''
		for line in message.split('\n'):
			# max message length of IRC = 512 (with \r\n)
			if len(line) > (MAX_MESSAGE_SIZE - 2):
				self.command_call('PRIVMSG %s :%s' % (channel, line[:(MAX_MESSAGE_SIZE - 2)]), delay)
				self.send_channel_message(line[(MAX_MESSAGE_SIZE - 1):])
			self.command_call('PRIVMSG %s :%s' % (channel, line), delay)
			if isinstance(channel, str) and channel.startswith('#'):
				# channel message
				self.notify_send_channel_message(channel, line)
			else:
				# private message
				self.notify_send_private_message(channel, line)
	
	def send_private_message(self, user, message, delay = False):
		self.send_channel_message(user, message, delay)

	def create_IrcUser(self, nickname, realname, host):
		user = IrcUser()
		user.nickname = nickname
		user.username = nickname
		user.realname = realname
		user.host     = host
		return user

