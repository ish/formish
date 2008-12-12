import unittest
import webob
import schemaish
from schemaish import *
from formish import *
from formish.widgets import *
from BeautifulSoup import BeautifulSoup
from formish import validation as fv
from datetime import date
from validatish import validator as v


class TestHTML(unittest.TestCase):
    """ Basic tests - we need lots more to make this robust
    """

    def test_default_title(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String())])
        f = Form(schema,name='form')
        print f()
        soup = BeautifulSoup(f())
        assert len(soup.findAll(id='form-one')) == 1 , "test that the form field is being created"
        
    def test_error_html(self):
        r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
        r.POST['one'] = ''
        schema = schemaish.Structure([('one', schemaish.String(validator=v.Required()))])
        f = Form(schema,name="form")
        try:
            data = f.validate(r)
        except fv.FormError, e:
            assert isinstance(f.errors['one'], attr.Invalid)        
        soup = BeautifulSoup(f())
        assert soup.find(id='form-one-field').find("span", "error").string == 'is required' , "test that the form error is being created"
        
    def test_complex_form(self):
        
        one = Structure([("a", String(validator=v.All(v.Email(),v.Required()))), ("b", String()), ("c", Sequence(Integer()))])
        two = Structure([("a", String()), ("b", Date()), ('c', Sequence(String())), ("d", String()), ("e", Integer(validator=v.Required())), ("f", String(validator=v.Required())) ])
        schema = Structure([("one", one), ("two", two)])
        f = Form(schema,name="form")

        f['one.b'].widget = TextArea()
        f['two.a'].widget = SelectChoice([('opt1',"Options 1"),('opt2',"Option 2")], noneOption=('-select option-',None))
        f['two.b'].widget = DateParts()
        f['two.c'].widget = CheckboxMultiChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.d'].widget = RadioChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.f'].widget = CheckedPassword()

        f.add_action(lambda x: x, 'submit', label="Submit Me")
        f.defaults = {'one': {'a' : 'ooteenee','c':['3','4','5']}, 'two': {'a': 'opt1','b': date(1966,1,3),'c':['opt2'],'d':'opt2'} } 
        soup = BeautifulSoup(f())
        ## Latch the results for acceptance tests
        #open('formish/tests/expectations/test_complex_form.html','w').write(html)
        expectedSoup = BeautifulSoup( open('formish/tests/unittests/expectations/test_complex_form.html').read())
        print f()
        #assert soup == expectedSoup


if __name__ == '__main__':
    unittest.main()
