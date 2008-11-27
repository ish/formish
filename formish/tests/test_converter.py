import unittest
import formish
import schemaish
from datetime import date

class TestConverters(unittest.TestCase):

    def test_integer_to_string_conversion(self):
        type = schemaish.Integer()
        value = 1
        expected = '1'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_date_string_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = '1966-12-18'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_float_string_conversion(self):
        type = schemaish.Float()
        value = 1.28
        expected = '1.28'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_boolean_string_conversion(self):
        type = schemaish.Boolean()
        value = True
        expected = 'True'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

        value = False
        expected = 'False'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)


    def test_date_datetuple_conversion(self):
        type = schemaish.Date()
        value = date(1966,12,18)
        expected = (1966,12,18)
        actual = formish.converter.datetuple_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.datetuple_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_sequencestring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Integer())
        value = [1,2,3,4]
        expected = '1,2,3,4'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_sequenceboolean_string_conversion(self):
        type = schemaish.Sequence(schemaish.Boolean())
        value = [True,False,True,True]
        expected = 'True,False,True,True'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)


    def test_sequencesequenceinteger_string_conversion(self):
        type = schemaish.Sequence(schemaish.Sequence(schemaish.Integer()))
        value = [[1,2,3],[4,5,6]]
        expected = '1,2,3\n4,5,6'
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

    def test_sequencetupleintegerstring_string_conversion(self):
        type = schemaish.Sequence(schemaish.Tuple((schemaish.Integer(),schemaish.String())))
        value = [(1,'1'),(2,'2')]
        expected = '1,1\n2,2'
    
        actual = formish.converter.string_converter(type).fromType(value)
        self.assertEquals(actual,expected)

        value, expected = expected, value
        actual = formish.converter.string_converter(type).toType(value)
        self.assertEquals(actual,expected)

if __name__ == '__main__':
    unittest.main()
