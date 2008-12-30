from formish.forms import *
from formish.validation import *
import unittest
from schemaish import *
from formish.dottedDict import dottedDict
import copy
from webob import MultiDict
import validatish


class DummyObject():
    pass


class Request(object):
    headers = {'content-type':'text/html'}
    
    def __init__(self, form_name='form', POST=None):
        if POST is None:
            POST = {}
        self.POST = MultiDict(POST)
        self.POST['__formish_form__'] = form_name
        self.method = 'POST'
        
            
class TestFormBuilding(unittest.TestCase):
    """Build a Form and test that it doesn't raise exceptions on build and that the methods/properties are as expected"""

    def test_form(self):
        """Test empty form construction """
        schema_empty = Structure()        
        name = "Empty Form"
        request =  Request(name)
        form = Form(schema_empty, name)

        # Schema matches
        self.assertEqual(form.structure.attr,schema_empty)
        # Form name matches
        self.assertEqual(form.name,name)
        # this is really empty
        assert list(form.fields) == []
        

    def test_flat_form(self):
        """Test a form that has no nested sections """
        schema_flat = Structure([("a", String()), ("b", String())])
        name = "Flat Form"
        request =  Request(name)
        form = Form(schema_flat, name)

        # stored schema
        assert form.structure.attr is schema_flat
        # number of fields
        assert len(list(form.fields)) is 2

        
    def test_nested_form(self):
        """Test a form two nested levels"""
        one = Structure([("a", String()), ("b", String())])
        two = Structure([("a", String()), ("b", String())])
        schema_nested = Structure([("one", one), ("two", two)])

        name = "Nested Form One"
        request =  Request(name)
        form = Form(schema_nested, name)

        # stored schema
        assert form.structure.attr is schema_nested
        # number of fields reflects first level
        assert len(list(form.fields)) == 2


    def test_data_and_request_conversion(self):
        """
        Test convert request to data and convert data to request
        """
        schema_nested = Structure([
            ("one", Structure([
                ("a", String()),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])
        r = {'one.a':'','one.b': '','one.c.x': '','one.c.y': ''}
        reqr = {'one.a':None,'one.b': None,'one.c.x': None,'one.c.y': None}
        reqrdata = {'one.a':[''],'one.b': [''],'one.c.x': [''],'one.c.y': ['']}
        data = {'one.a': '', 'one.b': '', 'one.c.x': '', 'one.c.y': ''}
        
        name = "Nested Form Two"
        request =  Request(name, r)
        form = Form(schema_nested, name)
        # request to data
        rdtd = convert_request_data_to_data(form.structure, dottedDict(copy.deepcopy(request.POST)))
        assert rdtd == dottedDict(reqr)
        # data to request
        dtrd = convert_data_to_request_data(form.structure, dottedDict(data))
        assert dtrd == reqrdata


    def test_nested_form_validation_errors(self):
        schema_nested = Structure([
            ("one", Structure([
                ("a", String(validator=validatish.Required())),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])
        
        name = "Nested Form Two"
        form = Form(schema_nested, name)

        r = {'one.a':'','one.b': '','one.c.x': '','one.c.y': ''}
        request =  Request(name, r)
        
        self.assertRaises(FormError, form.validate, request)

        # Do we get an error
        self.assert_( isinstance(form.errors['one.a'], attr.Invalid) )
        # Is the error message correct
        self.assertEqual( form.errors['one.a'].message, "is required" )

        
    def test_nested_form_validation_output(self):
        schema_nested = Structure([
            ("one", Structure([
                ("a", String(validator=validatish.Required())),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])
        # Test passing validation
        name = "Nested Form two"
        form = Form(schema_nested, name)

        request = Request(name, {'one.a': 'woot!', 'one.b': '', 'one.c.x': '', 'one.c.y': ''})
        expected = {'one': {'a':u'woot!','b':None, 'c': {'x':None,'y':None}}}
        self.assert_(form.validate(request) == expected)
        self.assertEquals(form.errors , {})


    def test_integer_type(self):
        schema_flat = Structure([("a", Integer()), ("b", String())])
        name = "Integer Form"
        form = Form(schema_flat, name)
        r = {'a': '3', 'b': '4'}
        request = Request(name, r)
        R = copy.deepcopy(r)

        reqr = {'a': ['3'], 'b': ['4']}
        # check scmea matches
        self.assert_(form.structure.attr is schema_flat)
        # Does the form produce an int and a string
        self.assertEquals(form.validate(request), {'a': 3, 'b': '4'})
        # Does the convert request to data work
        self.assertEqual( convert_request_data_to_data(form.structure, dottedDict(request.POST)) , {'a': 3, 'b': '4'})
        # Does the convert data to request work
        self.assert_( convert_data_to_request_data(form.structure, dottedDict( {'a': 3, 'b': '4'} )) == reqr)
        
          
    def test_datetuple_type(self):
        schema_flat = Structure([("a", Date()), ("b", String())])
        name = "Date Form"
        form = Form(schema_flat, name)
        form['a'].widget = DateParts()

        r = {'a.day': '1','a.month': '3','a.year': '1966', 'b': '4'}
        R = copy.deepcopy(r)
        request = Request(name, r)

        from datetime import date
        d = date(1966,3,1)

        # Check the data is converted correctly
        self.assertEquals(form.validate(request), {'a': d, 'b': '4'})
        # Check req to data
        self.assertEqual( convert_request_data_to_data(form.structure, dottedDict(request.POST)) , dottedDict({'a': d, 'b': '4'}))
        # Check data to req
        self.assert_( convert_data_to_request_data(form.structure, dottedDict( {'a': d, 'b': '4'} )) == dottedDict({'a': {'month': [3], 'day': [1], 'year': [1966]}, 'b': ['4']}))

    def test_form_retains_request_data(self):
        form = Form(Structure([("field", String())]))
        assert 'name="field" value=""' in form()
        data = form.validate(Request('formish', {'field': 'value'}))
        assert data == {'field': 'value'}
        assert form.request_data['field'] == ['value']
        assert 'name="field" value="value"' in form()

    def test_form_accepts_request_data(self):
        form = Form(Structure([("field", String())]))
        form.request_data = {'field': ['value']}
        assert form.request_data == {'field': ['value']}

    def test_form_with_defaults_accepts_request_data(self):
        form = Form(Structure([("field", String())]))
        form.defaults = {'field': 'default value'}
        assert 'name="field" value="default value"' in form()
        form.request_data = {'field': ['value']}
        assert form.request_data == {'field': ['value']}
        assert 'name="field" value="value"' in form()

    def test_form_defaults_clears_request_data(self):
        form = Form(Structure([("field", String())]))
        form.request_data = {'field': ['value']}
        form.defaults = {'field': 'default value'}
        assert form.defaults == {'field': 'default value'}
        assert form.request_data == {'field': ['default value']}
        assert 'name="field" value="default value"' in form()

               
if __name__ == "__main__":
    unittest.main()

