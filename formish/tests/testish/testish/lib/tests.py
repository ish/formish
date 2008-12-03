from testish.lib.base import TestCase
from testish.lib import forms


class Test(TestCase):

    def test_all(self):
        sel = self.selenium
        for attr in dir(forms):
            if attr.startswith('test_'):
                getattr(forms,attr)(self,sel)
    
