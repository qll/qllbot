"""
Implements an event system with some kind of an Observer pattern.
"""


events = {}


class subscribe(object):
	def __init__(self, event):
		self.event = event

	def __call__(self, function):
		if self.event in events:
			events[self.event].append(function)
		else:
			events[self.event] = [function]
		return function


def call(event, param):
	if event in events:
		for function in events[event]:
			function(*param)

