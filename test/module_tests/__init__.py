#!/usr/bin/env python
# coding: utf-8
import sys
sys.path.append('../')
from lib.bot import Bot
from lib.irc import Channel, User
from lib.commands import set_channel, set_sender, set_pm_sender


# setup for all tests
bot = Bot()
bot.init('qllbot', 'qllbot', 'qllbot', 'password', {}, True, None, 'utf-8')
channel1 = Channel('channel1', 'topic')
chuck = User('opuser', 'chuck', 'norris.com')
channel1.users = {
	'user': User('user', 'user', 'site.com'),
	'opuser': chuck,
	'voiceduser': User('voiceduser', 'chuck', 'testa.com'),
}
channel1.ops.append('opuser')
channel1.voiced.append('voiceduser')
channel2 = Channel('channel2', 'topic')
channel2.users = {
	'bob': User('bob', 'bobby', 'hostname.com'),
	'mary': User('mary', 'mary', 'site.com'),
	'chuck': User('chuck', 'chuck', 'norris.com'),
}
bot.client.channels = {'channel1': channel1, 'channel2': channel2}
set_channel('channel1')
set_sender(chuck)
set_pm_sender(chuck)
del channel1, channel2, bot

