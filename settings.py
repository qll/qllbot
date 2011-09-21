#!/usr/bin/env python
# -*- coding: utf-8 -*-

PROTOCOL = 'IRC'                       # SILC or IRC

USERNAME = 'qllbot'                    # useraccount of the bot
REALNAME = 'qllbot'                    # real name of the bot
PASSWORD = ''                          # password of the bot useraccount
OWNER    = 'qll'                       # username of the bot admin

SERVER           = 'irc.freenode.net'  # Server address
PORT             = ''                  # leave blank if you don't know (just for IRC)
CHANNELS         = {                   # channels to connect to {'NAME': 'PASSWORD', ...}
	'#qllbottest': '',
}

AUTO_OP_OWNER    = True                # if the bot gains sufficient rights +o the owner
SEND_KEEP_ALIVE  = False               # Default: False. Some networks with with NAT
                                       # require a socket to send data like every 20 seconds.
                                       # Use this, if you get "silent" disconnects.

MODULES = (                            # loaded modules (can be found in ./modules)
	'core',
	'basic',
	'admin',
	'internet',
	'youtube',
	'fun',
	'usercommands',
	'history',
	'feeds'
)

COMMAND_TOKEN = '#'                    # marks a command (default: #)

LOGGER = 'ConsoleLogger'               # Currently you have following choices of Loggers:
                                       # DummyLogger, ConsoleLogger, DbLogger
DB_LOGGER_CONSOLE  = True              # if you use DbLogger this enables console output, too

LOG_TIME_FORMAT    = '%H:%M:%S'
LOG_MESSAGE_FORMAT = '[%(channel)s %(time)s] %(username)s: %(message)s'
LOG_EVENT_FORMAT   = '* [%(time)s] %(event)s'


CACHE         = 'cache'                # cache directory
PUBKEY_PATH   = '%s/silc.pub' % CACHE  # public key file path (for SILC)
PRIVKEY_PATH  = '%s/silc.prv' % CACHE  # private key file path (for SILC)
DATABASE_PATH = '%s/db.sqlite' % CACHE # path to database (will be created if it does not exist)

VERSION  = '0.6.6'
GREETING = 'qllbot v%s' % VERSION      # message sent when bot joins channel
DEBUG    = False                       # print all socket messages to the console

### MODULES ###
# internet
WEATHER_LOCATION   = 'Bochum'          # default weather location (if #weather gets no parameters)
WEATHER_IN_CELSIUS = True              # converts #weather results in °C
GOOGLE_MAX_RESULTS = 3                 # displayed google results
# fun
ZOR_MAX = 3411                         # Highest known z0r.de id
# usercommands
USERCOMMANDS_TOKEN = '!'               # marks a usercommand
# feeds
NEWS_RESULTS = 3                       # maximum news results
NEWS_FEEDS = {                         # allowed feeds with key (for #feed or #news command)
	'faz':      'http://www.faz.net/s/Rub/Tpl~Epartner~SRss_~Ahomepageticker~E1.xml',
	'zeit':     'http://newsfeed.zeit.de/index',
	'spiegel':  'http://www.spiegel.de/index.rss',
	'bbc':      'http://feeds.bbci.co.uk/news/rss.xml',
	'aje':      'http://english.aljazeera.net/Services/Rss/?PostingId=2007731105943979989',
	'guardian': 'http://feeds.guardian.co.uk/theguardian/rss'
}
