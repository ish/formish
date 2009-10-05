import unittest

from formish import util


class TestUtil(unittest.TestCase):

    def test_form_in_request(self):
        class Request(object):
            method = 'POST'
            GET = {}
            POST = {}
        request = Request()
        self.assertTrue(util.form_in_request(request) is None)
        request = Request()
        request.POST = {'__formish_form__': 'foo'}
        self.assertTrue(util.form_in_request(request) == 'foo')
        request = Request()
        request.method = 'GET'
        request.GET = {'__formish_form__': 'foo'}
        self.assertTrue(util.form_in_request(request) == 'foo')

    def test_file_resource_path(self):
        tests = [
            (None, 'foo', 'foo'),
            (None, '@foo', '@@foo'),
            (None, 'f@o', 'f@o'),
            ('bar', 'foo', '@bar/foo'),
            ('bar', '@foo', '@bar/@foo'),
            ('bar', 'f@o', '@bar/f@o'),
        ]
        for (name, key, path) in tests:
            encoded = util.encode_file_resource_path(name, key)
            self.assertTrue(encoded == path)
            self.assertTrue(util.decode_file_resource_path(encoded) == (name, key))

class Test_classes_from_vars(unittest.TestCase):
    def _callFUT(self, classes, include=None):
        from formish.util import classes_from_vars
        return classes_from_vars(classes, include)

    def test_no_classes(self):
        result = self._callFUT([])
        self.assertEqual(result, '')

    def test_classes_as_basestring(self):
        result = self._callFUT('abc def')
        self.assertEqual(result, ' class="abc def"')

    def test_classes_as_list(self):
        result = self._callFUT(['abc', 'def'])
        self.assertEqual(result, ' class="abc def"')
        
    def test_classes_as_nested_list(self):
        result = self._callFUT(['abc', 'def', ['ghi']])
        self.assertEqual(result, ' class="abc def ghi"')
