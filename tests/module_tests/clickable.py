import sys
import unittest
import unittest.mock

sys.path.append('../../')
import lib.bot
import lib.irc
import modules.clickable


class TestClickableModule(unittest.TestCase):
    def setUp(self):
        lib.irc.say = lambda channel, msg: msg
        self.bot = lib.bot.Bot('localhost')

    def test_broken_link(self):
        msg = lib.irc.Message('iceqll.eu/test')
        with unittest.mock.patch.object(self.bot, 'send') as mocked:
            modules.clickable.make_links_clickable(bot=self.bot, msg=msg)
            mocked.assert_called_with('Clickable: http://iceqll.eu/test')

    def test_text(self):
        msg = lib.irc.Message('just a.test')
        with unittest.mock.patch.object(self.bot, 'send') as mocked:
            e = 'Normal text should not be made clickable.'
            mocked.side_effect = Exception(e)
            modules.clickable.make_links_clickable(bot=self.bot, msg=msg)

    def test_link(self):
        msg = lib.irc.Message('https://www.youtube.com/watch?v=IAISUDbjXj0')
        with unittest.mock.patch.object(self.bot, 'send') as mocked:
            e = 'Clickable links should not be made clickable.'
            mocked.side_effect = Exception(e)
            modules.clickable.make_links_clickable(bot=self.bot, msg=msg)


if __name__ == '__main__':
    unittest.main()
