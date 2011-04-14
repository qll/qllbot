#!/usr/bin/env python
# -*- coding: utf-8 -*-

PROTOCOL = 'IRC'                       # SILC or IRC

USERNAME = 'qllguy'                    # useraccount of the bot
REALNAME = 'qllguy'                    # real name of the bot
PASSWORD = '1337password1337'          # password of the bot useraccount
OWNER    = 'qll'                       # username of the bot admin

SERVER           = 'irc.freenode.net'  # Server address
PORT             = ''                  # leave blank if you don't know (just for IRC)
CHANNELS         = {                   # channels to connect to {'NAME': 'PASSWORD', ...}
	'#qllbottest': '',
}
CHANNEL_PASSWORD = ''                  # channel password

SEND_KEEP_ALIVE  = False               # Default: False. Some network configurations
                                       # require the bot to send data every 20 seconds.
                                       # Use this, if you get "silent" disconnects.

MODULES = (                            # loaded modules (can be found in ./modules)
	'core',
	'basic',
	'internet',
	'youtube',
	'fun',
	'usercommands',
	'feeds'
)

COMMAND_TOKEN = '#'                    # marks a command (default: #)

LOG_MESSAGE_FORMAT = '[%s %s] %s: %s'  # (channelname, time, username, message)
LOG_EVENT_FORMAT   = '* [%s] %s'       # (time, message)

CACHE         = 'cache'                # cache directory
PUBKEY_PATH   = '%s/silc.pub' % CACHE  # public key file path (for SILC)
PRIVKEY_PATH  = '%s/silc.prv' % CACHE  # private key file path (for SILC)
DATABASE_PATH = '%s/db.sqlite' % CACHE # path to database (will be created if it does not exist)

VERSION  = '0.4.1'
GREETING = 'qllbot v%s' % VERSION      # message sent when bot joins channel

### MODULES ###
# internet
WEATHER_LOCATION   = 'Bochum'          # default weather location (if #weather gets no parameters)
WEATHER_IN_CELSIUS = True              # converts #weather results in °C
GOOGLE_MAX_RESULTS = 3                 # displayed google results
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
