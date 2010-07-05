import unittest
from formish import fileresource


class TestCase(unittest.TestCase):
    def test_size_from_dict(self):
        tests = [
            ({}, (None, None)),
            ({'size': '10x20'}, (10, 20)),
            ({'width': '10'}, (10, None)),
            ({'height': '20'}, (None, 20)),
        ]
        for test, expected in tests:
            result = fileresource.get_size_from_dict(test)
            self.assertEquals(result, expected)


if __name__ == '__main__':
    unittest.main()
