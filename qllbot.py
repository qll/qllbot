#!/usr/bin/env python3
"""qllbot - A SSL-capable IRC bot with focus on easy module development.

Written by qll (github.com/qll), distributed under the BSD 2-Clause License.
"""
import argparse
import settings
import lib.bot
import lib.core_events
import logging
import logging.config
import os
import ssl
import sys


def do_daemonize():
    """Fork the program to the background and closes all file descriptors."""
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
    """Write a file with the process ID to the file system."""
    with open(path, 'w') as f:
        f.write(str(os.getpid()))


def load_modules():
    """Imports all modules from the modules directory."""
    for module in os.listdir('modules/'):
        if not module.startswith('_') and module.endswith('.py'):
            __import__('modules.{}'.format(module.split('.')[0]))


def read_known_hosts():
    """Read {host: hash} mappings from the known_hosts file."""
    try:
        if not os.path.isfile(settings.KNOWN_HOSTS_FILE):
            return {}
        with open(settings.KNOWN_HOSTS_FILE, 'r') as f:
            lines = f.read().strip().split('\n')
            return {line.split()[0]: line.split()[1] for line in lines}
    except AttributeError:
        return {}


def _add_setting(dict_, key):
    """Add a setting to the dict_ if it exists."""
    try:
        dict_[key.lower()] = getattr(settings, key)
    except AttributeError:
        pass


def append_known_host(host, hash_):
    """Append a new (host, hash) pair to the known_hosts file."""
    with open(settings.KNOWN_HOSTS_FILE, 'a') as f:
        f.write('{} {}\n'.format(host, hash_))


def main(daemonize=False, pid=None):
    """Bootstrap all parts of the qllbot and start the main loop."""
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

    log.debug('Loading all modules.')
    load_modules()

    log.debug('Loading known_hosts file and setting bot configuration.')
    bot_args = {'known_hosts': read_known_hosts()}
    _add_setting(bot_args, 'PORT')
    _add_setting(bot_args, 'USE_SSL')
    _add_setting(bot_args, 'ENCODING')
    _add_setting(bot_args, 'CA_CERTS')

    running = False
    while not running:
        log.info('Starting the bot.')
        bot = lib.bot.Bot(settings.HOST, **bot_args)
        try:
            running = True
            bot.loop()
        except lib.bot.UnknownCertError as e:
            if daemonize:
                log.error('Unknown certificate for %s (SHA512-Hash: %s).' %
                          (e.host, e.sha512_hash))
                sys.exit(1)
            print('It seems as if you connect to this IRC the first time.')
            print('Please verify these cryptographic hashes manually:\n')
            print('SHA512-Hash: %s' % e.sha512_hash)
            print('SHA1-Hash: %s\n' % e.sha1_hash)
            decision = input('Do you want to add the host to the list of known'
                             ' hosts and connect (j/n)? ').lower()
            if decision != 'j':
                return
            bot_args['known_hosts'][settings.HOST] = e.sha512_hash
            append_known_host(settings.HOST, e.sha512_hash)
            running = False  # go back to the while loop
        except ssl.CertificateError as e:
            log.error(str(e))
        except KeyboardInterrupt:
            log.debug('Received KeyboardInterrupt.')
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
