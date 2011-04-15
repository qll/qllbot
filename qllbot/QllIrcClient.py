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
	
	def run(self):
		''' Starts the client '''
		self.running()
	
	def found_terminator(self, response):
		''' Interprets raw IRC commands '''
		response = response.strip().split(' ', 3)
		if len(response) > 2:
			if response[1] == 'JOIN':
				self.notify_join(self.parse_user(response[0]), response[2][1:])
			elif response[1] == 'PRIVMSG':
				if response[2] == USERNAME:
					self.private_message(self.parse_user(response[0]), None, response[3][1:])
				else:
					self.channel_message(self.parse_user(response[0]), response[2], None, response[3][1:])
			elif response[1] == 'INVITE':
				self.notify_invite(response[3][1:], response[3][1:], self.parse_user(response[0]))
		elif len(response) > 1:
			if response[0] == 'PING':
				self.command_call('PONG %s' % response[1])
		
		self.buffer = ''

	def run_one(self):
		''' Checks if the socket recieved some data '''
		try:
			self.buffer += self.irc.recv(512)
		except socket.error:
			pass
		if self.buffer != '':
			strings = self.buffer.split('\r\n')
			for string in strings:
				self.found_terminator(string)

	def command_call(self, command):
		''' Sends an IRC command '''
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

	def send_channel_message(self, channel, message):
		''' Sends a message to a channel '''
		for line in message.encode('utf-8').split('\n'):
			# max message length of IRC = 512 (with \r\n)
			if len(line) > 510:
				self.command_call('PRIVMSG %s :%s' % (channel, line[:510]))
				self.send_channel_message(line[511:])
			self.command_call('PRIVMSG %s :%s' % (channel, line))
			
	def parse_user(self, string):
		''' Tries to emulate something like the SilcUser object '''
		# cut ':'
		string = string[1:] 
		string = string.split('@')
		username = string[0].split('!~')
		user = IrcUser()
		user.username = username[0]
		user.nickname = username[0]
		user.realname = username[1]
		user.hostname = string[1]
		return user

