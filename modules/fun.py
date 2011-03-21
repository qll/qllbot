#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from qllbot.Registry import *


def get_z0r(param):
	''' Returns random z0r.de link. '''
	return 'http://z0r.de/%d' %  random.randint(1, 2668)

def answer_yesno(param):
	''' Answers yes or no to a question. '''
	if random.randint(1, 10) >= 5:
		return 'yes.'
	else:
		return 'no.'

add_command('z0r', get_z0r)
add_command('zor', get_z0r)
add_command('yesno', answer_yesno)
