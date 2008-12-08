from testish.lib.base import TestCase
from testish.lib import forms


class Test(TestCase):

    def test_func(self):
        sel = self.selenium
        for attr in dir(forms):
            if attr.startswith('functest_'):
                getattr(forms,attr)(self,sel)

