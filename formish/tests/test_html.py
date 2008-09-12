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
from mako.template import Template
from mako.lookup import TemplateLookup


template = """
<%namespace name="formish" file="/formish/Form.html" />
${formish.form(f)}

"""
lookup = TemplateLookup(directories=['formish/templates/mako'])

class TestHTML(unittest.TestCase):
    """ Basic tests - we need lots more to make this robust
    """

    def test_default_title(self):
        r = webob.Request.blank('http://localhost/')
        schema = schemaish.Structure([('one', schemaish.String())])
        f = Form(schema,name='form')

        html= Template(template, lookup=lookup).render(f=f)
        soup = BeautifulSoup(html)
        assert len(soup.findAll(id='form-one')) == 1 , "test that the form field is being created"
        
    def test_error_html(self):
        r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
        r.POST['one'] = ''
        schema = schemaish.Structure([('one', schemaish.String(validator=NotEmpty))])
        f = Form(schema,name="form")
        try:
            data = f.validate(r)
        except fv.FormError, e:
            assert isinstance(f.errors['one'], schemaish.Invalid)        
        html= Template(template, lookup=lookup).render(f=f)
        soup = BeautifulSoup(html)
        assert soup.find(id='form-one-field').find("span", "error").string == 'Please enter a value' , "test that the form error is being created"
        
    def test_complex_form(self):
        
        one = Structure([("a", String(validator=v.Email(not_empty=True))), ("b", String()), ("c", Sequence(Integer()))])
        two = Structure([("a", String()), ("b", Date()), ('c', Sequence(String())), ("d", String()), ("e", Integer(validator=v.NotEmpty())), ("f", String(validator=v.NotEmpty())) ])
        schema = Structure([("one", one), ("two", two)])
        f = Form(schema,name="form")

        f['one.b'].widget = TextArea()
        f['two.a'].widget = SelectChoice([('opt1',"Options 1"),('opt2',"Option 2")], noneOption=('-select option-',None))
        f['two.b'].widget = DateParts()
        f['two.c'].widget = CheckboxMultiChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.d'].widget = RadioChoice([('opt1',"Options 1"),('opt2',"Option 2")])
        f['two.f'].widget = CheckedPassword()

        f.addAction(lambda x: x, 'submit', label="Submit Me")
        f.defaults = {'one': {'a' : 'ooteenee','c':['3','4','5']}, 'two': {'a': 'opt1','b': date(1966,1,3),'c':['opt2'],'d':'opt2'} } 
        html = Template(template, lookup=lookup).render(f=f)
        soup = BeautifulSoup(html)
        ## Latch the results for acceptance tests
        open('formish/tests/expectations/test_complex_form-actual.html','w').write(html)
        expectedSoup = BeautifulSoup( open('formish/tests/expectations/test_complex_form.html').read())
        
        assert soup == expectedSoup


if __name__ == '__main__':
    unittest.main()

