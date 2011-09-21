#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from settings import *

class Logger():
	def get_current_time(self):
		return time.strftime(LOG_TIME_FORMAT, time.localtime())
