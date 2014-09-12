#!/usr/bin/env python3
"""qllbot - A SSL-capable IRC bot with focus on easy module development.

Written by qll (github.com/qll), distributed under the BSD 2-Clause License.
"""
import argparse
import settings
import lib.bot
import logging
import logging.config
import os


def do_daemonize():
    """Forks the program to the background and closes all file descriptors."""
    fork()
    os.setsid()
    fork()
    # close file descriptors
    for fd in range(3):
        try:
            os.close(fd)
        except OSError:
            pass
    # open /dev/null as filedescriptor
    os.open(os.devnull, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)


def write_pid_file(path):
    """Writes a file with the process ID to the file system."""
    with open(path, 'w') as f:
        f.write(str(os.getpid()))


def load_modules():
    """Imports all modules from the modules directory."""
    for module in os.listdir('modules/'):
        if not module.startswith('_') and module.endswith('.py'):
            __import__('modules.{}'.format(module.split('.')[0]))


def read_known_hosts():
    """Reads {host: hash} mappings from the known_hosts file."""
    try:
        if not os.path.isfile(settings.KNOWN_HOSTS_FILE):
            return {}
        with open(settings.KNOWN_HOSTS_FILE, 'r') as f:
            lines = f.read().strip().split('\n')
            return {line.split()[0]: line.split()[1] for line in lines}
    except AttributeError:
        return {}


def _add_setting(dict_, key):
    """Adds a setting to the dict_ if it exists."""
    try:
        dict_[key.lower()] = getattr(settings, key)
    except AttributeError:
        pass


def main(daemonize=False, pid=None):
    if daemonize:
        do_daemonize()
    if pid is not None:
        write_pid_file(pid)

    # change cwd to the director of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # create files with 600 and dirs with 700 permissions
    os.umask(63)

    logging.config.dictConfig(settings.LOGGING)
    log = logging.getLogger(__name__)

    load_modules()

    bot_args = {'known_hosts': read_known_hosts()}
    _add_setting(bot_args, 'PORT')
    _add_setting(bot_args, 'USE_SSL')
    _add_setting(bot_args, 'ENCODING')
    _add_setting(bot_args, 'CA_CERTS')
    bot = lib.bot.Bot(settings.HOST, **bot_args)

    log.info('Starting the bot.')
    try:
        bot.loop()
    except KeyboardInterrupt:
        log.info('Received KeyboardInterrupt.')
    except:
        log.exception('Exception in main loop:')
    finally:
        log.info('Exiting...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--daemonize', default=False,
                        action='store_true',
                        help='fork to a background process')
    parser.add_argument('-p', '--pid', default=None,
                        help='create file with the process ID at given path')
    main(**vars(parser.parse_args()))
