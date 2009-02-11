import unittest
from dottedish import dotted, _set_dict, _get, _setdefault


class DummyObject(object):
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
            self.assertEqual(dotted(test[0]).data, test[1])
        
    def test_convert_error(self):
        for test in self.test_error:
            self.assertRaises(KeyError,dotted, test)
            
    def test_convert_dictlist(self):
        for test in self.test_dictlist_data:
            self.assertEqual(dotted(test[0]).data, test[1])
            
    def test_comparing(self):
        """Using the special method __eq__ to compare a dotted dict with a normal dict """
        for test in self.test_dict_data:
            self.assertEqual(dotted(test[0]), test[1])
            
    def test_references(self):
        """Does it refer to the same data if you convert an existing dotted or plain dict """
        a = DummyObject()
        d = {'a.a.a':1, 'a.b.a':3, 'b':a}
        # Check dict single level keys don't lose reference
        self.assertEqual( dotted(d).data['b'], d['b'] )
        self.assertEqual( dotted(d).data, dotted(dotted(d)).data )
        
    def test_set_dict(self):
        # Set dict should return a list if the key is a '0'
        testval = 'test'
        tests = [
            ({}, ['a'], {'a':testval}),
            ({}, ['0'], [testval]),
            ({}, [0], [testval]),
            ({}, [0,'a'], [{'a':testval}]),
            ({}, ['list',0,'a'], {'list':[{'a':testval}]}),
            ({'a':2}, ['a'], {'a':testval}),
            ({'a': [0,1,2]},['a',3], {'a': [0,1,2,testval]}),
            ({'a': [0,1,2]},['a','3'], {'a': [0,1,2,testval]}),
            ([{'a': [1]}], [0,'b'], [{'a': [1],'b': testval}]),
        ]

        for d, key, result in tests:
            d = _set_dict(d, key, testval)
            self.assertEqual( d, result )

        #error_tests = [
            #({'a':2}, ['0']),
            #({'a':2}, [0]),
            #({'a': [0,1,2]},['a',4]),
            #({'a': [0,1,2]},['a','4']),
            
        #]
        #for d, key in error_tests:
            #c = lambda ignore: _set_dict(d, key, testval)
            #self.assertRaises( KeyError, c, None )
        
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
            dd = dotted(d)
            for k, v in checkers:
                self.assertEquals(dd.get(k), v)

        error_tests = [
        ( {'list': {}}, ( ('list.0.a',None), ) ),
        ( {'list': {}}, ( ('list.0.a', 'foo'), ) ),
        
        ]
        # Check None's come out
        for d, checkers  in error_tests:
            dd = dotted(d)
            for k, v in checkers:
                self.assertEquals(dd.get(k), None)
        # Check the default comes out
        for d, checkers  in error_tests:
            dd = dotted(d)
            for k, v in checkers:
                self.assertEquals(dd.get(k, v), v)

    def test_dict_dottedset(self):
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
            dd = dotted(d)
            for k, v, result in checkers:
                dd[k] = v
                self.assertEquals(dd, result)

                
    def test_setdefault(self):
        testval = 'test'
        tests = [
            ( {}, 'one.a', {'one': {'a':testval}} ),
            ( {}, 'list.0.a', {'list': [ {'a':testval} ] }),
            ( [{'a': 1}],  '1.a', [{'a':1},{'a':testval}] ),
            ( {'list':[{'a': 1}]}, 'list.1.a',  {'list': [{'a':1},{'a':testval}] }),
            ( {'list': {'x':{}}}, 'list.x.0.a', {'list':{'x':[{'a':testval}]}} ), 
            ( {'one':{'a':1}}, 'one.b', {'one': {'a':1,'b':testval}}),
            ( {'one': {'a': [''], 'b': ['']}}, 'one.c.x', {'one': {'a': [''], 'b': [''], 'c':{'x':testval}}} ),
            ]
        for data, dottedkey, value in tests:
            _setdefault(data, dottedkey, testval)
            self.assertEquals(data, value)
        
            
if __name__ == "__main__":
    unittest.main()

