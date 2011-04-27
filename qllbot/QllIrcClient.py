#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, socket
from settings import *
from qllbot.QllClient import QllClient
from qllbot.IrcUser import IrcUser


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
		''' Interprets raw IRC commands '''
		response = response.strip().split(' ', 3)
		if len(response) > 2:
		
			if response[1] == 'JOIN':
				self.notify_join(self.parse_user(response[0]), response[2][1:])
			elif response[1] == 'PART':
				self.notify_leave(self.parse_user(response[0]), response[2])
			elif response[1] == 'PRIVMSG':
				if len(response) < 4:
					print('Error in PRIVMSG')
					return
				if response[2] == USERNAME:
					self.private_message(self.parse_user(response[0]), None, response[3][1:])
				else:
					self.channel_message(self.parse_user(response[0]), response[2], None, response[3][1:])
			elif response[1] == 'INVITE':
				self.notify_invite(response[3][1:], response[3][1:], self.parse_user(response[0]))
			elif len(response) > 3 and (response[3].startswith('@') or response[3].startswith('=')):
				additional = response[3][2:].split(' ', 1)
				users      = additional[1][1:].split(' ')
				self.notify_users_response(additional[0], users)
				
		elif len(response) > 1:
			if response[0] == 'PING':
				self.command_call('PONG %s' % response[1])

	def run_one(self):
		''' Checks if the socket recieved some data '''
		try:
			self.buffer += self.irc.recv(512)
		except socket.error:
			pass
		if self.buffer != '':
			# debug
		    #print(self.buffer)
			
			strings = self.buffer.split('\r\n')
			
			# buffer unfinished messages
			if strings[len(strings) - 1] != '':
				self.buffer = strings.pop()
			else:
				self.buffer = ''
				
			for string in strings:
				try:
					string = string.decode('utf-8', 'replace')
				except UnicodeDecodeError:
					print('Error: UnicodeDecodeError')
				self.found_terminator(string)

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
			if len(line) > 510:
				self.command_call('PRIVMSG %s :%s' % (channel, line[:510]), delay)
				self.send_channel_message(line[511:])
			self.command_call('PRIVMSG %s :%s' % (channel, line), delay)
			if isinstance(channel, str) and channel.startswith('#'):
				# channel message
				self.notify_send_channel_message(channel, line)
			else:
				# private message
				self.notify_send_private_message(channel, line)
	
	def send_private_message(self, user, message, delay = False):
		self.send_channel_message(user, message, delay)

	def parse_user(self, string):
		''' Tries to emulate something like the SilcUser object '''
		# cut ':'
		string = string[1:] 
		string = string.split('@')
		username = string[0]
		realname = ''
		if '!~' in username:
			username = username.split('!~')
			realname = username[1]
			username = username[0]
		user = IrcUser()
		user.username = username
		user.nickname = username
		user.realname = realname
		user.hostname = string[1]
		return user

