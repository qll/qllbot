import lib.cmd
import lib.event
import lib.irc
import logging
import settings


_log = logging.getLogger(__name__)


# connection event handlers
@lib.event.subscribe('connected')
def auth_to_server(bot=None):
    if settings.PASSWORD:
        _log.debug('Sending server password.')
        bot.send(lib.irc.password(settings.PASSWORD))


@lib.event.subscribe('connected')
def identify(bot=None):
    _log.info('Identifying as %s.' % settings.NICKNAME)
    bot.send(lib.irc.identify(settings.NICKNAME, settings.HOST))


@lib.event.subscribe('connected')
def join_channels(bot=None):
    for channel, password in settings.CHANNELS.items():
        _log.debug('Joining %s.' % channel)
        bot.send(lib.irc.join(channel, password))


@lib.event.subscribe('nickname_in_use')
def modify_nickname(bot=None):
    """Append underscores if the nickname is already in use."""
    settings.NICKNAME = '%s_' % settings.NICKNAME
    _log.warning('Nickname already in use. Trying %s.' % settings.NICKNAME)
    identify(bot)
    join_channels(bot)


# watchdog routines
WATCHDOG_THRESHOLD = 120  # after how many ticks will a ping be sent out?
_watchdog_counter = 0
_ping_sent = False  # True when a watchdog ping was sent out


@lib.event.subscribe('raw_message')
def reset_watchdog_counter(bot=None, msg=None):
    """When receiving messages from the server we can reset the watchdog."""
    global _watchdog_counter
    _watchdog_counter = 0


@lib.event.subscribe('ping')
def answer_ping(bot=None, code=''):
    """Answer the server's PINGs."""
    bot.send(lib.irc.pong(code))


@lib.event.subscribe('watchdog_tick')
def send_watchdog_ping(bot=None):
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


@lib.event.subscribe('pong')
def receive_watchdog_pong(bot=None, code=''):
    """The received PONG answers our watchdog PING."""
    global _watchdog_counter, _ping_sent
    _log.debug('Received watchdog pong.')
    _ping_sent = False


# IRC message parsing and event generation

@lib.event.subscribe('raw_message')
def parse_raw_msg(bot=None, msg=None):
    event, kwargs = lib.irc.parse(msg)
    if event is None:
        _log.debug('Unknown message: %s' % msg)
        return
    _log.debug('Calling IRC event: %s.' % event)
    kwargs['bot'] = bot
    try:
        lib.event.call(event, kwargs=kwargs)
    except Exception:
        _log.exception('Exception in event handler for event %s:' % event)


# command invocation

@lib.event.subscribe('channel_message')
@lib.event.subscribe('private_message')
def invoke_command(bot=None, msg=None):
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
