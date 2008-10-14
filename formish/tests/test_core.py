from formish.forms import *
from formish import validation
import unittest
from schemaish import *
from formish.dottedDict import dottedDict
import copy
from webob import MultiDict

class DummyObject():
    pass



class TestGetDataUsingDottedKey(unittest.TestCase):
    """Testing accessing a dotted key to get data out of a nested dict"""
    test_data = [
        ( {'a':1, 'b':2}, 'a', 1 ),
        ( {'a':1, 'b':2}, 'b', 2 ),
        ( {'a':{'a':1}, 'b':2}, 'a.a', 1 ),
        ( {'a':{'a':1}, 'b':2}, 'b', 2 ),
        ( {'a':{'a':1, 'b':3}, 'b':2}, 'a.a', 1 ),
        ( {'a':{'a':1, 'b':3, 'c':5}, 'b':2}, 'a.c', 5 ),
        ( {'a':{'a':{'a':1}, 'b':{'a':3}}, 'b':2}, 'a.a.a', 1 ),
        ( {'a':{'a':{'a':1}, 'b':{'a':3}}, 'b':2}, 'a.b.a', 3 ),
    ]

    def test_get(self):
        """use get method and __getitem__ on dotted dict """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).get(test[1]), test[2])
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0])[test[1]], test[2])
            
    def test_set(self):
        """set a variable using normal and dotted notation """
        for test in self.test_data:
            dd = dottedDict(test[0])
            do = DummyObject()
            dd['x'] = do
            self.assertEqual(dd['x'], do)
            
    def test_keys(self):
        """check that the .keys() method returns correctly """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).keys(), test[0].keys())
       
    def test_setdefault(self):
        do = DummyObject()
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).setdefault('X.Y.Z',7), 7)
        
            
    def test_get_missingattr(self):
        """This should raise an AttributeError - not working """
        d = dottedDict( {'a': {'a': 1}, 'b': 2} )
        self.assertRaises(KeyError, d.__getitem__, 'Q.Q.Q')
        self.assertRaises(KeyError, d.__getitem__, 'missing')
        

    def test_missing(self):
        self.assertEqual(dottedDict({}).get('missing', None), None)
        self.assertEqual(dottedDict({}).get('missing', "value"), "value")


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
        schema_empty = Structure()        
        name = "Empty Form"
        request =  Request(name)
        form = Form(schema_empty, name)
        self.assertEqual(form.structure.attr,schema_empty)
        self.assertEqual(form.name,name)
        fd = {'a':1,'b':2}
        form._data = fd
        assert form._data is fd
        
    def test_empty_form(self):
        """Test empty form construction """
        schema_empty = Structure([])        
        name = "Empty Form"
        request =  Request(name)
        form = Form(schema_empty, name)
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
        fd = {'a': 1,'b': 2}
        form._data = fd
        # defaults have been stored properly 
        assert form._data == fd

        
    one = Structure([("a", String()), ("b", String())])
    two = Structure([("a", String()), ("b", String())])
    schema_slightlynested = Structure([("one", one), ("two", two)])

    def test_slightlynested_form(self):
        """Test a form with nested sections"""
        name = "Slightly Nested Form"
        request =  Request(name)
        form = Form(self.schema_slightlynested, name)
        fd = {'one': { 'a': 2, 'b': 3 },'two': { 'a': 2, 'b': 3 }}
        form.defaults = fd
        # stored schema
        assert form.structure.attr is self.schema_slightlynested
        # number of fields reflects first level
        assert len(list(form.fields)) == 2
        # stored defaults
        assert form.defaults == fd

        


    def test_nested_form(self):
        schema_nested = Structure([
            ("one", Structure([
                ("a", String(validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])        
        name = "Nested Form"
        request =  Request(name)
        form = Form(schema_nested, name)
        # stored schema
        assert form.structure.attr is schema_nested
        # has only a single group
        assert len(list(form.fields)) == 1
        fd = {'one': {'a': 3, 'b':9, 'c': {'x':3, 'y':5}}}
        form.defaults = fd
        # stored defaults
        assert form.defaults == fd

    
       
        
        
    def test_nested_form_validation(self):
        schema_nested = Structure([
            ("one", Structure([
                ("a", String(validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])
        # Test failing validation
        r = {'one.a':'','one.b': '','one.c.x': '','one.c.y': ''}
        reqr = {'one.a':None,'one.b': None,'one.c.x': None,'one.c.y': None}
        reqrdata = {'one.a':[''],'one.b': [''],'one.c.x': [''],'one.c.y': ['']}
        data = {'one.a': '', 'one.b': '', 'one.c.x': '', 'one.c.y': ''}
        
        name = "Nested Form one"
        request =  Request(name, r)
        form = Form(schema_nested, name)
        rdtd = convertRequestDataToData(form.structure, dottedDict(copy.deepcopy(request.POST)))
        assert rdtd == dottedDict(reqr)
        dtrd = convertDataToRequestData(form.structure, dottedDict(data))
        assert dtrd == reqrdata
        
        self.assertRaises(validation.FormError, form.validate, request)

        self.assert_( isinstance(form.errors['one.a'], Invalid) )
        self.assertEqual( form.errors['one.a'].message, "Please enter a value" )

        
    def test_nested_form_typecheck(self):
        schema_nested = Structure([
            ("one", Structure([
                ("a", String(validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String()),
                ("c", Structure([("x", String()),("y", String())])),
                ])
             ),
            ])
        # Test passing validation
        name = "Nested Form two"
        request = Request(name, {'one.a': 'woot!', 'one.b': '', 'one.c.x': '', 'one.c.y': ''})
        reqr = Request(name, {'one.a': ['woot!'], 'one.b': [''], 'one.c.x': [''], 'one.c.y': ['']})
        form = Form(schema_nested, name)
        self.assert_(form.validate(request) == {'one': {'a':u'woot!','b':None, 'c': {'x':None,'y':None}}})
        self.assertEquals(form.errors , {})


        

    def test_integer_type(self):
        schema_flat = Structure([("a", Integer()), ("b", String())])
        r = {'a': '3', 'b': '4'}
        reqr = {'a': ['3'], 'b': ['4']}
        name = "Integer Form"
        request = Request(name, r)
        R = copy.deepcopy(r)
        form = Form(schema_flat, name)
        self.assert_(form.structure.attr is schema_flat)
        fd = {'a': 1,'b': '2'}
        form.defaults = fd
        self.assertEquals(form.validate(request), {'a': 3, 'b': '4'})
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'a': 3, 'b': '4'})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'a': 3, 'b': '4'} )) == reqr)
        
          
    def test_datetuple_type(self):
        schema_flat = Structure([("a", Date()), ("b", String())])
        r = {'a.day':1,'a.month':3,'a.year':1966, 'b': '4'}
        name = "Date Form"
        request = Request(name, r)
        R = copy.deepcopy(r)
        form = Form(schema_flat, name)
        form['a'].widget = DateParts()
        from datetime import date
        d = date(1966,3,1)
        fd = {'a': d,'b': '2'}
        form.defaults = fd
        self.assertEquals(form.validate(request), {'a': d, 'b': '4'})
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , dottedDict({'a': d, 'b': '4'}))
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'a': d, 'b': '4'} )) == dottedDict({'a': {'month': [3], 'day': [1], 'year': [1966]}, 'b': ['4']}))
               
if __name__ == "__main__":
    unittest.main()

