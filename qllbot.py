#!/usr/bin/env python3
"""
qllbot - An easy and SSL-capable IRC bot 

"""
import os
import lib.logging as log
import lib.core_events
from lib.irc import Client
from optparse import OptionParser
from lib.bot import Bot, UnknownCertException, InvalidCertException
from settings import *


def main():
	""" Bootstraps the bot. """
	try:
		options = get_options()
		if options.daemonize:
			daemonize()
		# change cwd to the directory of this file
		os.chdir(os.path.dirname(os.path.abspath(__file__)))
		# create files with 600 and dirs with 700 permissions (63 = 077)
		os.umask(63)
		if options.pid != None:
			write_pid_file(options.pid)
		log.set_up_logging()
		known_hosts = get_known_hosts()
		load_modules()
		bot = Bot()
		bot.init(NICKNAME, REALNAME, IDENT, PASSWORD, CHANNELS, SSL, CA_CERT)
		try:
			bot.connect(HOST, PORT, known_hosts)
		except InvalidCertException:
			log.system('Certificate does not match the one stored in the known_hosts file!')
			return
		except UnknownCertException as e:
			if options.daemonize:
				# since we can't ask when in daemonized mode, lets log this
				log.system('Unknown certificate for {} (SHA1-Fingerprint: {})'.format(HOST, e.sha1_fingerprint))
				return
			print('It seems as if you connect to this IRC server the first time.')
			print('Please verify these cryptographic fingerprints:\n')
			print('SHA1-Fingerprint: {0}'.format(e.sha1_fingerprint))
			print('MD5-Fingerprint:  {0}\n'.format(e.md5_fingerprint))
			print('Do you want to add the host to the list of known hosts and connect? (j/n)')
			if input().lower() != 'j':
				return
			known_hosts[HOST] = e.sha1_fingerprint
			add_known_host(HOST, e.sha1_fingerprint)
			bot.connect(HOST, PORT, known_hosts)
		if SSL:
			cipher = bot.irc.cipher()
			log.system('Connected with {} using {} to {}'.format(cipher[1], cipher[0], HOST))
		else:
			log.system('Connected to {}'.format(HOST))
		bot.loop()
	except KeyboardInterrupt:
		log.system('Recieved KeyboardInterrupt')
	except SystemExit:
		pass
	except:
		log.exception('Exception in main loop:')
	finally:
		log.system('Exiting...')


def get_options():
	""" Parses command line options and returns a dictionary containing the results. """
	parser = OptionParser()
	parser.add_option(
		'-d', '--daemonize',
		help = 'daemonize qllbot (fork it to a background process)',
		action = 'store_true',
		default = False
	)
	parser.add_option(
		'-p', '--pid',
		help = 'create file containing the process ID at the given path',
		default = None
	)
	return parser.parse_args()[0]


def daemonize():
	""" Forks the program to the background and closes all file descriptors. """
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


def fork():
	""" Forks and kills parent. """
	pid = os.fork()
	if pid > 0:
		os._exit(0)


def write_pid_file(path):
	""" Writes a file with the process ID to the file system. """
	with open(path, 'w') as f:
		f.write(str(os.getpid()))


def load_modules():
	for module in os.listdir('modules/'):
		if not module.startswith('_') and module.endswith('.py'):
			__import__('modules.{}'.format(module.split('.')[0]))


def get_known_hosts():
	""" Returns a dictionary of {host: fingerprint} mappings from the known_hosts file. """
	if not os.path.isfile(KNOWN_HOSTS_FILE):
		return {}
	with open(KNOWN_HOSTS_FILE, 'r') as f:
		return {l.split()[0]: l.split()[1] for l in f.readlines() if l.strip() != ''}


def add_known_host(host, fingerprint):
	""" Appends a new (host, fingerprint) pair to the known_hosts file. """
	with open(KNOWN_HOSTS_FILE, 'a') as f:
		f.write('{} {}\n'.format(host, fingerprint))


if __name__ == '__main__':
	main()
