"""
Commonly needed form widgets.
"""

__all__ = ['Input', 'Password', 'CheckedPassword', 'Hidden', 'TextArea',
        'Checkbox', 'DateParts', 'FileUpload', 'SelectChoice', 'RadioChoice',
        'CheckboxMultiChoice']

import cgi
from formish.converter import *
from formish.validation import *


UNSET = object()


class Widget(object):
    
    def __init__(self,**k):
        self.converter_options = k.get('converter_options',{})
    
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
    
    def __init__(self, **k):
        self.cols = k.pop('cols', None)
        self.rows = k.pop('rows', None)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
    
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data, converter_options=self.converter_options)]
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0], converter_options=self.converter_options)

    
class Checkbox(Widget):

    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        if len(data) == 0:
            out='False'
        else:
            out='True'
        return string_converter(schemaType).toType(out)

    
class DateParts(Widget):
    
    def __init__(self, dayFirst=False):
        self.dayFirst = dayFirst
        
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
    

class FileUpload(Widget):
    
    def __init__(self, fileHandler, showImagePreview=False, allowClear=True):
        self.fileHandler = fileHandler
        self.showImagePreview = showImagePreview
        self.allowClear = allowClear
    
    def pre_render(self, schemaType, data):
        data = string_converter(schemaType).fromType(data)
        if data is None:
            return {'name': ['']}
        return {'name': [data['uid']]}
    
    def pre_parse_request(self, schemaType, data):
        fs = data.get('file',[''])[0]
        if data.get('remove',[None])[0] is not None:
            data['name'] = ['']
        elif fs is not '':
            data['name'] = [self.fileHandler.storeFile(fs)]
        data['file'] = ['']
        return data
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data['name'][0])

    
class SelectChoice(Widget):

    noneOption = ('', '- choose -')

    def __init__(self, options, noneOption=UNSET):
        if not isinstance(options[0], tuple):
            for i, o in enumerate(options):
                options[i] = (o,o)
        self.options = options
        if noneOption is not UNSET:
            self.noneOption = noneOption
            
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])

    def selected(self, option, value, schemaType):
        if option[0] == self.convert(schemaType,[value]):
            return ' selected="selected"'
        else:
            return ''

    
class RadioChoice(Widget):

    noneOption = ('', '- choose -')

    def __init__(self, options, noneOption=UNSET):
        if not isinstance(options[0], tuple):
            for i, o in enumerate(options):
                options[i] = (o,o)
        self.options = options
        if noneOption is not UNSET:
            self.noneOption = noneOption
            
    def pre_render(self, schemaType, data):
        return [string_converter(schemaType).fromType(data)]
    
    def convert(self, schemaType, data):
        if len(data) == 0:
            return []
        return string_converter(schemaType).toType(data[0])

    def selected(self, option, value, schemaType):
        if option[0] == self.convert(schemaType,[value]):
            return ' checked="checked"'
        else:
            return ''
    
    
class CheckboxMultiChoice(Widget):

    def __init__(self, options):
        if not isinstance(options[0], tuple):
            for i, o in enumerate(options):
                options[i] = (o,o)
        self.options = options
            
    def pre_render(self, schemaType, data):
        if data is None: 
            return []
        return [string_converter(schemaType.attr).fromType(d) for d in data]
    
    def convert(self, schemaType, data):
        return [string_converter(schemaType.attr).toType(d) for d in data]

    def checked(self, option, values, schemaType):
        if values is not None:
            typed_values = self.convert(schemaType,values)
        if values is not None and option[0] in typed_values:
            return ' checked="checked"'
        else:
            return ''


