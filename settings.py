"""qllbot settings file.

Edit this file to make qllbot suit your needs :-)
"""


# connection details
HOST = 'chat.freenode.net'
PORT = 7000  # default: 6667
USE_SSL = True  # default: False

# if you specify the path of the CA certificates, they will be used to verify
# the SSL connection
CA_CERTS = None


# bot nickname
NICKNAME = 'qllbot'

# the owner is able to control the bot
OWNER = 'qll'


# which channels should the bot join on connect
CHANNELS = {
    # channels of the form '#chan': 'password',
    '#qllbottest': '',
}


# message encoding
ENCODING = 'utf-8'

# paths
KNOWN_HOSTS_FILE = 'storage/known_hosts'
DATABASE_FILE = 'storage/db.sqlite'

# prefix char for commands
COMMAND_CHAR = '#'


# https://docs.python.org/3.4/library/logging.config.html for details
LOGGING = {
    'version': 1,
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
        # this probably is what you'd want in a daemonized setting:
        # 'file': {
        #     'level': 'INFO',
        #     'class': 'logging.FileHandler',
        #     'filename': 'storage/bot.log',
        #     'formatter': 'standard'
        # }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
