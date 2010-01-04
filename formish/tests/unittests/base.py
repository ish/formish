import unittest
from webob.multidict import MultiDict

class Request(object):
    headers = {'content-type':'text/html'}
    
    def __init__(self, form_name='form', POST=None):
        if POST is None:
            POST = {}
        self.POST = MultiDict(POST)
        self.POST['__formish_form__'] = form_name
        self.GET = self.POST
        self.method = 'POST'

class TestCase(unittest.TestCase):

    Request = Request

