"""Implements an event system."""


_events = {}  # globally holds all event listeners


class subscribe(object):
    """Decorator to subscribe to an event. Usage: @subscribe('event_name')."""

    def __init__(self, event):
        self.event = event

    def __call__(self, function):
        _events.setdefault(self.event, []).append(function)
        return function


def call(event, params):
    """Executes all event listeners of the specified event."""
    if event in _events:
        for function in _events[event]:
            function(*params)
