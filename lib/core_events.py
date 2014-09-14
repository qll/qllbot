import lib.cmd
import lib.events
import lib.irc
import logging
import settings


_log = logging.getLogger(__name__)


# connection event handlers

@lib.events.subscribe('connected')
def identify(bot):
    _log.info('Identifying as %s.' % settings.NICKNAME)
    bot.send(lib.irc.identify(settings.NICKNAME, settings.HOST))


@lib.events.subscribe('connected')
def join_channels(bot):
    for channel, password in settings.CHANNELS.items():
        _log.debug('Joining %s.' % channel)
        bot.send(lib.irc.join(channel, password))


@lib.events.subscribe('nickname_in_use')
def modify_nickname(bot=None):
    """Append underscores if the nickname is already in use."""
    settings.NICKNAME = '%s_' % settings.NICKNAME
    _log.warning('Nickname already in use. Trying %s.' % settings.NICKNAME)
    identify(bot)
    join_channels(bot)


# watchdog routines
WATCHDOG_THRESHOLD = 60  # after how many ticks will a ping be sent out?
_watchdog_counter = 0
_ping_sent = False  # True when a watchdog ping was sent out


@lib.events.subscribe('raw_message')
def reset_watchdog_counter(bot, msg):
    """When receiving messages from the server we can reset the watchdog."""
    global _watchdog_counter
    _watchdog_counter = 0


@lib.events.subscribe('ping')
def answer_ping(bot=None, code=''):
    """Answer the server's PINGs."""
    bot.send(lib.irc.pong(code))


@lib.events.subscribe('watchdog_tick')
def send_watchdog_ping(bot):
    """If no activity was measured for a long enough time, we send a PING."""
    global _watchdog_counter, _ping_sent
    _watchdog_counter += 1
    if _watchdog_counter > WATCHDOG_THRESHOLD:
        _watchdog_counter = 0
        if _ping_sent:
            _log.warning('Watchdog pong not received! Reconnecting.')
            bot.reconnect()
            _ping_sent = False
        else:
            _log.debug('Sending watchdog ping.')
            bot.send(lib.irc.ping('alive'))
            _ping_sent = True


@lib.events.subscribe('pong')
def receive_watchdog_pong(bot=None, code=''):
    """The received PONG answers our watchdog PING."""
    global _watchdog_counter, _ping_sent
    _log.debug('Received watchdog pong.')
    _ping_sent = False


# IRC message parsing and event generation

@lib.events.subscribe('raw_message')
def parse_raw_msg(bot, msg):
    event, kwargs = lib.irc.parse(msg)
    if event is None:
        _log.debug('Unknown message: %s' % msg)
        return
    _log.debug('Calling IRC event: %s.' % event)
    kwargs['bot'] = bot
    lib.events.call(event, kwargs=kwargs)


# command invocation

@lib.events.subscribe('channel_message')
@lib.events.subscribe('private_message')
def invoke_command(bot=None, msg=None, priv_msg=None):
    if priv_msg is not None:
        msg = priv_msg
    if msg.sender.nick == settings.NICKNAME:
        return
    msg = lib.cmd.CommandMessage(msg, settings.COMMAND_CHAR)
    if msg.is_command():
        _log.debug('Trying to invoke the %s command (private: %s).' %
                   (msg.cmd, msg.private))
        msg.bot = bot
        try:
            output = lib.cmd.execute(msg.cmd, msg, private=msg.private)
        except Exception:
            _log.exception('Exception in command %s:' % msg.cmd)
            output = 'Well done - an exception occured! It was logged.'
        if output:
            response = (lib.irc.say_to(msg.sender, output) if msg.private else
                        lib.irc.say(msg.channel, output))
            bot.send(response)
