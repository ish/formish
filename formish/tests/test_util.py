from formish.forms import *
from formish import validation
import unittest
from schemaish import *
from formish.dottedDict import dottedDict, _getDictFromDottedDict
import wingdbstub

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
            self.assertEquals(dottedDict(test[0]).data, test[1])
        for test in self.test_error:
            self.assertRaises(KeyError,dottedDict, test)
    
    def test_references(self):
        d = {'a.a.a':1, 'a.b.a':3, 'b':2}
        self.assertEquals( dottedDict(d).data, dottedDict(dottedDict(d)).data )


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
            self.assertEquals(dottedDict(test[0]).get(test[1]), test[2])
            
    #def test_get_missingattr(self):
        #self.assertRaises(AttributeError, getattr( dottedDict( {'a':{'a':1}, 'b':2} ), 'x.x.x'))
        #self.assertRaises(KeyError, getattr(dottedDict(), 'missing'))
        

    def test_missing(self):
        self.assertEquals(dottedDict({}).get('missing', None), None)
        self.assertEquals(dottedDict({}).get('missing', "value"), "value")


class Request(object):
    
    def __init__(self, POST=None):
        if POST is None:
            POST = {}
        self.POST = POST
            
class TestFormBuilding(unittest.TestCase):
    """
    Build a Form and test that it doesn't raise exceptions on build and that
    the methods/properties are as expected
    """
    def test_form(self):
        schema_empty = Structure("Empty")        
        request =  Request()
        name = "Empty Form"
        form = Form(name, schema_empty, request)
        self.assert_(form.request is request)
        self.assert_(form.structure.attr is schema_empty)
        self.assert_(form.name is name)
        fd = {'a':1,'b':2}
        form._data = fd
        self.assert_(form._data is fd)
        
    def test_empty_form(self):
        schema_empty = Structure("Empty Attr List", attrs=[])        
        request =  Request()
        name = "Empty Form"
        form = Form(name, schema_empty, request)
        self.assertEquals(list(form.fields), [])
      

    def test_flat_form(self):
        schema_flat = Structure("One", attrs=[("a", String("A")), ("b", String("B"))])
        request =  Request()
        name = "Flat Form"
        form = Form(name, schema_flat, request)
        self.assert_(form.structure.attr is schema_flat)
        self.assertEquals(len(list(form.fields)), 2)
        fd = {'a': 1,'b': 2}
        form._data = fd
        self.assert_(form._data is fd)
        self.assert_(form.a._data, 1)
        self.assert_(form.b._data, 2)
        self.assert_(form.a.title, 'a')
        self.assert_(form.b.title, 'b')
        
    one = Structure("One", attrs=[("a", String("A")), ("b", String("B"))])
    two = Structure("Two", attrs=[("a", String("A")), ("b", String("B"))])
    schema_slightlynested = Structure("Structure", attrs=[("one", one), ("two", two)])

    def test_slightlynested_form(self):
        request =  Request()
        name = "Slightly Nested Form"
        form = Form(name, self.schema_slightlynested, request)
        self.assert_(form.structure.attr is self.schema_slightlynested)
        self.assertEquals(len(list(form.fields)), 2)
        fd = {'one': { 'a': 2, 'b': 3 },'two': { 'a': 2, 'b': 3 }}
        form.data = fd
        self.assert_(form._data == fd)
        self.assert_(form.one.a._data, 2)
        self.assert_(form.two.b._data, 3)
        self.assert_(form.one.title, 'one')
        self.assert_(form.two.title, 'two')
        self.assert_(form.two.b.title, 'b')
        


    def test_nested_form(self):
        schema_nested = Structure("Structure", attrs=[
                ("one", Structure("One", attrs=[
                    ("a", String("A", validator=NotEmpty, 
                        description="This is a field with name a and title A and has a NotEmpty validator")),
                    ("b", String("B")),
                    ("c", Structure("C", attrs=[("x", String("X")),("y", String("Y"))])),
                    ])
                 ),
                ])        
        request =  Request()
        name = "Nested Form"
        form = Form(name, schema_nested, request)
        self.assert_(form.structure.attr is schema_nested)
        self.assertEquals(len(list(form.fields)), 1)
        fd = {'one': {'a': 3, 'b':9, 'c': {'x':3, 'y':5}}}
        form.data = fd
        self.assert_(form._data, fd)
        self.assert_(form.one.a._data, None)
        self.assert_(form.one.a.title, "A")
        self.assert_(form.one.b.title, "B")
        self.assert_(form.one.c.x.title, "X")
        self.assert_(form.one.a.description, "This is a field with name a and title A and has a NotEmpty validator")
        self.assert_(len(list(form.one.fields)) == 3)
       
        
        
    def test_nested_form_validation_one(self):
        schema_nested = Structure("Structure", attrs=[
            ("one", Structure("One", attrs=[
                ("a", String("A", validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String("B")),
                ("c", Structure("C", attrs=[("x", String("X")),("y", String("Y"))])),
                ])
             ),
            ])
        
        # Test failing validation
        request =  Request({'one.a':'','one.b': '','one.c.x': '','one.c.y': ''})
        name = "Nested Form one"
        form = Form(name, schema_nested, request)
        
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'one.a': '', 'one.b': '', 'one.c.x': '', 'one.c.y': ''})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'one': {'a': '', 'c': {'y': '', 'x': ''}, 'b': ''}} )) == {'one.a':'','one.b': '','one.c.x': '','one.c.y': ''})
        
        self.assertRaises(validation.FormError, getattr, form, 'data')

        self.assert_( isinstance(form.errors['one']['a'], Invalid) )
        self.assert_( form.errors['one']['a'].message == "Please enter a value" )
        self.assert_( isinstance(form.one.a.error, Invalid) )
        self.assert_( form.one.a.error.message == "Please enter a value" )
        
    def test_nested_form_validation_two(self):
        schema_nested = Structure("Structure", attrs=[
            ("one", Structure("One", attrs=[
                ("a", String("A", validator=NotEmpty, 
                    description="This is a field with name a and title A and has a NotEmpty validator")),
                ("b", String("B")),
                ("c", Structure("C", attrs=[("x", String("X")),("y", String("Y"))])),
                ])
             ),
            ])
        # Test passing validation
        request =   Request({'one': {'a':'woot!','b':'', 'c': {'x':'','y':''}}})
        name = "Nested Form two"
        form = Form(name, schema_nested, request)
        self.assert_(form.data == {'one': {'a':'woot!','b':'', 'c': {'x':'','y':''}}})
        self.assertEquals(form.errors , {})
        self.assert_( isinstance(form.one.a.widget, BoundWidget) )
        self.assert_( isinstance(form.one.a.widget.widget, Widget) )
        self.assert_( isinstance(form.one.a.widget.field, Field) )
        form.one.a.widget = TextArea()
        self.assert_( isinstance(form.one.a.widget.widget, TextArea) )
        widgets = {'one': {'a': TextArea()}}
        form = Form(name, schema_nested, request, widgets=widgets)
        self.assert_( isinstance(form.one.a.widget, BoundWidget) )
        self.assert_( isinstance(form.one.a.widget.widget, TextArea) )

        
    schema_flat = Structure("One", attrs=[("a", Integer("A")), ("b", String("B"))])

    def test_integer_type(self):
        request = Request({'a': '3', 'b': '4'})
        name = "Integer Form"
        form = Form(name, self.schema_flat, request)
        self.assert_(form.structure.attr is self.schema_flat)
        fd = {'a': 1,'b': 2}
        form._data = fd
        self.assertEquals(form.data, {'a': 3, 'b': '4'})
         
        
    
            
if __name__ == "__main__":
    unittest.main()

