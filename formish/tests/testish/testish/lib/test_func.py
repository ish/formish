from testish.lib.base import TestCase
from testish.lib import forms


class TestTogether(TestCase):
    """
    Run all tests in a single browser session.
    """

    def test_func(self):
        for attr in dir(forms):
            if attr.startswith('functest_'):
                getattr(forms,attr)(self)


class TestSeparately(TestCase):
    """
    Run each test in a separate browser session.

    Test methods are dynamically added to this class by replacing the functest_
    prefix with test_ and attaching the method to the class (see below).
    """
    pass


# Dynamically add test methods to the TestSeparately class. Yep, this is a
# truly horrible hack.
for attr in dir(forms):
    if attr.startswith('functest_'):
        func_name = 'test_%s'%attr[9:]
        func = getattr(forms, attr)
        func.__name__ = func_name
        setattr(TestSeparately, func_name, func)

