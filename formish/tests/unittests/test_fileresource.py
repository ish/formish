import unittest
from formish import fileresource


class TestCase(unittest.TestCase):
    def test_size_from_dict(self):
        tests = [
            # Easy stuff
            ({}, (None, None, False)),
            ({'size': '10x20'}, (10, 20, False)),
            ({'width': '10'}, (10, None, False)),
            ({'height': '20'}, (None, 20, False)),
            ({'width': '10', 'height': '20'}, (10, 20, False)),
            ({'max-size': '10x20'}, (10, 20, True)),
            ({'max-width': '10'}, (10, None, True)),
            ({'max-height': '20'}, (None, 20, True)),
            ({'max-width': '10', 'max-height': '20'}, (10, 20, True)),
            # Anything non-max has precedence
            ({'width': '10', 'max-height': '20'}, (10, None, False)),
            # "Empty" request args
            ({'size': ''}, (None, None, False)),
            ({'width': ''}, (None, None, False)),
            ({'height': ''}, (None, None, False)),
            ({'size': ' '}, (None, None, False)),
            ({'width': ' '}, (None, None, False)),
            ({'height': ' '}, (None, None, False)),
        ]
        for test, expected in tests:
            result = fileresource.get_size_from_dict(test)
            self.assertEquals(result, expected)


if __name__ == '__main__':
    unittest.main()
