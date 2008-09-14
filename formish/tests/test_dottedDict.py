from formish.forms import *
from formish import validation
import unittest
from schemaish import *
from formish.dottedDict import dottedDict, _setDict, _get, _set, _setdefault
import copy


class DummyObject():
    pass

class TestDottedDict(unittest.TestCase):
    """Testing conversion from dotted notation dictionary to nested dictionary"""
    test_dict_data = [
        ( {'a':1, 'b':2}, {'a':1, 'b':2} ),
        ( {'a.a':1, 'b':2}, {'a':{'a':1}, 'b':2} ),
        ( {'a.a':1, 'a.b':3, 'b':2}, {'a':{'a':1, 'b':3}, 'b':2} ),
        ( {'a.a':1, 'a.b':3, 'a.c': 5, 'b':2}, {'a':{'a':1, 'b':3, 'c':5}, 'b':2} ),
        ( {'a.a.a':1, 'a.b.a':3, 'b':2}, {'a':{'a':{'a':1}, 'b':{'a':3}}, 'b':2} ),
        ]
    test_dictlist_data = [
        ( {'a.a.0':1, 'a.a.1':3, 'a.b':2}, {'a':{'a':[1,3], 'b':2}} ),
   
    ]
    test_error = [
        {'a.a':1, 'b':2, 'a':7},
    ]
    


    def test_convert(self):
        """Just checking that converting results in assigning the right dict """
        for test in self.test_dict_data:
            self.assertEqual(dottedDict(test[0]).data, test[1])
            
    def test_convert_error(self):
        for test in self.test_error:
            self.assertRaises(KeyError,dottedDict, test)
            
    def test_convert_dictlist(self):
        import wingdbstub
        for test in self.test_dictlist_data:
            self.assertEqual(dottedDict(test[0]).data, test[1])
            
    def test_comparing(self):
        """Using the special method __eq__ to compare a dotted dict with a normal dict """
        for test in self.test_dict_data:
            self.assertEqual(dottedDict(test[0]), test[1])
            
    def test_references(self):
        """Does it refer to the same data if you convert an existing dottedDict or plain dict """
        a = DummyObject()
        d = {'a.a.a':1, 'a.b.a':3, 'b':a}
        # Check dict single level keys don't lose reference
        self.assertEqual( dottedDict(d).data['b'], d['b'] )
        self.assertEqual( dottedDict(d).data, dottedDict(dottedDict(d)).data )
        
    def test_setDict(self):
        import wingdbstub
        # Set dict should return a list if the key is a '0'
        testval = 'test'
        tests = [
            #({}, ['a'], {'a':testval}),
            #({}, ['0'], [testval]),
            #({}, [0], [testval]),
            #({}, [0,'a'], [{'a':testval}]),
            #({}, ['list',0,'a'], {'list':[{'a':testval}]}),
            #({'a':2}, ['a'], {'a':testval}),
            #({'a': [0,1,2]},['a',3], {'a': [0,1,2,testval]}),
            #({'a': [0,1,2]},['a','3'], {'a': [0,1,2,testval]}),
            ([{'a': [1]}], [0,'b'], [{'a': [1],'b': testval}]),
        ]

        for d, key, result in tests:
            d = _setDict(d, key, testval)
            self.assertEqual( d, result )

        error_tests = [
            ({'a':2}, ['0']),
            ({'a':2}, [0]),
            ({'a': [0,1,2]},['a',4]),
            ({'a': [0,1,2]},['a','4']),
            
        ]
        for d, key in error_tests:
            c = lambda ignore: _setDict(d, key, testval)
            self.assertRaises( KeyError, c, None )
        
    def test_dict_dottedget(self):
        tests = [
        ( {'a':1, 'b':2}, ( ('a',1),('b',2) ) ),
        ( {'a':{'a':1}, 'b':2}, ( ('a.a',1),('b',2) ) ),
        ( {'a':{'a':1, 'b':3}, 'b':2}, ( ('a.a',1),('a.b',3),('b',2) ) ),
        ( {'a':{'a':[1,3], 'b':2}}, ( ('a.a.0',1),('a.a.1',3) ) ),
        ( {'a':{'a':[1, {'a':7}], 'b':2}}, ( ('a.a.0',1),('a.a.1.a',7) ) ),
        ( {'list': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]}, ( ('list.0.a',1), ) ),
        
        ]
        for d, checkers  in tests:
            for k, v in checkers:
                self.assertEquals(_get(d,k), v)
            
    def test_get(self):
        tests = [
        ( {'a':1, 'b':2}, ( ('a',1),('b',2) ) ),
        ( {'a':{'a':1}, 'b':2}, ( ('a.a',1),('b',2) ) ),
        ( {'a':{'a':1, 'b':3}, 'b':2}, ( ('a.a',1),('a.b',3),('b',2) ) ),
        ( {'a':{'a':[1,3], 'b':2}}, ( ('a.a.0',1),('a.a.1',3) ) ),
        ( {'a':{'a':[1, {'a':7}], 'b':2}}, ( ('a.a.0',1),('a.a.1.a',7) ) ),
        ( {'list': [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]}, ( ('list.0.a',1), ) ),
        
        ]
        for d, checkers  in tests:
            dd = dottedDict(d)
            for k, v in checkers:
                self.assertEquals(dd.get(k), v)

        error_tests = [
        ( {'list': {}}, ( ('list.0.a',None), ) ),
        
        ]
        for d, checkers  in error_tests:
            dd = dottedDict(d)
            for k, v in checkers:
                self.assertRaises(KeyError,dd.get, k)

    def test_dict_dottedset(self):
        import wingdbstub
        tests = [
        ( {'list': {}}, ( ('list.0.a',7, {'list':[{'a':7}]}), ) ),
        ( {'list': {'x':{}}}, ( ('list.x.0.a',7, {'list':{'x':[{'a':7}]}}), ) ),
        ]
        for d, checkers in tests:
            for k, v, result in checkers:
                _setdefault(d,k,v)
                self.assertEquals(d, result)
                                
                
    def test_set(self):
        tests = [
        ( {'list': {}}, ( ('list.0.a',7, {'list':[{'a':7}]}), ) ),
        ( {'list': {'x':{}}}, ( ('list.x.0.a',7, {'list':{'x':[{'a':7}]}}), ) ),
        
        ]
        for d, checkers  in tests:
            dd = dottedDict(d)
            for k, v, result in checkers:
                dd[k] = v
                self.assertEquals(dd, result)

                
    def test_setdefault(self):
        tests = [
            ( {}, 'list.0.a', 7 ),
            ( [{'a': 1}],  '1.a', 7 ),
            ( {'list':[{'a': 1}]},  'list.1.a', 7 ),
            ]
        for data, dottedkey, value in tests:
            _setdefault(data, dottedkey, value)
            self.assertEquals(_get(data, dottedkey), value)
        
            
if __name__ == "__main__":
    unittest.main()
 