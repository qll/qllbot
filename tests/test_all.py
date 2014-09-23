import unittest
import sys
sys.path.append('..')


if __name__ == '__main__':
    loader = unittest.TestLoader()
    kwargs = {'pattern': '*.py', 'top_level_dir': '.'}
    lib_tests = loader.discover('lib_tests', **kwargs)
    module_tests = loader.discover('module_tests', **kwargs)
    all_tests = unittest.TestSuite((lib_tests, module_tests))
    unittest.TextTestRunner(verbosity=2).run(all_tests)
