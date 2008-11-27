from peak.rules import abstract, when
import schemaish
try:
    import decimal
    haveDecimal = True
except ImportError:
    haveDecimal = False
from formish import validation, file
from datetime import date, time


class Converter(object):
    
    def __init__(self, schemaType, **k):
        self.schemaType = schemaType
        self.converter_options = k.pop('converter_options', {})
        
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return value
    
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        return value

class NullConverter(Converter):
    pass


class NumberToStringConverter(Converter):
    cast = None
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return str(value)
    
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
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



class FileToStringConverter(Converter):
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return value.filename
        
    def toType(self, value, converter_options={}):
        if value is None or value == '':
            return None
        return file.File(None,value,None)
    
class BooleanToStringConverter(Converter):
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        if value:
            return 'True'
        return 'False'
        
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
        if value not in ('True', 'False'):
            raise validation.FieldValidationError('%r should be either True or False'%value)
        return value == 'True'
    
class DateToStringConverter(Converter):
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return value.isoformat()
    
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
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


class TimeToStringConverter(Converter):
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return value.isoformat()
    
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        value = value.strip()
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
        
 

    
    
    
class DateToDateTupleConverter(Converter):
    
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        return value.year, value.month, value.day
        
    def toType(self, value, converter_options={}):
        if value is None:
            return None
        try:
            try:
                V = [int(v) for v in value]
            except ValueError:
                raise validation.FieldValidationError('Invalid Number')
            value = date(*V)
        except (TypeError, ValueError), e:
            raise validation.FieldValidationError('Invalid date: '+str(e))
        return value
        




def getDialect(delimiter=','):
    import csv
    class Dialect(csv.excel):
        def __init__(self, *a, **k):
            self.delimiter = k.pop('delimiter',',')
            csv.excel.__init__(self,*a, **k)
    return Dialect(delimiter=delimiter)

def convert_csvrow_to_list(row, delimiter=','):
    import cStringIO as StringIO
    import csv
    dialect = getDialect(delimiter=delimiter)
    sf = StringIO.StringIO()
    csvReader = csv.reader(sf, dialect=dialect)
    sf.write(row)
    sf.seek(0,0)
    return csvReader.next()
    
def convert_list_to_csvrow(l, delimiter=','):
    import cStringIO as StringIO
    import csv
    dialect = getDialect(delimiter=delimiter)
    sf = StringIO.StringIO()
    writer = csv.writer(sf, dialect=dialect)
    writer.writerow(l)
    sf.seek(0,0)
    return sf.read().strip()


        
class SequenceToStringConverter(Converter):
    """ I'd really like to have the converter options on the init but ruledispatch won't let me pass keyword arguments
    """
    
    def __init__(self, schemaType, **k):
        Converter.__init__(self, schemaType, **k)
        
    def fromType(self, value, converter_options={}):
        if value is None:
            return None
        delimiter = converter_options.get('delimiter',',')
        if isinstance(self.schemaType.attr, schemaish.Sequence):
            out = []
            for line in value:
                lineitems =  [string_converter(self.schemaType.attr.attr).fromType(item) for item in line]
                linestring = convert_list_to_csvrow(lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)
        elif isinstance(self.schemaType.attr, schemaish.Tuple):
            out = []
            for line in value:
                lineitems =  [string_converter(self.schemaType.attr.attrs[n]).fromType(item) for n,item in enumerate(line)]
                linestring = convert_list_to_csvrow(lineitems, delimiter=delimiter)
                out.append(linestring)
            return '\n'.join(out)
 
        else:
            value =  [string_converter(self.schemaType.attr).fromType(v) for v in value]
            return convert_list_to_csvrow(value, delimiter=delimiter)
        
    
    def toType(self, value, converter_options={}):
        if not value:
            return None
        delimiter = converter_options.get('delimiter',',')
        if isinstance(self.schemaType.attr, schemaish.Sequence):
            out = []
            for line in value.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [string_converter(self.schemaType.attr.attr).toType(v) for v in l]
                out.append( convl )
            return out
        if isinstance(self.schemaType.attr, schemaish.Tuple):
            out = []
            for line in value.split('\n'):
                l = convert_csvrow_to_list(line, delimiter=delimiter)
                convl = [string_converter(self.schemaType.attr.attrs[n]).toType(v) for n,v in enumerate(l)]
                out.append( tuple(convl) )
            return out
        else:
            if delimiter != '\n' and len(value.split('\n')) > 1:
                raise validation.FieldValidationError("More than one line found for csv with delimiter=\'%s\'"%delimiter)
            if delimiter == '\n':
                out = value.splitlines()
            else:
                out = convert_csvrow_to_list(value, delimiter=delimiter)
                
            return [string_converter(self.schemaType.attr).toType(v) for v in out]



class TupleToStringConverter(Converter):
    """ I'd really like to have the converter options on the init but ruledispatch won't let me pass keyword arguments
    """
    
    def __init__(self, schemaType, **k):
        Converter.__init__(self, schemaType, **k)
        
    def fromType(self, value, converter_options={}):
        delimiter = converter_options.get('delimiter',',')
        if value is None:
            return None
        lineitems =  [string_converter(self.schemaType.attrs[n]).fromType(item) for n,item in enumerate(value)]
        linestring = convert_list_to_csvrow(lineitems, delimiter=delimiter)

        return linestring
        
    
    def toType(self, value, converter_options={}):
        delimiter = converter_options.get('delimiter',',')
        if not value:
            return None
        l = convert_csvrow_to_list(value, delimiter=delimiter)
        convl = [string_converter(self.schemaType.attrs[n]).toType(v) for n,v in enumerate(l)]
        return tuple(convl)
    
    
@abstract()
def string_converter(schemaType):
    pass


@when(string_converter, (schemaish.String,))
def string_to_string(schemaType):
    return NullConverter(schemaType)

@when(string_converter, (schemaish.Integer,))
def int_to_string(schemaType):
    return IntegerToStringConverter(schemaType)

@when(string_converter, (schemaish.Float,))
def float_to_string(schemaType):
    return FloatToStringConverter(schemaType)

@when(string_converter, (schemaish.Decimal,))
def decimal_to_string(schemaType):
    return DecimalToStringConverter(schemaType)

@when(string_converter, (schemaish.Date,))
def date_to_string(schemaType):
    return DateToStringConverter(schemaType)

@when(string_converter, (schemaish.Time,))
def time_to_string(schemaType):
    return TimeToStringConverter(schemaType)

@when(string_converter, (schemaish.Sequence,))
def sequence_to_string(schemaType):
    return SequenceToStringConverter(schemaType)

@when(string_converter, (schemaish.Tuple,))
def tuple_to_string(schemaType):
    return TupleToStringConverter(schemaType)

@when(string_converter, (schemaish.Boolean,))
def boolean_to_string(schemaType):
    return BooleanToStringConverter(schemaType)

@when(string_converter, (schemaish.File,))
def file_to_string(schemaType):
    return FileToStringConverter(schemaType)


@abstract()
def datetuple_converter(schemaType):
    pass

@when(datetuple_converter, (schemaish.Date,))
def date_to_datetuple(schemaType):
    return DateToDateTupleConverter(schemaType)



@abstract()
def boolean_converter(schemaType):
    pass

@when(boolean_converter, (schemaish.Boolean,))
def boolean_to_boolean(schemaType):
    return NullConverter(schemaType)



@abstract()
def file_converter(schemaType):
    pass

@when(file_converter, (schemaish.File,))
def file_to_file(schemaType):
    return NullConverter(schemaType)





__all__ = [
    'string_converter','datetuple_converter','boolean_converter','file_converter'
    ]
