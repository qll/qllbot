import os
import sys
import unittest
import unittest.mock
import urllib.request

sys.path.append('../../')
import lib.bot
import lib.irc
import modules.youtube


YT_API_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'youtube_api_data.xml')


class TestYoutubeModule(unittest.TestCase):
    def setUp(self):
        lib.irc.say = lambda channel, msg: msg

    def test_link(self):
        meta = 'Trololo [00:04:56] (by testuser)'
        msg = lib.irc.Message('https://www.youtube.com/watch?v=QH2-TGUlwu4')
        bot = lib.bot.Bot('localhost')
        with open(YT_API_DATA_FILE, 'r') as f:
            with unittest.mock.patch.object(bot, 'send') as mocked_send:
                with unittest.mock.patch.object(urllib.request, 'urlopen',
                                                return_value=f) as _:
                    modules.youtube.display_youtube_metadata(bot=bot, msg=msg)
                    mocked_send.assert_called_with(meta)

    def test_nospoiler(self):
        msg = lib.irc.Message('https://www.youtube.com/watch?v=QH2-TGUlwu4 '
                              'nospoiler')
        bot = lib.bot.Bot('localhost')
        with unittest.mock.patch.object(bot, 'send') as mocked:
            mocked.side_effect = Exception('Send method should not be called.')
            modules.youtube.display_youtube_metadata(bot=bot, msg=msg)


if __name__ == '__main__':
    unittest.main()
