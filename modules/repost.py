import lib.cmd
import lib.irc
import re
import contextlib
import random


LINK_RE = re.compile(r'https?://[^ ]+')
_report_msgs = [
    'OMG %s! Repost! %s was faster.',
    'Much repost. Such %s. Very wow %s',
    'Too slow, %s! %s already posted this :P',
]


@lib.event.subscribe('new_db')
def create_repost_schema(db=None):
    """Creates the repost SQLite schema."""
    db.execute('CREATE TABLE repost_track (link TEXT PRIMARY KEY, user TEXT)')
    db.commit()


@lib.event.subscribe('channel_message')
def track_links(bot=None, msg=None):
    """Checks every message for unclickable links and makes them clickable."""
    matches = LINK_RE.finditer(' %s ' % msg.content)
    with contextlib.closing(bot.db.cursor()) as c:
        for match in matches:
            url = match.group(0)
            c.execute(
                'SELECT user FROM repost_track WHERE link=?', (url,))
            row = c.fetchone()
            if not row:
                c.execute(
                    'INSERT INTO repost_track (link, user) VALUES (?, ?)',
                    (url, msg.sender.nick))
            elif msg.sender.nick != row[0]:
                response = (random.choice(_report_msgs)
                            % (msg.sender.nick, row[0]))
                bot.send(lib.irc.say(msg.channel, response))
    bot.db.commit()
