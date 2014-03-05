"""
qllbot settings file

Edit this file to make qllbot suit your needs... :-)
"""

HOST = 'chat.freenode.net'	# Server address
PORT = 7000					# Port of the IRC service
SSL  = True					# Enable SSL?

NICKNAME = 'qllbot'	# Nickname of the bot
REALNAME = 'qllbot'	# Realname of the bot
IDENT    = 'qllbot'	# Identifier of qllbot
PASSWORD = ''		# Password of the bot useraccount (if given, the bot will make an attempt to identify with NickServ)
OWNER    = 'qll'	# Nickname of the bot owner (for administrative commands)
COMMAND_CHAR = '#'	# Char which prefixes all commands 

CHANNELS = {		# Channels of the form {'name': 'password'}
	'#qllbottest': '',
}

# The following two options are only relevant if SSL is enabled.
# You have two choices to identify the IRC server:
# - If you want to use a CA certificate to check the SSL connection's certificate,
#   insert the path to the CA certificate in CA_CERT.
# - If you do not want to use a CA certificate, leave CA_CERT empty. qllbot is
#   able to remember the SHA1-Fingerprint of the certificate the server responds
#   with when you connect the first time. It will be stored as a (Host,
#   SHA1-Fingerprint) Tuple in the known_hosts file. If the certificate ever
#   changes qllbot will raise an InvalidCertException.
CA_CERT = None	# Path to PEM-encoded certificate file or None
KNOWN_HOSTS_FILE = 'storage/known_hosts'

DEBUG        = False						# In debug mode developer informations will be logged
LOG_TO_FILE  = False						# Log to file?
LOG_FILE     = 'storage/qllbot.log'			# Path to the log file
LOG_MESSAGES = 2							# Log chat messages: 0 no, 1 yes, 2 only to console
LOG_EVENTS   = 2							# Log events like join, leave: 0 no, 1 yes, 2 only to console
LOG_SYSTEM   = 2							# Log events like connect, disconnect: 0 no, 1 yes, 2 only to console
LOG_MSG_FMT  = '[{time}][{channel}] {nick}: {message}'	# log format for messages
LOG_EVNT_FMT = '* [{time}] {event}'			# log format for events
LOG_SSTM_FMT = '! [{time}] {event}'			# log format for system events
LOG_TIME_FMT = '%d.%m.%Y %H:%M:%S'			# strftime format of log entries

ENCODING = 'utf-8'	# encoding the bot should use for incoming and outgoing messages


# Possibility to overwrite all settings with a local settings file.
import os.path
if os.path.isfile('local_settings.py'):
	from local_settings import *

