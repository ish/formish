from formish.forms import *
import unittest
from schemaish import *

class TestDictFromDottedDict(unittest.TestCase):
    """
    Testing conversion from dotted notation dictionary to nested dictionary
    """
    test_data = [
        ( {'a':1, 'b':2}, {'a':1, 'b':2} ),
        ( {'a.a':1, 'b':2}, {'a':{'a':1}, 'b':2} ),
        ( {'a.a':1, 'a.b':3, 'b':2}, {'a':{'a':1, 'b':3}, 'b':2} ),
        ( {'a.a':1, 'a.b':3, 'a.c': 5, 'b':2}, {'a':{'a':1, 'b':3, 'c':5}, 'b':2} ),
        ( {'a.a.a':1, 'a.b.a':3, 'b':2}, {'a':{'a':{'a':1}, 'b':{'a':3}}, 'b':2} ),
   
    ]
    test_error = [
        {'a.a':1, 'b':2, 'a':7},
    ]

    def test_convert(self):
        for test in self.test_data:
            self.assertEquals(getDictFromDottedDict(test[0]), test[1])
        for test in self.test_error:
            self.assertRaises(KeyError,getDictFromDottedDict, test)


class TestGetDataUsingDottedKey(unittest.TestCase):
    """
    Testing accessing a dotted key to get data out of a nested dict
    """
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
        for test in self.test_data:
            self.assertEquals(getDataUsingDottedKey(test[0], test[1]), test[2])
        self.assertRaises(KeyError, getDataUsingDottedKey, {'a':{'a':1}, 'b':2}, 'x.x.x')

    def test_missing(self):
        self.assertRaises(KeyError, getDataUsingDottedKey, {}, 'missing')
        self.assertEquals(getDataUsingDottedKey({}, 'missing', None), None)
        self.assertEquals(getDataUsingDottedKey({}, 'missing', "value"), "value")


class Request(object):
    
    def __init__(self, POST):
        self.POST = POST
            
class TestFormBuilding(unittest.TestCase):
    """
    Build a Form and test that it doesn't raise exceptions on build and that
    the methods/properties are as expected
    """
    schema_empty = Structure("Structure", attrs=[])
    
    def test_form(self):
        request =  Request({})
        name = "Empty Form"
        form = Form(name, self.schema_empty, request)
        self.assert_(form.request is request)
        self.assert_(form.structure.attr is self.schema_empty)
        self.assert_(form.name is name)
        self.assertEquals(form.data, {})
        fd = {'a':1,'b':2}
        form.data = fd
        self.assert_(form.data is fd)
        
    def test_empty_form(self):
        request =  Request({})
        name = "Empty Form"
        form = Form(name, self.schema_empty, request)
        self.assertEquals(list(form.fields), [])
        
    one = Structure("One", attrs=[("a", String("A")), ("b", String("B"))])
    two = Structure("Two", attrs=[("a", String("A")), ("b", String("B"))])
    schema_flat = Structure("Structure", attrs=[("one", one), ("two", two)])

    def test_flat_form(self):
        request =  Request({})
        name = "Flat Form"
        form = Form("wibble", self.schema_flat, request)
        self.assert_(form.structure.attr is self.schema_flat)
        self.assertEquals(len(list(form.fields)), 2)
        fd = {'one': { 'a': 2, 'b': 3 },'two': { 'a': 2, 'b': 3 }}
        form.data = fd
        self.assert_(form.data is fd)
        self.assert_(form.one.a.value, 2)
        self.assert_(form.two.b.value, 3)
        self.assert_(form.one.title, 'one')
        self.assert_(form.two.title, 'two')
        self.assert_(form.two.b.title, 'b')
        
    schema_nested = Structure("Structure", attrs=[
            ("one", Structure("One", attrs=[
                ("a", String("A", validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String("B")),
                ("c", Structure("C", attrs=[("x", String("X")),("y", String("Y"))])),
                ])
             ),
            ])

    def test_nested_form(self):
        request =  Request({})
        name = "Nested Form"
        form = Form(name, self.schema_nested, request)
        self.assert_(form.structure.attr is self.schema_nested)
        self.assertEquals(len(list(form.fields)), 1)
        fd = {'one': {'a': 3, 'b':9, 'c': {'x':3, 'y':5}}}
        form.data = fd
        self.assert_(form.data is fd)
        self.assert_(form.one.a.value, None)
        self.assert_(form.one.a.title, "A")
        self.assert_(form.one.b.title, "B")
        self.assert_(form.one.c.x.title, "X")
        self.assert_(form.one.a.description, "This is a field with name a and title A and has a NotEmpty validator")
        self.assert_(len(list(form.one.fields)) == 3)
       
        
        
    def test_nested_form_validation(self):
        
        # Test failing validation
        request =  Request({'one': {'a':'','b':'', 'c': {'x':'','y':''}}})
        name = "Nested Form"
        form = Form(name, self.schema_nested, request)
        self.assertEquals(form.validateRequest(), False)

        self.assert_( isinstance(form.errors['one']['a'], Invalid) )
        self.assert_( form.errors['one']['a'].message == "Please enter a value" )
        self.assert_( isinstance(form.one.a.error, Invalid) )
        self.assert_( form.one.a.error.message == "Please enter a value" )
        
        # Test passing validation
        request =   Request({'one': {'a':'woot!','b':'', 'c': {'x':'','y':''}}})
        form = Form(name, self.schema_nested, request)
        self.assertEquals(form.validateRequest(), True)
        self.assertEquals(form.errors, {})
        self.assert_( isinstance(form.one.a.widget, BoundWidget) )
        self.assert_( isinstance(form.one.a.widget.widget, Widget) )
        self.assert_( isinstance(form.one.a.widget.field, Field) )
        form.one.a.widget = TextArea()
        self.assert_( isinstance(form.one.a.widget.widget, TextArea) )
        widgets = {'one': {'a': TextArea()}}
        form = Form(name, self.schema_nested, request, widgets=widgets)
        self.assert_( isinstance(form.one.a.widget, BoundWidget) )
        self.assert_( isinstance(form.one.a.widget.widget, TextArea) )
        
        
        
    
            
if __name__ == "__main__":
    unittest.main()

