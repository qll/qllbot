""" Test cases for the fun module. """
import re
import modules.fun
from lib.bot import Bot
from lib.commands import get_channel
from unittest import TestCase


class WhoCommandTestCase(TestCase):
	def setUp(self):
		self.possible_users = Bot().client.channels[get_channel()].users.keys()

	def test_sentence(self):
		self.assertTrue(
			re.match(
				r'({0}) stole your pants(\.|!)'.format('|'.join(self.possible_users)),
				modules.fun.who('stole my pants?')
			)
		)
	
	def test_substitutions(self):
		self.assertEqual(modules.fun.who('me').split()[1], 'you')
		self.assertEqual(modules.fun.who('you').split()[1], 'me')
		self.assertEqual(modules.fun.who('your').split()[1], 'my')
		self.assertEqual(modules.fun.who('my').split()[1], 'your')
		self.assertEqual(modules.fun.who('mine').split()[1], 'yours')
		self.assertEqual(modules.fun.who('yours').split()[1], 'mine')
	
	def test_twokeywords(self):
		self.assertEqual(
			modules.fun.who('thinks my pants like you').split(' ', 1)[1],
			'thinks your pants like me'
		)
	
	def test_criticalword(self):
		self.assertEqual(
			# every word contains me
			modules.fun.who('game meeting atmega').split(' ', 1)[1],
			'game meeting atmega'
		)
	
