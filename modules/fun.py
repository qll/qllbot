import lib.cmd
import random
import re


ZOR_MAX = 6134


@lib.cmd.command(alias=['zor'])
def z0r(msg):
    """Returns random z0r.de link."""
    return 'http://z0r.de/%s' % random.randint(1, ZOR_MAX)


@lib.cmd.command()
def yesno(msg):
    """Answers yes or no to a question."""
    return random.choice(('yes', 'no')) + '.'


# @lib.cmd.command()
# def who(msg):
#     """#who wants help for this command?"""
#     if not msg.params:
#         return
#     params = ' %s ' % msg.params
#     replacements = {'me': 'you', 'my': 'your', 'mine': 'yours'}
#     for a, b in replacements.items():
#         # TODO: fails at "me you"
#         params = re.sub(r' (%s|%s)(\?| )' % (a, b),
#                         lambda m: ' %s%s' % (b if m.group(1) == a else a, m.group(2)),
#                         params)
#     params = params.replace('?', random.choice(('!', '.')))
#     users = Bot().client.channels[get_channel()].users
#     user = users[choice(list(users.keys()))]
#     return '{} {}'.format(user, param[1:-1])
