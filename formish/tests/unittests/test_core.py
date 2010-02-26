import formish
import unittest
import schemaish
from dottedish.api import dotted, unflatten
from formish.forms import validation
from webob.multidict import MultiDict
import validatish


class DummyObject(object):
    pass


class Request(object):
    headers = {'content-type':'text/html'}
    
    def __init__(self, form_name='form', POST=None, GET=None, method='POST'):
        # Build GET and POST data
        self.GET = MultiDict(GET or {})
        self.POST = MultiDict(POST or {})
        # Add the form's name to the appropriate request data dict.
        getattr(self, method.upper())['__formish_form__'] = form_name
        # Set the method
        self.method = method

    def get_post(self):
        def container_factory(parent_key, item_key):
            if item_key.isdigit():
                return []
            return {}
        return unflatten(self.POST.dict_of_lists().iteritems(), container_factory=container_factory)
        
            
class TestFormBuilding(unittest.TestCase):
    """Build a Form and test that it doesn't raise exceptions on build and that the methods/properties are as expected"""

    def test_form(self):
        """Test empty form construction """
        schema_empty = schemaish.Structure()        
        name = "Empty Form"
        form = formish.Form(schema_empty, name)

        # Schema matches
        self.assertEqual(form.structure.attr,schema_empty)
        # Form name matches
        self.assertEqual(form.name,name)
        # this is really empty
        assert list(form.fields) == []

    def test_readonly_field(self):
        """Test a form that has no a read only field"""
        schema_readonly = schemaish.Structure([("a", schemaish.String()), ("b", schemaish.String())])
        name = "Flat Form"
        request =  Request(name)
        form = formish.Form(schema_readonly, name)
        form['a'].widget=formish.Input(readonly=True)
        request = Request(name, {'b': 'bar'})
        actualdata = form.validate(request)
        expecteddata = {'a': None,'b': 'bar'}
        assert  actualdata == expecteddata
        form.defaults = {'a': 'foo'}
        actualdata = form.validate(request)
        expecteddata = {'a': 'foo','b': 'bar'}
        assert  actualdata == expecteddata
        # XXX Is building a form part of the test? Leaving it in, just in case.
        form()


    def test_flat_form(self):
        """Test a form that has no nested sections """
        schema_flat = schemaish.Structure([("a", schemaish.String()), ("b", schemaish.String())])
        name = "Flat Form"
        form = formish.Form(schema_flat, name)

        # stored schema
        assert form.structure.attr is schema_flat
        # number of fields
        assert len(list(form.fields)) is 2

        
    def test_nested_form(self):
        """Test a form two nested levels"""
        one = schemaish.Structure([("a", schemaish.String()), ("b", schemaish.String())])
        two = schemaish.Structure([("a", schemaish.String()), ("b", schemaish.String())])
        schema_nested = schemaish.Structure([("one", one), ("two", two)])

        name = "Nested Form One"
        form = formish.Form(schema_nested, name)

        # stored schema
        assert form.structure.attr is schema_nested
        # number of fields reflects first level
        assert len(list(form.fields)) == 2



    def test_nested_form_validation_errors(self):
        schema_nested = schemaish.Structure([
            ("one", schemaish.Structure([
                ("a", schemaish.String(validator=validatish.Required())),
                ("b", schemaish.String()),
                ("c", schemaish.Structure([("x", schemaish.String()),("y", schemaish.String())])),
                ])
             ),
            ])
        
        name = "Nested Form Two"
        form = formish.Form(schema_nested, name)

        r = {'one.a':'','one.b': '','one.c.x': '','one.c.y': ''}
        request =  Request(name, r)
        
        self.assertRaises(formish.FormError, form.validate, request)

        # Do we get an error
        self.assert_( form.errors['one.a'], 'is_required') 

        
    def test_nested_form_validation_output(self):
        schema_nested = schemaish.Structure([
            ("one", schemaish.Structure([
                ("a", schemaish.String(validator=validatish.Required())),
                ("b", schemaish.String()),
                ("c", schemaish.Structure([("x", schemaish.String()),("y", schemaish.String())])),
                ])
             ),
            ])
        # Test passing validation
        name = "Nested Form two"
        form = formish.Form(schema_nested, name)

        request = Request(name, {'one.a': 'woot!', 'one.b': '', 'one.c.x': '', 'one.c.y': ''})
        expected = {'one': {'a':u'woot!','b':None, 'c': {'x':None,'y':None}}}
        self.assert_(form.validate(request) == expected)
        self.assertEquals(form.errors , {})


    def test_integer_type(self):
        schema_flat = schemaish.Structure([("a", schemaish.Integer()), ("b", schemaish.String())])
        name = "Integer Form"
        form = formish.Form(schema_flat, name)
        r = {'a': '3', 'b': '4'}
        request = Request(name, r)

        reqr = {'a': ['3'], 'b': ['4']}
        # check scmea matches
        self.assert_(form.structure.attr is schema_flat)
        # Does the form produce an int and a string
        self.assertEquals(form.validate(request), {'a': 3, 'b': '4'})
        # Does the convert request to data work
        self.assertEqual( form.widget.from_request_data(form, request.POST) , {'a': 3, 'b': '4'})
        # Does the convert data to request work
        self.assert_( form.widget.to_request_data(form, {'a': 3, 'b': '4'} ) == reqr)

    def test_failure_and_success_callables(self):


        schema_flat = schemaish.Structure([("a", schemaish.Integer(validator=validatish.Range(min=10))), ("b", schemaish.String())])
        name = "Integer Form"
        form = formish.Form(schema_flat, name)

        r = {'a':'2','b': '4'}
        request = Request(name, r)
        self.assertEquals(form.validate(request, failure, success), 'failure')
        self.assertEquals(form.validate(request, failure), 'failure')
        self.assertRaises(formish.FormError, form.validate, request, success_callable=success)

        r = {'a': '12', 'b': '4'}
        request = Request(name, r)
        form = formish.Form(schema_flat, name)
        self.assertEquals(form.validate(request, failure, success), 'success')
        self.assertEquals(form.validate(request, success_callable=success), 'success')
        self.assertEquals(form.validate(request, failure_callable=failure), {'a': 12, 'b': '4'})
        
          
    def test_datetuple_type(self):
        schema_flat = schemaish.Structure([("a", schemaish.Date()), ("b", schemaish.String())])
        name = "Date Form"
        form = formish.Form(schema_flat, name)
        form['a'].widget = formish.DateParts()

        r = {'a.day': '1','a.month': '3','a.year': '1966', 'b': '4'}
        request = Request(name, r)

        from datetime import date
        d = date(1966,3,1)

        # Check the data is converted correctly
        self.assertEquals(form.validate(request), {'a': d, 'b': '4'})
        # Check req to data
        self.assertEqual( form.widget.from_request_data(form, request.get_post()) , {'a': d, 'b': '4'})
        # Check data to req
        self.assert_( form.widget.to_request_data(form, {'a': d, 'b': '4'}) == {'a': {'month': [3], 'day': [1], 'year': [1966]}, 'b': ['4']})

    def test_form_retains_request_data(self):
        form = formish.Form(schemaish.Structure([("field", schemaish.String())]),'form')
        assert 'name="field" value=""' in form()
        data = form.validate(Request('form', {'field': 'value'}))
        assert data == {'field': 'value'}
        assert form.request_data['field'] == ['value']
        assert 'name="field" value="value"' in form()

    def test_form_accepts_request_data(self):
        form = formish.Form(schemaish.Structure([("field", schemaish.String())]))
        form.request_data = {'field': ['value']}
        assert form._request_data == {'field': ['value']}

    def test_form_with_defaults_accepts_request_data(self):
        form = formish.Form(schemaish.Structure([("field", schemaish.String())]))
        form.defaults = {'field': 'default value'}
        assert 'name="field" value="default value"' in form()
        form.request_data = {'field': ['value']}
        assert form._request_data == {'field': ['value']}
        assert 'name="field" value="value"' in form()

    def test_form_defaults_clears_request_data(self):
        form = formish.Form(schemaish.Structure([("field", schemaish.String())]))
        form.request_data = {'field': ['value']}
        form.defaults = {'field': 'default value'}
        assert form._defaults == {'field': 'default value'}
        assert form._request_data == None
        assert 'name="field" value="default value"' in form()

    def test_method(self):
        schema = schemaish.Structure([('string', schemaish.String())])
        # Default should be POST
        self.assertTrue('method="post"' in formish.Form(schema,'form')().lower())
        # (Crudely) check that an explicit method is rendered correctly by the
        # templates.
        for method in ['POST', 'GET', 'get', 'Get']:
            expected = ('method="%s"' % method).lower()
            rendered = formish.Form(schema, method=method)().lower()
            self.assertTrue(expected in rendered)
        # Check that unsupported methods are rejected.
        self.assertRaises(ValueError, formish.Form, schema, method='unsupported')
        # Check that default (POST) and non-default (e.g. GET) forms validate.
        for method, request in [('post', Request(POST={'string': 'abc'})),
                                ('get', Request(GET={'string': 'abc'}, method='GET'))]:
            data = formish.Form(schema,'form', method=method).validate(request)
            self.assertTrue(data == {'string': 'abc'})

    def test_simple_validation(self):
        schema_flat = schemaish.Structure([("a", schemaish.Integer())])
        name = "Integer Form"
        form = formish.Form(schema_flat, name)
        r = {'a': '3'}
        request = Request(name, r)

        reqr = {'a': ['3']}
        # Does the form produce an int and a string
        self.assertEquals(form.validate(request), {'a': 3})
        # Does the convert request to data work
        # self.assertEqual( validation.from_request_data(form.structure, dotted(request.POST)) , {'a': 3, 'b': '4'})
        # Does the convert data to request work
        # self.assert_( validation.to_request_data(form.structure, dotted( {'a': 3, 'b': '4'} )) == reqr)


class TestActions(unittest.TestCase):

    def test_get(self):
        request = Request(method='GET')
        self.assertTrue(self._form('GET').action(request) == 'one')
        request = Request(GET={'one': 'One'}, method='GET')
        self.assertTrue(self._form('GET').action(request) == 'one')
        request = Request(GET={'two': 'Two'}, method='GET')
        self.assertTrue(self._form('GET').action(request) == 'two')

    def test_post(self):
        request = Request(method='POST')
        self.assertTrue(self._form('POST').action(request) == 'one')
        request = Request(POST={'one': 'One'}, method='POST')
        self.assertTrue(self._form('POST').action(request) == 'one')
        request = Request(POST={'two': 'Two'}, method='POST')
        self.assertTrue(self._form('POST').action(request) == 'two')

    def _form(self, method):
        def callback1(*a, **k):
            return 'one'
        def callback2(*a, **k):
            return 'two'
        schema = schemaish.Structure([('string', schemaish.String())])
        form = formish.Form(schema, method=method, add_default_action=False)
        form.add_action('one', 'One', callback1)
        form.add_action('two', 'Two', callback2)
        return form


def success(request, data):
    return 'success'


def failure(request, form):
    return 'failure'


class TestBugs(unittest.TestCase):

    def test_date_conversion(self):
        from datetime import date, datetime
        schema = schemaish.Structure([('date', schemaish.Date())])
        form = formish.Form(schema,name='form')
        form['date'].widget = formish.SelectChoice([(date(1970,1,1),'a'),
                                                       (date(1980,1,1),'b'),
                                                       (datetime(1990,1,1),'c')])
        self.assertRaises(formish.FormError, form.validate, Request('form', {'date': '1990-01-01T00:00:00'}))
        form()

               
if __name__ == "__main__":
    unittest.main()

