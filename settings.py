"""qllbot settings file.

Edit this file to make qllbot suit your needs :-)
"""


# connection details
HOST = 'chat.freenode.net'
PORT = 7000  # default: 6667
USE_SSL = True  # default: False


CA_CERTS = None


# bot identity details
NICKNAME = 'qllbot'
REALNAME = 'qllbot'
IDENT = 'qllbot'
PASSWORD = ''
OWNER = 'qll'
COMMAND_CHAR = '#'


# which channels should the bot join on connect
CHANNELS = {
    # channels of the form '#chan': 'password',
    '#qllbottest': '',
}


# rarely touched settings
ENCODING = 'utf-8'
KNOWN_HOSTS_FILE = 'storage/known_hosts'


DEBUG = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
