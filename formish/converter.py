from peak.rules import abstract, when
import schemaish
try:
    import decimal
    haveDecimal = True
except ImportError:
    haveDecimal = False
from formish import validation
from datetime import date, time
from formish.dottedDict import dottedDict

class NullConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None
        return value
    
    def toType(self, value):
        if value is None:
            return None
        return value


class NumberToStringConverter(object):
    cast = None
    
    def fromType(self, value):
        if value is None:
            return None
        return str(value)
    
    def toType(self, value):
        if value is not None:
            value = value.strip()
        if not value:
            return None
        # "Cast" the value to the correct type. For some strange reason,
        # Python's decimal.Decimal type raises an ArithmeticError when it's
        # given a dodgy value.
        try:
            value = self.cast(value)
        except (ValueError, ArithmeticError):
            raise validation.FieldValidationError("Not a valid number")
        return value
        
        
class IntegerToStringConverter(NumberToStringConverter):
    cast = int


class FloatToStringConverter(NumberToStringConverter):
    cast = float


if haveDecimal:
    class DecimalToStringConverter(NumberToStringConverter):
        cast = decimal.Decimal


class BooleanToStringConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None
        if value:
            return 'True'
        return 'False'
        
    def toType(self, value):
        if value is not None:
            value = value.strip()
        if not value:
            return None
        if value not in ('True', 'False'):
            raise validation.FieldValidationError('%r should be either True or False'%value)
        return value == 'True'
    
    
class DateToStringConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None
        return value.isoformat()
    
    def toType(self, value):
        if value is not None:
            value = value.strip()
        if not value:
            return None
        return self.parseDate(value)
        
    def parseDate(self, value):
        try:
            y, m, d = [int(p) for p in value.split('-')]
        except ValueError:
            raise validation.FieldValidationError('Invalid date')
        try:
            value = date(y, m, d)
        except ValueError, e:
            raise validation.FieldValidationError('Invalid date: '+str(e))
        return value


class TimeToStringConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None
        return value.isoformat()
    
    def toType(self, value):
        if value is not None:
            value = value.strip()
        if not value:
            return None
        return self.parseTime(value)
        
    def parseTime(self, value):
        
        if '.' in value:
            value, ms = value.split('.')
        else:
            ms = 0
            
        try:
            parts = value.split(':')  
            if len(parts)<2 or len(parts)>3:
                raise ValueError()
            if len(parts) == 2:
                h, m = parts
                s = 0
            else:
                h, m, s = parts
            h, m, s, ms = int(h), int(m), int(s), int(ms)
        except:
            raise validation.FieldValidationError('Invalid time')
        
        try:
            value = time(h, m, s, ms)
        except ValueError, e:
            raise validation.FieldValidationError('Invalid time: '+str(e))
            
        return value
        
        
class DateToDateTupleConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None, None, None
        return value.year, value.month, value.day
        
    def toType(self, value):
        if value is None:
            return None
        try:
            value = date(*[int(v) for v in value])
        except (TypeError, ValueError), e:
            raise validation.FieldValidationError('Invalid date: '+str(e))
        return value
        


class TupleToStringConverter(object):

    def __init__(self, type):
        self.type = type

    def fromType(self, value):
        if value is None:
            return ""
        row = [iformal.IStringConvertible(t).fromType(v) for (t,v) in
                zip(self.type.fields, value)]
        row = [(i or "").encode("utf-8") for i in row]
        out = StringIO()
        csv.writer(out, delimiter=self.type.delimiter).writerow(row)
        # Return the first line only (the CSV module adds "\r\n").
        return out.getvalue().decode("utf-8").splitlines()[0]

    def toType(self, value):
        if value is not None:
            value = value.strip()
        if not value:
            return None
        value = value.encode("utf-8")
        row = csv.reader(StringIO(value), delimiter=self.type.delimiter).next()
        row = [i.strip() for i in row]
        row = [i.decode("utf-8") for i in row]
        if len(row) != len(self.type.fields):
            raise validation.FieldValidationError("Please enter %d values, separated by a %s" % (len(self.type.fields), self.type.delimiter))
        value = [iformal.IStringConvertible(t).toType(v) for (t,v) in
                zip(self.type.fields, row)]
        return tuple(value)



class SequenceToStringConverter(object):
    
    def fromType(self, value):
        if value is None:
            return None
        import cStringIO as StringIO
        import csv

        sf = StringIO.StringIO()
        writer = csv.writer(sf)
        writer.writerow(value)
        sf.seek(0,0)
        return sf.read().strip()
        
    
    def toType(self, value):
        if not value:
            return None
        import cStringIO as StringIO
        import csv
    
        sf = StringIO.StringIO()
        csvReader = csv.reader(sf)
        sf.write(value)
        sf.seek(0,0)
        return csvReader.next()    


@abstract()
def string_converter(value):
    pass


@when(string_converter, (schemaish.String,))
def string_to_string(value):
    return NullConverter()

@when(string_converter, (schemaish.Integer,))
def int_to_string(value):
    return IntegerToStringConverter()

@when(string_converter, (schemaish.Float,))
def int_to_string(value):
    return IntegerToStringConverter()

@when(string_converter, (schemaish.Decimal,))
def decimal_to_string(value):
    return DecimalToStringConverter()

@when(string_converter, (schemaish.Date,))
def date_to_string(value):
    return DateToStringConverter()

@when(string_converter, (schemaish.Time,))
def date_to_string(value):
    return TimeToStringConverter()

@abstract()
def datetuple_converter(value):
    pass

@when(datetuple_converter, (schemaish.Date,))
def date_to_datetuple(value):
    return DateToDateTupleConverter()

@abstract()
def boolean_converter(value):
    pass

@when(boolean_converter, (schemaish.Boolean,))
def boolean_to_boolean(value):
    return NullConverter()

@when(boolean_converter, (schemaish.String,))
def boolean_to_string(value):
    return BooleanToStringConverter()



__all__ = [
    'string_converter','datetuple_converter'
    ]