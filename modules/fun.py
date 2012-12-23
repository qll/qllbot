import random
import re
from random import randint, choice
from lib.bot import Bot
from lib.commands import command, pm_command, get_channel


ZOR_MAX = 4719


@command(alias=['zor'])
@pm_command(alias=['zor'])
def z0r(param):
	""" Returns random z0r.de link. """
	return 'http://z0r.de/{}'.format(random.randint(1, ZOR_MAX))


@command()
@pm_command()
def yesno(param):
	""" Answers yes or no to a question. """
	if random.randint(1, 10) >= 5:
		return 'yes.'
	else:
		return 'no.'


@command()
def who(param):
	""" #who wants help for this command? """
	if param == '':
		return
	param = ' {} '.format(param)
	replacements = {'me': 'you', 'my': 'your', 'mine': 'yours'}
	for a, b in replacements.items():
		# actually fails at "me you", but I don't want to think 'bout that right now :-/
		param = re.sub(
			r' ({}|{})(\?| )'.format(a, b),
			lambda m: ' {}{}'.format(b if m.group(1) == a else a, m.group(2)),
			param
		)
	param = param.replace('?', choice(('!', '.')))
	users = Bot().client.channels[get_channel()].users
	user = users[choice(list(users.keys()))]
	return '{} {}'.format(user, param[1:-1])
	
