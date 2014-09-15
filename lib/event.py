"""Implements an event system.

A list of possible events with their parameters follows:

Event Name      | Arguments
==========================================
connected       | bot=lib.bot.Bot
new_db          | db=sqlite3.Connection
raw_message     | bot=lib.bot.Bot, msg=str
watchdog_tick   | bot=lib.bot.Bot

All IRC events (found in irc.py _irc_regex) receive a lib.bot.Bot instance as
the first parameter and their regular expression groups (in order) as the next
parameters.
"""


_events = {}  # globally holds all event listeners


class subscribe(object):
    """Decorator to subscribe to an event. Usage: @subscribe('event_name')."""

    def __init__(self, event):
        self.event = event

    def __call__(self, function):
        _events.setdefault(self.event, []).append(function)
        return function


def call(event, kwargs={}):
    """Execute all event listeners of the specified event."""
    if event in _events:
        for function in _events[event]:
            function(**kwargs)
