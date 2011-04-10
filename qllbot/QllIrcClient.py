#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, socket, asynchat, asyncore
from settings import *
from qllbot.QllClient import QllClient
from qllbot.IrcUser import IrcUser


class QllIrcClient(QllClient, asynchat.async_chat):
	def __init__(self):
		asynchat.async_chat.__init__(self)
		self.set_terminator('\n')
		self.buffer = ''
	
	def run(self):
		self.running()
	
	def collect_incoming_data(self, data):
		self.buffer += data
	
	def found_terminator(self):
		response = self.buffer.strip().split(' ', 3)
		if len(response) > 2:
			if response[1] == 'JOIN':
				self.notify_join(self.parse_user(response[0]), response[2][1:])
			elif response[1] == 'PRIVMSG':
				if response[2] == USERNAME:
					self.private_message(self.parse_user(response[0]), None, response[3][1:])
				else:
					self.channel_message(self.parse_user(response[0]), response[2], None, response[3][1:])
			elif response[1] == 'NOTICE':
				pass
			else:
				# debugstuff
				print 'Unknown command:\n %s\n' % (self.buffer)
		elif len(response) > 1:
			if response[0] == 'PING':
				self.command_call('PONG %s' % response[1])
		
		self.buffer = ''

	def run_one(self):
		''' Don't need this, because loop is asynchronous '''
		pass

	def command_call(self, command):
		self.send('%s\n' % command)
	
	def connect_to_server(self, server, port = 6667):
		if PORT != '':
			port = PORT
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connect((server, port))
		
		asyncore.loop()
	
	def handle_connect(self):
		''' Identifies the user to the server '''
		self.command_call('NICK %s' % USERNAME)
		self.command_call('USER %s %d %d :%s' % (USERNAME, 0, 0, REALNAME))
		self.connected_to_server()
	
	def handle_close(self):
		''' Starts the disconnected() event '''
		#self.disconnected('')
	
	def send_channel_message(self, channel, message):
		''' Sends a message to a channel '''
		for line in message.encode('utf-8').split('\n'):
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

