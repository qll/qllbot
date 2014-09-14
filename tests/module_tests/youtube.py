import sys
import unittest
import unittest.mock

sys.path.append('../../')
import lib.bot
import lib.irc
import modules.youtube


class TestYoutubeModule(unittest.TestCase):
    def setUp(self):
        lib.irc.say = lambda channel, msg: msg

    def test_link(self):
        meta = 'Nyan Cat [original] [00:03:37] (by saraj00n)'
        msg = lib.irc.Message('https://www.youtube.com/watch?v=QH2-TGUlwu4')
        bot = lib.bot.Bot('localhost')
        with unittest.mock.patch.object(bot, 'send') as mocked:
            modules.youtube.display_youtube_metadata(bot=bot, msg=msg)
            mocked.assert_called_with(meta)

    def test_nospoiler(self):
        msg = lib.irc.Message('https://www.youtube.com/watch?v=QH2-TGUlwu4 '
                              'nospoiler')
        bot = lib.bot.Bot('localhost')
        with unittest.mock.patch.object(bot, 'send') as mocked:
            mocked.side_effect = Exception('Send method should not be called.')
            modules.youtube.display_youtube_metadata(bot=bot, msg=msg)


if __name__ == '__main__':
    unittest.main()
