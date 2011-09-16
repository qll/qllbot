#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time, re
from qllbot.Registry import *


def get_time(param):
	''' Returns current date and time in following format: dayname, day.month.year, hour:minute:second.
You can supply your own format with: #time [format] (e.g. #time  d.%m.%Y -> 15.03.2011) '''
	if param == '':
		return time.strftime('%A, %d.%m.%Y, %H:%M:%S', time.localtime())
	return time.strftime(param, time.localtime())

def say(param):
	''' Echoes the given string (#say [text] -> [text]). '''
	return param


add_command('time', get_time)
add_command('say', say)

