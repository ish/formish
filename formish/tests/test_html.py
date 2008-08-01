import unittest
import webob
import schemaish
from schemaish.validators import *
from formish.forms import Form
from BeautifulSoup import BeautifulSoup
from formish import validation as v


class TestHTML(unittest.TestCase):

    def test_default_title(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String())])
        f = Form("form", schema, r)
        assert f.one.title == "One", "test default title"
        soup = BeautifulSoup(f())
        assert len(soup.findAll(id='form-one')) == 1 , "test that the form field is being created"
        
    def test_error_display(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String(validator=NotEmpty))])
        f = Form("form", schema, r)
        try:
            data = f.validate()
        except v.FormError, e:
            assert isinstance(f.errors['one'], schemaish.Invalid)
        soup = BeautifulSoup(f())
        assert soup.find(id='form-one-field').find("span", "error").string == 'Please enter a value' , "test that the form error is being created"
        
        


if __name__ == '__main__':
    unittest.main()

