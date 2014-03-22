try:
    import unittest2 as unittest
except ImportError:
    import unittest  # NOQA
    

class TestDummy(unittest.TestCase):

    def test_dummy(self):
        self.assertTrue(True)
