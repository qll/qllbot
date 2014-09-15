import sys
import unittest

sys.path.append('../../')
import lib.event


class TestEvents(unittest.TestCase):
    def setUp(self):
        TestEvents.successful = False
        TestEvents.successful2 = False

    def test_subscribe(self):
        @lib.event.subscribe('test')
        def subscribe_test():
            TestEvents.successful = True

        lib.event.call('test')
        self.assertTrue(TestEvents.successful)

    def test_subscribe_with_params(self):
        @lib.event.subscribe('test2')
        def subscribe_test(successful=False):
            TestEvents.successful = successful

        lib.event.call('test2', {'successful': True})
        self.assertTrue(TestEvents.successful)

    def test_subscribe_two_with_params(self):
        @lib.event.subscribe('test3')
        def subscribe_test(successful=False):
            TestEvents.successful = successful

        @lib.event.subscribe('test3')
        def subscribe_test2(successful=False):
            TestEvents.successful2 = successful

        lib.event.call('test3', {'successful': True})
        self.assertTrue(TestEvents.successful)
        self.assertTrue(TestEvents.successful2)


if __name__ == '__main__':
    unittest.main()
