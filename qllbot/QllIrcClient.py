#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
from settings import *
from qllbot.Registry import *
from qllbot.QllClient import QllClient
from qllbot.IrcUser import IrcUser


registry = Registry()

# todo: implement with asyncore.asynchat
class QllIrcClient(QllClient):

	irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __init__(self):
		self.running()
	
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

	def run_one(self):
		response = self.irc.recv(500)
		#print response
		response = response.strip().split(' ', 3)
		if len(response) > 2:
			if response[1] == 'JOIN':
				self.notify_join(self.parse_user(response[0]), response[2][1:])
			elif response[1] == 'PRIVMSG':
				if response[2] == USERNAME:
					self.private_message(self.parse_user(response[0]), None, response[3][1:])
				else:
					self.channel_message(self.parse_user(response[0]), response[2], None, response[3][1:])
		elif len(response) > 1:
			if response[0] == 'PING':
				self.command_call('PONG %s' % response[1])

	def command_call(self, command):
		self.irc.send('%s\n' % command)

	def connect_to_server(self, server):
		defaultPort = 6667
		if PORT != '':
			defaultPort = PORT
		self.irc.connect((server, defaultPort))
		self.command_call('NICK %s' % USERNAME)
		self.command_call('USER %s %d %d :%s' % (USERNAME, 0, 0, USERNAME))
		self.connected()
	
	def send_channel_message(self, channel, message):
		for line in message.encode('utf-8').split('\n'):
			self.command_call('PRIVMSG %s :%s' % (channel, line))

