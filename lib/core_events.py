import lib.logging as log
import lib.commands as commands
from lib.events import subscribe
from lib.bot import Bot
from lib.irc import User, Channel
from settings import OWNER, HOST, COMMAND_CHAR


bot = Bot()


# essential
@subscribe('ping')
def pong(code):
	bot.send('PONG ' + code)


# logging 
@subscribe('channel_message')
def log_message(sender, channel, message):
	log.message(sender, channel, message)

@subscribe('private_message')
def log_private_message(sender, message):
	log.message(sender, sender, message)

@subscribe('join')
def log_join_channel(user, channel):
	log.event('{0} joined channel {1}'.format(user, channel))

@subscribe('leave')
def log_leave_channel(user, channel):
	log.event('{0} left channel {1}'.format(user, channel))

@subscribe('quit')
def log_client_quit(user, message):
	log.event('{0} left the server ({1})'.format(user, message))

@subscribe('kicked')
def log_kicked(user, channel, kicked, message):
	log.event('{0} kicked {1} from {2}({3})'.format(user, kicked, channel, message))

@subscribe('topic')
def log_topic(user, channel, topic):
	log.event("{0} changed topic to '{1}' in {2}".format(user, topic, channel))


# code to keep track of channels and users
def create_channel(name):
	""" Creates channel if not already in channel list. """	
	if name not in bot.client.channels:
		bot.client.channels[name] = Channel(name)

@subscribe('join')
def add_user_to_channel(user, channel):
	create_channel(channel)
	bot.client.channels[channel].users[user.nickname] = user

@subscribe('leave')
def remove_user_from_channel(user, channel):
	if user.nickname == bot.client.nickname:
		# bot left channel
		bot.client.channels.pop(channel)
	else:
		bot.client.channels[channel].remove_user(user)

@subscribe('kicked')
def kicked_user_from_channel(user, channel, kicked, message):
	remove_user_from_channel(user, channel)

@subscribe('quit')
def remove_user_from_all_channels(user, message):
	for name, channel in bot.client.channels.items():
		channel.remove_user(user)

@subscribe('mode')
def recheck_user_role(user, channel, mode, receiver):
	if '+o' in mode and receiver not in bot.client.channels[channel].ops:
		bot.client.channels[channel].ops.append(receiver)
	elif '-o' in mode and receiver in bot.client.channels[channel].ops:
		bot.client.channels[channel].ops.remove(receiver)
	elif '+v' in mode and receiver not in bot.client.channels[channel].voiced:
		bot.client.channels[channel].voiced.append(receiver)
	elif '-v' in mode and receiver in bot.client.channels[channel].voiced:
		bot.client.channels[channel].voiced.remove(receiver)

@subscribe('join_users')
def add_all_users_from_channel(channel, users):
	create_channel(channel)
	for user in users.split(' '):
		is_op = True if '@' in user else False
		is_voiced = True if '+' in user else False
		if is_op or is_voiced:
			user = user[1:]
		bot.client.channels[channel].users[user] = User(user)
		if is_op:
			bot.client.channels[channel].ops.append(user)
		if is_voiced:
			bot.client.channels[channel].voiced.append(user)

@subscribe('topic')
def topic_changed(user, channel, topic):
	create_channel(channel)
	bot.client.channels[channel].topic = topic

@subscribe('join_topic')
def parse_topic(channel, topic):
	create_channel(channel)
	bot.client.channels[channel].topic = topic


# behaviour
@subscribe('invite')
def join_invited_channel(user, channel):
	""" Joins channel on owner invite. """
	if user.nickname == OWNER:
		bot.client.join(channel)

@subscribe('nickname_in_use')
def modify_nickname():
	log.event('Nickname already in use')
	bot.disconnect()


# commands
@subscribe('channel_message')
def check_for_command(sender, channel, message):
	if sender.nickname == bot.client.nickname:
		return
	if message.startswith(COMMAND_CHAR):
		commands.set_sender(sender)
		commands.set_channel(channel)
		commands.is_pm = False
		command = message[1:].strip().split(' ', 1)
		if len(command) > 1:
			output = commands.execute_command(sender, command[0], command[1])
		else:
			output = commands.execute_command(sender, command[0])
		if output:
			bot.client.say(channel, output)

@subscribe('private_message')
def check_for_pm_command(sender, message):
	if sender.nickname == bot.client.nickname:
		return
	if message.startswith(COMMAND_CHAR):
		commands.set_pm_sender(sender)
		commands.is_pm = True
		command = message[1:].strip().split(' ', 1)
		if len(command) > 1:
			output = commands.execute_pm_command(sender, command[0], command[1])
		else:
			output = commands.execute_pm_command(sender, command[0])
		if output:
			bot.client.pm(sender, output)
