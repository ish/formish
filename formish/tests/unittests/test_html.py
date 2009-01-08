import unittest
import webob
import schemaish
import formish
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
        f = formish.Form(schema,name='form')
        soup = BeautifulSoup(f())
        assert len(soup.findAll(id='form-one')) == 1 , "test that the form field is being created"
        
    def test_error_html(self):
        r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
        r.POST['one'] = ''
        schema = schemaish.Structure([('one', schemaish.String(validator=v.Required()))])
        f = formish.Form(schema,name="form")
        try:
            data = f.validate(r)
        except fv.FormError, e:
            assert isinstance(f.errors['one'], schemaish.attr.Invalid)        
        soup = BeautifulSoup(f())
        assert soup.find(id='form-one-field').find("span", "error").string == 'is required' , "test that the form error is being created"
        
    def test_complex_form(self):
        
        one = schemaish.Structure([("a", schemaish.String(validator=v.All(v.Email(),v.Required()))), ("b", schemaish.String()), ("c", schemaish.Sequence(schemaish.Integer()))])
        two = schemaish.Structure([("a", schemaish.String()), ("b", schemaish.Date()),\
                         ('c', schemaish.Sequence(schemaish.String())), ("d", schemaish.String()), \
                         ("e", schemaish.Integer(validator=v.Required())), ("f", schemaish.String(validator=v.Required())) ])
        schema = schemaish.Structure([("one", one), ("two", two)])
        f = formish.Form(schema,name="form")

        f['one.b'].widget = formish.TextArea()
        f['two.a'].widget = formish.SelectChoice([('opt1',"Options 1"),('opt2',"Option 2")], none_option=('-select option-',None))
        f['two.b'].widget = formish.DateParts()
        f['two.c'].widget = formish.CheckboxMultiChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.d'].widget = formish.RadioChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.f'].widget = formish.CheckedPassword()

        f.add_action(lambda x: x, 'submit', label="Submit Me")
        f.defaults = {'one': {'a' : 'ooteenee','c':['3','4','5']}, 'two': {'a': 'opt1','b': date(1966,1,3),'c':['opt2'],'d':'opt2'} } 
        soup = BeautifulSoup(f())
        ## Latch the results for acceptance tests
        #open('formish/tests/expectations/test_complex_form.html','w').write(html)
        expectedSoup = BeautifulSoup( open('formish/tests/unittests/expectations/test_complex_form.html').read())
        #assert soup == expectedSoup


if __name__ == '__main__':
    unittest.main()
