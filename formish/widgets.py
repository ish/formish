from formish.converter import *
from formish.validation import *

# Marker object for args that are not supplied
_UNSET = object()

class Widget(object):
    
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]

    # ??: Should the validate be here? Confused
    def validate(self, data):
        errors = None
        return data, errors

    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])    


class Input(Widget):
    pass
   

class Password(Widget):
    pass

   
class CheckedPassword(Widget):
    
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        password = data.get('password',[None])[0]
        confirm = data.get('confirm',[None])[0]
        if password != confirm:
            raise FieldValidationError('Password did not match')
        return string_converter(schemaType).toType(password)


class Hidden(Widget):
    
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])

        
class TextArea(Widget):
    
    def __init__(self, cols=None, rows=None):
        if cols is not None:
            self.cols = cols
        if rows is not None:
            self.rows = rows 
                
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])

    
class Checkbox(Widget):

    def pre_render(self, schemaType, data):
        return [boolean_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        if len(data) == 0:
            out=False
        else:
            out=True
        return boolean_converter(schemaType).toType(out)            

    
class DateParts(Widget):
    
    def pre_render(self, schemaType, data):
        data = datetuple_converter(schemaType).fromType(data)
        d = {}
        d['year'] = [data[0]]
        d['month'] = [data[1]]
        d['day'] = [data[2]]
        return d
    
    def convert(self, schemaType, data):
        year = data.get('year', [''])[0]
        month = data.get('month', [''])[0]
        day = data.get('day', [''])[0]
        return datetuple_converter(schemaType).toType((year, month, day))
    
    
class SelectChoice(Widget):

    def __init__(self, options, noneOption=None):
        self.options = options
        self.noneOption = noneOption
            
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])

    def selected(self, option, value):
        if option[1] == value:
            return ' selected="selected"'

    
class RadioChoice(Widget):

    def __init__(self, options, noneOption=None):
        self.options = options
        self.noneOption = noneOption
            
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        if len(data) == 0:
            return []
        return string_converter(schemaType).toType(data[0])

    def selected(self, option, value):
        if option[1] == value:
            return ' checked="checked"'
    
    
class CheckboxMultiChoice(Widget):

    def __init__(self, options):
        self.options = options
            
    def pre_render(self, schemaType, data):
        if data is None: 
            return []
        return [string_converter(schemaType.attr).fromType(d) for d in data]
    
    def convert(self, schemaType, data):
        return [string_converter(schemaType.attr).toType(d) for d in data]

    def checked(self, option, value):
        if value is not None and option[1] in value:
            return ' checked="checked"'
    
 
class BoundWidget(object):
    
    def __init__(self, widget, field, cssClass=[]):
        self.widget = widget
        self.field = field
        self.cssClass=cssClass
        
    def pre_render(self, schemaType, data):
        return self.widget.pre_render(schemaType, data)

    def convert(self, schemaType, data):
        return self.widget.convert(schemaType, data)
        
    def validate(self, data):
        return self.widget.validate(data)

