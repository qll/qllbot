import sys
import unittest

sys.path.append('../../')
import lib.events


class TestEvents(unittest.TestCase):
    def setUp(self):
        TestEvents.successful = False
        TestEvents.successful2 = False

    def test_subscribe(self):
        @lib.events.subscribe('test')
        def subscribe_test():
            TestEvents.successful = True

        lib.events.call('test', [])
        self.assertTrue(TestEvents.successful)

    def test_subscribe_with_params(self):
        @lib.events.subscribe('test2')
        def subscribe_test(successful):
            TestEvents.successful = successful

        lib.events.call('test2', [True])
        self.assertTrue(TestEvents.successful)

    def test_subscribe_two_with_params(self):
        @lib.events.subscribe('test3')
        def subscribe_test(successful):
            TestEvents.successful = successful

        @lib.events.subscribe('test3')
        def subscribe_test2(successful):
            TestEvents.successful2 = successful

        lib.events.call('test3', [True])
        self.assertTrue(TestEvents.successful)
        self.assertTrue(TestEvents.successful2)


if __name__ == '__main__':
    unittest.main()
