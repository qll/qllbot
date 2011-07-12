#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, resource

def daemonize():
	pid = os.fork()
	if pid != 0:
		# kill parent
		os._exit(0)
	
	os.setsid()
	
	# second child
	pid = os.fork()
	if (pid != 0):
		# kill first child
		os._exit(0)

	os.umask(0)
	
	# following code from activestate.com
	maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
	if (maxfd == resource.RLIM_INFINITY):
		maxfd = 1024

	 # iterate through and close all file descriptors.
	for fd in range(0, maxfd):
		try:
			os.close(fd)
		except OSError:
			pass
	
	if hasattr(os, 'devnull'):
		redirect_to = os.devnull
	else:
		redirect_to = '/dev/null'

	os.open(redirect_to, os.O_RDWR)	# standard input (0)

	os.dup2(0, 1)			# standard output (1)
	os.dup2(0, 2)			# standard error (2)

