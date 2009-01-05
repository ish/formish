"""
Commonly needed form widgets.
"""

__all__ = ['Input', 'Password', 'CheckedPassword', 'Hidden', 'TextArea',
        'Checkbox', 'DateParts', 'FileUpload', 'SelectChoice', 'RadioChoice',
        'CheckboxMultiChoice', 'SequenceDefault','CheckboxMultiChoiceTree']

from convertish.convert import string_converter,datetuple_converter, ConvertError
from formish.validation import *
from formish import dottedDict
from schemaish import type


UNSET = object()


class Widget(object):

    _template = None
    
    def __init__(self,**k):
        self.converter_options = k.get('converter_options',{})
        self.cssClass = k.get('cssClass', None)
        self.converttostring = True
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
    

    def pre_render(self, schemaType, data):
        data = string_converter(schemaType).fromType(data)
        if data is None:
            return ['']
        return [data]


    def convert(self, schemaType, data):
        return string_converter(schemaType).toType(data[0])


    def pre_parse_request(self, schemaType, data):
        return data


    def __repr__(self):
        return '<widget "%s">'%(self._template)




class Input(Widget):

    _template = 'Input'

    def __init__(self,**k):
        self.strip = k.pop('strip', True)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
            
    def convert(self, schemaType, data):
        if self.strip is True:
            d = data[0].strip()
        else:
            d = data[0]
        if not d:
            d = None
        return string_converter(schemaType).toType(d)

class Password(Widget):

    _template = 'Password'

    def __init__(self,**k):
        self.strip = k.pop('strip', True)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
            
    def convert(self, schemaType, data):
        if self.strip is True:
            d = data[0].strip()
        else:
            d = data[0]
        if not d:
            d = None
        return string_converter(schemaType).toType(d)

   
class CheckedPassword(Widget):

    _template = 'CheckedPassword'

    def __init__(self,**k):
        self.strip = k.pop('strip', True)
        self.cssClass = k.pop('cssClass', None)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
            
    def pre_render(self, schemaType, data):
        data = string_converter(schemaType).fromType(data)
        if data is None:
            return {'password': [''], 'confirm': ['']}
        return {'password': [password], 'confirm': [password]}
    
    def convert(self, schemaType, data):
        password = data['password'][0]
        confirm = data['confirm'][0]
        if self.strip is True:
            password = password.strip()
            if not password:
                password = None
            confirm = confirm.strip()
            if not confirm:
                confirm = None
        if password != confirm:
            raise ConvertError('Password did not match')
        return string_converter(schemaType).toType(password)


class Hidden(Widget):
    _template= 'Hidden'


class SequenceDefault(Widget):

    _template = 'SequenceDefault'

    def __init__(self,**k):
        Widget.__init__(self,**k)
        self.max = k.get('max')
        self.min = k.get('min')
        self.addremove = k.get('addremove', True)
        self.converttostring = False

    def pre_render(self, schemaType, data):
        return data

        
class TextArea(Widget):

    _template = 'TextArea'
    
    def __init__(self, **k):
        Widget.__init__(self,**k)
        self.cols = k.pop('cols', None)
        self.rows = k.pop('rows', None)
        self.strip = k.pop('strip', True)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = '\n'
    
    def pre_render(self, schemaType, data):
        data = string_converter(schemaType).fromType(data, converter_options=self.converter_options)
        if data is None:
            return ['']
        return [data]
    
    def convert(self, schemaType, data):
        if self.strip is True:
            d = data[0].strip()
        else:
            d = data[0]
        if not d:
            d = None
        return string_converter(schemaType).toType(d, converter_options=self.converter_options)

    
class Checkbox(Widget):

    _template = 'Checkbox'

    def convert(self, schemaType, data):
        if len(data) == 0:
            out='False'
        else:
            out='True'
        return string_converter(schemaType).toType(out)

    
class DateParts(Widget):

    _template = 'DateParts'
    
    def __init__(self, dayFirst=False, cssClass=None):
        Widget.__init__(self)
        self.cssClass = cssClass
        self.dayFirst = dayFirst
        
    def pre_render(self, schemaType, data):
        data = datetuple_converter(schemaType).fromType(data)
        if data is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        return {'year': [data[0]], 'month': [data[1]], 'day': [data[2]]}
    
    def convert(self, schemaType, data):
        year = data.get('year', [''])[0].strip()
        month = data.get('month', [''])[0].strip()
        day = data.get('day', [''])[0].strip()
        if year or month or day:
            date_parts = (year, month, day)
        else:
            date_parts = None
        return datetuple_converter(schemaType).toType(date_parts)
        

class FileUpload(Widget):
    """
    File upload widget.
    """

    _template = 'FileUpload'
    
    def __init__(self, fileHandler, showImagePreview=False, allowClear=True, cssClass=None,originalurl=None):
        """
        :arg filehandler: fileHandler is any object with the following methods:

            storeFile(self, f)
                where f is a file instance

            getUrlForFile(self, data)
                where data is the form item data or a path to a temporary file and
                is expected to return a URL to access the persisted or temporary
                data.

        :arg showImagePreview: a boolean that, if set, will include an image thumbnail with the widget
        :arg cssClass: extra css classes to apply to the widget
        :arg originalurl: a default url to 
        """
        Widget.__init__(self)
        self.cssClass = cssClass
        self.fileHandler = fileHandler
        self.showImagePreview = showImagePreview
        self.allowClear = allowClear
        self.originalurl = originalurl
    
    def pre_render(self, schemaType, data):
        if isinstance(data, type.File):
            self.default = self.fileHandler.urlfactory(data)
        elif data is not None:
            self.default = data
        else:
            self.default = ''
        return {'name': [self.default], 'default':[self.default]}
    
    def pre_parse_request(self, schemaType, data):
        if data.get('remove',[None])[0] is not None:
            # Removing the file
            data['name'] = ['']
            return data

        fs = data.get('file',[''])[0]
        if fs is not u'':
            # Storing an uploaded file
            name = self.fileHandler.store_file(fs)
            data['name'] = [name]
        return data
    
    def convert(self, schemaType, data):
        # XXX We could add a file converter that converts this to a string data?

        if data['name'] == ['']:
            return None
        elif data['name'] == data['default']:
            return type.File(None, None, None)
        else:
            filename = data['name'][0]
            path_for_file = self.fileHandler.get_path_for_file(filename)
            f = open(path_for_file)
            mimetype = self.fileHandler.get_mimetype(filename)
            fs = type.File(f, filename, mimetype)
            return fs



    
class SelectChoice(Widget):

    _template = 'SelectChoice'

    noneOption = ('', '- choose -')

    def __init__(self, options, noneOption=UNSET, cssClass=None):
        Widget.__init__(self)
        self.cssClass = cssClass
        self.options = _normalise_options(options)
        if noneOption is not UNSET:
            self.noneOption = noneOption
            
    def selected(self, option, value, schemaType):
        if option[0] == value:
            return ' selected="selected"'
        else:
            return ''

    def get_options(self, schemaType):
        options = []
        for value, label in self.options:
            options.append( (string_converter(schemaType).fromType(value),label) )
        return options
    
    def get_noneOption(self, schemaType):
        return (string_converter(schemaType).fromType(self.noneOption[0]), self.noneOption[1])
    

class RadioChoice(Widget):

    _template = 'RadioChoice'

    noneOption = ('', '- choose -')

    def __init__(self, options, noneOption=UNSET, cssClass=None):
        Widget.__init__(self)
        self.cssClass = cssClass
        self.options = _normalise_options(options)
        if noneOption is not UNSET:
            self.noneOption = noneOption
            
    def convert(self, schemaType, data):
        if not data:
            data = ['']
        return super(RadioChoice, self).convert(schemaType, data)

    def selected(self, option, value, schemaType):
        if option[0] == self.convert(schemaType,[value]):
            return ' checked="checked"'
        else:
            return ''
    
    
class CheckboxMultiChoice(Widget):

    _template = 'CheckboxMultiChoice'

    def __init__(self, options, cssClass=None):
        self.options = _normalise_options(options)
        Widget.__init__(self,cssClass=cssClass)
            
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

class CheckboxMultiChoiceTree(Widget):

    _template = 'CheckboxMultiChoiceTree'

    def __init__(self, options, cssClass=None):
        self.options = options
        self.optiontree = dottedDict._getDictFromDottedKeyDict(dict(options),noexcept=True) 
        Widget.__init__(self,cssClass=cssClass)
            
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
        
        
def _normalise_options(options):
    """
    Return a sequence of (value, label) pairs for all options where each option
    can be a scalar value or a (value, label) tuple.
    """
    out = []
    if hasattr(options, '__call__'):
        options = options()
    for option in options:
        if isinstance(option, tuple):
            out.append( option )
        else:
            out.append( (option, str(option)) )
    return out

