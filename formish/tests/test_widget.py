import unittest

import formish


class TestCheckboxMultiChoice(unittest.TestCase):

    def test_empty_options(self):
        formish.CheckboxMultiChoice([])


class TestSelectChoice(unittest.TestCase):

    def test_empty_options(self):
        formish.SelectChoice([])


class TestRadioChoice(unittest.TestCase):

    def test_empty_options(self):
        formish.RadioChoice([])


if __name__ == '__main__':
    unittest.main()

