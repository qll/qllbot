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
# REALNAME = 'qllbot'
# IDENT = 'qllbot'
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
DATABASE_FILE = 'storage/db.sqlite'
COMMAND_CHAR = '#'


DEBUG = True


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s-%(name)s]%(asctime)s: %(message)s',
            'datefmt': '%d.%m.%Y/%H:%S',
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
