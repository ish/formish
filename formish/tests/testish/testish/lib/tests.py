from testish.lib.base import TestCase
from testish.lib import forms


class Test(TestCase):

    request = lambda x: webob.Request.blank('http://localhost/')
    def test_func(self):
        sel = self.selenium
        for attr in dir(forms):
            if attr.startswith('functest_'):
                getattr(forms,attr)(self,sel)


    def test_unit(self):
        sel = self.selenium
        for attr in dir(forms):
            if attr.startswith('unittest_'):
                getattr(forms,attr)(self)
    
