import unittest
import webob
import schemaish
from schemaish import validators as v
from schemaish import *
from formish import *
from formish.widgets import *
from BeautifulSoup import BeautifulSoup
from formish import validation as fv
from datetime import date

class TestHTML(unittest.TestCase):

    def test_default_title(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String())])
        f = Form(schema)
        assert f.one.title == "One", "test default title"
        soup = BeautifulSoup(f(r))
        assert len(soup.findAll(id='form-one')) == 1 , "test that the form field is being created"
        
    def test_error_html(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String(validator=NotEmpty))])
        f = Form(schema)
        try:
            data = f.validate(r)
        except fv.FormError, e:
            assert isinstance(f.errors['one'], schemaish.Invalid)
        soup = BeautifulSoup(f(r))
        assert soup.find(id='form-one-field').find("span", "error").string == 'Please enter a value' , "test that the form error is being created"
        
    def test_complex_form(self):
        request = webob.Request.blank('http://localhost/')
        one = Structure([("a", String(validator=v.Email(not_empty=True))), ("b", String()), ("c", Sequence(Integer()))])
        two = Structure([("a", String()), ("b", Date()), ('c', Sequence(String())), ("d", String()), ("e", Integer(validator=v.NotEmpty())), ("f", String(validator=v.NotEmpty())) ])
        schema = Structure([("one", one), ("two", two)])
        form = Form(schema)
        form.one.b.widget = TextArea()
        form.two.a.widget = SelectChoice([('Option 1','opt1'),('Option 2','opt2')], noneOption=('-select option-',None))
        form.two.b.widget = DateParts()
        form.two.c.widget = CheckboxMultiChoice([('Option 1','opt1'),('Option 2','opt2')])
        form.two.d.widget = RadioChoice([('Option 1','opt1'),('Option 2','opt2')])
        form.two.f.widget = CheckedPassword()
        form.addAction(lambda x: x, 'submit', label="Submit Me")
        form.defaults = {'one': {'a' : 'ooteenee','c':['3','4','5']}, 'two': {'b': date(1966,1,3)} }
        soup = form(request)
        ## Latch the results for acceptance tests
        #open('formish/tests/expectations/test_complex_form.html','w').write(form())
        expectedSoup = open('formish/tests/expectations/test_complex_form.html').read()
        assert soup == expectedSoup


if __name__ == '__main__':
    unittest.main()

