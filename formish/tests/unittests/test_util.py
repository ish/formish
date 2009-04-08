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

