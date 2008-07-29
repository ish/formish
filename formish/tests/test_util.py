from formish.forms import *
from formish import validation
import unittest
from schemaish import *
from formish.dottedDict import dottedDict
import wingdbstub

class DummyObject():
    pass

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
        """ Just checking that converting results in assigning the right dict """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).data, test[1])
        for test in self.test_error:
            self.assertRaises(KeyError,dottedDict, test)
            
    def test_comparing(self):
        """ Using the special method __eq__ to compare a dotted dict with a normal dict """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]), test[1])
            
    def test_references(self):
        """ Does it refer to the same data if you convert an existing dottedDict or plain dict """
        a = DummyObject()
        d = {'a.a.a':1, 'a.b.a':3, 'b':a}
        # Check dict single level keys don't lose reference
        self.assertEqual( dottedDict(d).data['b'], d['b'] )
        self.assertEqual( dottedDict(d).data, dottedDict(dottedDict(d)).data )
        


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
        """ use get method and __getitem__ on dotted dict """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).get(test[1]), test[2])
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0])[test[1]], test[2])
            
    def test_set(self):
        """ set a variable using normal and dotted notation """
        for test in self.test_data:
            dd = dottedDict(test[0])
            do = DummyObject()
            dd['x'] = do
            self.assertEqual(dd['x'], do)
            
    def test_keys(self):
        """ check that the .keys() method returns correctly """
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).keys(), test[0].keys())
       
    def test_setdefault(self):
        do = DummyObject()
        for test in self.test_data:
            self.assertEqual(dottedDict(test[0]).setdefault('X.Y.Z',7), 7)
        
            
    def test_get_missingattr(self):
        """ This should raise an AttributeError - not working """
        d = dottedDict( {'a': {'a': 1}, 'b': 2} )
        self.assertRaises(KeyError, getattr, d , 'Q.Q.Q')
        self.assertRaises(KeyError, getattr, dottedDict(), 'missing')
        

    def test_missing(self):
        self.assertEqual(dottedDict({}).get('missing', None), None)
        self.assertEqual(dottedDict({}).get('missing', "value"), "value")


class Request(object):
    
    def __init__(self, POST=None):
        if POST is None:
            POST = {}
        self.POST = POST
        self.method = 'POST'
            
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
        self.assertEqual(form.request,request)
        self.assertEqual(form.structure.attr,schema_empty)
        self.assertEqual(form.name,name)
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
        self.assertEqual(form.a._data, 1)
        self.assertEqual(form.b._data, 2)
        self.assertEqual(form.a.title, 'A')
        self.assertEqual(form.b.title, 'B')
        
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
        form.defaults = fd
        self.assert_(form._data == fd)
        self.assertEqual(form.one.a._data, 2)
        self.assertEqual(form.two.b._data, 3)
        self.assertEqual(form.one.title, 'One')
        self.assertEqual(form.two.title, 'Two')
        self.assertEqual(form.two.b.title, 'B')
        


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
        form.defaults = fd
        self.assertEqual(form._data, fd)
        self.assertEqual(form.one.a._data, 3)
        self.assertEqual(form.one.a.title, "A")
        self.assertEqual(form.one.b.title, "B")
        self.assertEqual(form.one.c.x.title, "X")
        self.assertEqual(form.one.a.description, "This is a field with name a and title A and has a NotEmpty validator")
        self.assert_(len(list(form.one.fields)) == 3)
    
        form.one.a = 7
        self.assertEqual(form.one.a, 7)
       
        
        
    def test_nested_form_validation(self):
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
        request =  Request({'one.a':[''],'one.b': [''],'one.c.x': [''],'one.c.y': ['']})
        name = "Nested Form one"
        form = Form(name, schema_nested, request)
        
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'one.a': '', 'one.b': '', 'one.c.x': '', 'one.c.y': ''})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'one': {'a': '', 'c': {'y': '', 'x': ''}, 'b': ''}} )) == {'one.a':[''],'one.b': [''],'one.c.x': [''],'one.c.y': ['']})
        
        self.assertRaises(validation.FormError, form.validate)

        self.assert_( isinstance(form.errors['one']['a'], Invalid) )
        self.assertEqual( form.errors['one']['a'].message, "Please enter a value" )
        self.assert_( isinstance(form.one.a.error, Invalid) )
        self.assertEqual( form.one.a.error.message, "Please enter a value" )
        
    def test_nested_form_typecheck(self):
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
        request =   Request({'one': {'a':['woot!'],'b':[''], 'c': {'x':[''],'y':['']}}})
        name = "Nested Form two"
        form = Form(name, schema_nested, request)
        self.assert_(form.validate() == {'one': {'a':'woot!','b':'', 'c': {'x':'','y':''}}})
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

        

    def test_integer_type(self):
        schema_flat = Structure("One", attrs=[("a", Integer("A")), ("b", String("B"))])
        request = Request({'a': ['3'], 'b': ['4']})
        name = "Integer Form"
        form = Form(name, schema_flat, request)
        self.assert_(form.structure.attr is schema_flat)
        fd = {'a': 1,'b': '2'}
        form.data = fd
        self.assertEquals(form.validate(), {'a': 3, 'b': '4'})
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'a': 3, 'b': '4'})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'a': 3, 'b': '4'} )) == {'a': ['3'], 'b': ['4']})
         
    def test_incorrect_initial_data(self):
        """ TODO: This should raise an error when we get inbound checking which will rely on the schema having inbuilt schema checking!!! """
        schema_flat = Structure("One", attrs=[("a", Integer("A")), ("b", String("B"))])
        r = {'a': ['3'], 'b': ['4']}
        request = Request(r)
        name = "Integer Form"
        form = Form(name, schema_flat, request)
        fd = {'a': '1','b': 2}
        form.data = fd
        self.assertEquals(form.validate(), {'a': 3, 'b': '4'})
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'a': 3, 'b': '4'})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'a': 3, 'b': '4'} )) == r)
          
    def test_datetuple_type(self):
        schema_flat = Structure("One", attrs=[("a", Date("A")), ("b", String("B"))])
        r = {'a': {'day':[1],'month':[3],'year':[1966]}, 'b': ['4']}
        request = Request(r)
        name = "Date Form"
        form = Form(name, schema_flat, request)
        form.a.widget = DateParts()
        from datetime import date
        d = date(1966,3,1)
        fd = {'a': d,'b': '2'}
        form.data = fd
        self.assertEquals(form.validate(), {'a': d, 'b': '4'})
        self.assertEqual( convertRequestDataToData(form.structure, dottedDict(request.POST)) , {'a': d, 'b': '4'})
        self.assert_( convertDataToRequestData(form.structure, dottedDict( {'a': d, 'b': '4'} )) == r)
               
if __name__ == "__main__":
    unittest.main()

