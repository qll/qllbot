import lib.cmd
import lib.irc
import settings


@lib.cmd.command()
def mh(msg):
    """Highlight everyone in the channel."""
    return " ".join(u.nick for u in msg.channel.users
                    if u.nick != settings.NICKNAME)
