"""
Commonly needed form widgets.
"""

__all__ = ['Input', 'Password', 'CheckedPassword', 'Hidden', 'TextArea',
        'Checkbox', 'DateParts', 'FileUpload', 'SelectChoice','SelectWithOtherChoice','RadioChoice',
        'CheckboxMultiChoice', 'SequenceDefault','CheckboxMultiChoiceTree']

from convertish.convert import string_converter, \
        datetuple_converter,ConvertError
from schemaish.type import File as SchemaFile
from formish import dottedDict


UNSET = object()


class Widget(object):
    """
    Base class for widgets
    """

    _template = None
    
    def __init__(self, **k):
        self.converter_options = k.get('converter_options', {})
        self.css_class = k.get('css_class', None)
        self.converttostring = True
        self.empty = k.get('empty', None)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
    

    def pre_render(self, schema_type, data):
        """
        Before the widget is rendered, the data is converted to a string
        format.If the data is None then we return an empty string. The sequence
        is request data representation.
        """
        if data is None:
            return ['']
        string_data = string_converter(schema_type).from_type(data)
        return [string_data]


    def pre_parse_request(self, schema_type, request_data, full_request_data):
        """
        Prior to convert being run, we have a chance to munge the data. This is
        only used by file upload at the moment
        """
        return request_data


    def convert(self, schema_type, request_data):
        """
        after the form has been submitted, the request data is converted into
        to the schema type.
        """
        string_data = request_data[0]
        if string_data == '':
            return self.empty
        return string_converter(schema_type).to_type(string_data)

    def __repr__(self):
        return '<widget "%s">'% (self._template)

    def __call__(self, field):
        return field.form.renderer('/formish/widgets/%s.html'%self._template, {'f':field})




class Input(Widget):
    """
    Basic input widget type, used for text input
    """

    _template = 'Input'

    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

    def convert(self, schema_type, request_data):
        """
        Default to stripping whitespace
        """
        string_data = request_data[0]
        if self.strip is True:
            string_data = string_data.strip()
        if string_data == '':
            return self.empty
        return string_converter(schema_type).to_type(string_data)



class Password(Input):
    """
    Password widget is a basic input type but using password html input type
    """
    _template = 'Password'


   
class CheckedPassword(Input):
    """
    Checked Password ensures that the password has been entered twice
    """

    _template = 'CheckedPassword'

    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.css_class = k.pop('css_class', None)
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
            
    def pre_render(self, schema_type, data):
        """
        Extract both the password and confirm fields
        """
        string_data = string_converter(schema_type).from_type(data)
        if string_data is None:
            return {'password': [''], 'confirm': ['']}
        return {'password': [string_data], 'confirm': [string_data]}
    
    def convert(self, schema_type, request_data):
        """
        Check the password and confirm match (when stripped)
        """
        password = request_data['password'][0]
        confirm = request_data['confirm'][0]
        if self.strip is True:
            password = password.strip()
            confirm = confirm.strip()
        if password != confirm:
            raise ConvertError('Password did not match')
        if password == '':
            return self.empty
        return string_converter(schema_type).to_type(password)



class Hidden(Input):
    """
    Basic input but using a hidden html input field
    """
    _template = 'Hidden'



class SequenceDefault(Widget):
    """
    Sequence handling widget - used by default for schema sequences

    :arg min: minimum number of sequence items to show
    :arg max: maximum number of sequence items to show
    :arg addremove: boolean whether to show the addremove buttons (jquery
        activated)
    """

    _template = 'SequenceDefault'

    def __init__(self, **k):
        Widget.__init__(self, **k)
        self.max = k.get('max')
        self.min = k.get('min')
        self.addremove = k.get('addremove', True)
        self.sortable = k.get('sortable', True)
        self.converttostring = False

    def pre_render(self, schema_type, data):
        """
        Short circuits the usual pre_render
        """
        return data

        
class TextArea(Input):
    """
    Textarea input field

    :arg cols: set the cols attr on the textarea element
    :arg rows: set the cols attr on the textarea element
    """

    _template = 'TextArea'
    
    def __init__(self, **k):
        Input.__init__(self, **k)
        self.cols = k.pop('cols', None)
        self.rows = k.pop('rows', None)
        self.strip = k.pop('strip', True)
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = '\n'
    
    def pre_render(self, schema_type, data):
        """
        We're using the converter options to allow processing sequence data
        using the csv module
        """
        string_data = string_converter(schema_type).from_type(data, \
            converter_options=self.converter_options)
        if string_data is None:
            return ['']
        return [string_data]
    
    def convert(self, schema_type, request_data):
        """
        We're using the converter options to allow processing sequence data
        using the csv module
        """
        string_data = request_data[0]
        if self.strip is True:
            string_data = string_data.strip()
        if string_data == '':
            return self.empty
        return string_converter(schema_type).to_type(string_data,
            converter_options=self.converter_options)

    
class Checkbox(Widget):
    """
    Checkbox widget, defaults to True or False
    """

    _template = 'Checkbox'

    def convert(self, schema_type, request_data):
        """
        If the request data exists, then we treat this as True
        """
        if len(request_data) == 0:
            out_string = 'False'
        else:
            out_string = 'True'
        return string_converter(schema_type).to_type(out_string)

    
class DateParts(Widget):
    """
    Simple three part date entry form
    """

    _template = 'DateParts'
    
    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.day_first = k.pop('day_first', None)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

        
    def pre_render(self, schema_type, data):
        """
        Convert to date parts
        """
        dateparts = datetuple_converter(schema_type).from_type(data)
        if dateparts is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        return {'year': [dateparts[0]],
                'month': [dateparts[1]],
                'day': [dateparts[2]]}
    
    def convert(self, schema_type, request_data):
        """
        Pull out the parts and convert
        """
        year = request_data.get('year', [''])[0].strip()
        month = request_data.get('month', [''])[0].strip()
        day = request_data.get('day', [''])[0].strip()
        if year or month or day:
            date_parts = (year, month, day)
        else:
            return self.empty
        return datetuple_converter(schema_type).to_type(date_parts)
        

class FileUpload(Widget):
    """
    File upload widget.
    """

    _template = 'FileUpload'
    
    def __init__(self, filehandler, show_image_preview=False, \
                 allow_clear=True, css_class=None, originalurl=None):
        """
        :arg filehandler: filehandler is any object with the following methods:

            storeFile(self, f)
                where f is a file instance

            getUrlForFile(self, data)
                where data is the form item data or a path to a temporary file
                and is expected to return a URL to access the persisted or
                temporary data.

        :arg show_image_preview: a boolean that, if set, will include an image
            thumbnail with the widget
        :arg css_class: extra css classes to apply to the widget
        :arg originalurl: a default url to 
        """
        Widget.__init__(self)
        self.css_class = css_class
        self.filehandler = filehandler
        self.show_image_preview = show_image_preview
        self.allow_clear = allow_clear
        self.originalurl = originalurl
    
    def pre_render(self, schema_type, data):
        """
        We use the url factory to get an identifier for the file which we use
        as the name. We also store it in the 'default' field so we can check if
        something has been uploaded (the identifier doesn't match the name)
        """
        if isinstance(data, SchemaFile):
            self.default = self.filehandler.urlfactory(data)
        elif data is not None:
            self.default = data
        else:
            self.default = ''
        return {'name': [self.default], 'default':[self.default]}
    
    def pre_parse_request(self, schema_type, data, full_request_data):
        """
        File uploads are wierd; in out case this means assymetric. We store the
        file in a temporary location and just store an identifier in the field.
        This at least makes the file look symmetric.
        """
        if data.get('remove', [None])[0] is not None:
            # Removing the file
            data['name'] = ['']
            return data

        fieldstorage = data.get('file', [''])[0]
        if fieldstorage is not u'':
            # Storing an uploaded file
            name = self.filehandler.store_file(fieldstorage)
            data['name'] = [name]
        return data
    
    def convert(self, schema_type, request_data):
        """
        Creates a File object if possible
        """
        # XXX We could add a file converter that converts this to a string data?

        if request_data['name'] == ['']:
            return None
        elif request_data['name'] == request_data['default']:
            return SchemaFile(None, None, None)
        else:
            filename = request_data['name'][0]
            path_for_file = self.filehandler.get_path_for_file(filename)
            filepath = open(path_for_file)
            mimetype = self.filehandler.get_mimetype(filename)
            filetype = SchemaFile(filepath, filename, mimetype)
            return filetype



    
class SelectChoice(Widget):
    """
    Html Select element
    """

    _template = 'SelectChoice'

    none_option = ('', '- choose -')

    def __init__(self, options, **k):
        """
        :arg options: either a list of values ``[value,]`` where value is used for the label or a list of tuples of the form ``[(value, label),]``
        :arg none_option: a tuple of ``(value, label)`` to use as the unselected option
        :arg css_class: a css class to apply to the field
        """
        none_option = k.pop('none_option', UNSET)
        if none_option is not UNSET:
            self.none_option = none_option
        Widget.__init__(self, **k)
        self.options = _normalise_options(options)
            
    def selected(self, option, value, schema_type):
        """
        Check the value passed matches the actual value
        """
        if value and option[0] == self.convert(schema_type, [value]):
            return ' selected="selected"'
        else:
            return ''

    def get_options(self, schema_type):
        """
        Return all of the options for the widget
        """
        options = []
        for value, label in self.options:
            options.append(
        (string_converter(schema_type).from_type(value),label)
            )
        return options
    
    def get_none_option_value(self, schema_type):
        """
        Get the default option (the 'unselected' option)
        """
        return string_converter(schema_type).from_type(
            self.none_option[0])
    
class SelectWithOtherChoice(SelectChoice):
    """
    Html Select element
    """
    _template = 'SelectWithOtherChoice'

    other_option = ('...', 'Other ...')

    def __init__(self, options, **k):
        other_option = k.pop('other_option', UNSET)
        if other_option is not UNSET:
            self.other_option = other_option
        self.strip = k.pop('strip',True)
        SelectChoice.__init__(self, options, **k)

    def pre_render(self, schema_type, data):
        """
        populate the other choice if needed
        """
        string_data = string_converter(schema_type).from_type(data)
        if string_data in [value for value, label in self.options]:
            return {'select': ['...'], 'other': [string_data]}
        return {'select': [string_data], 'other': ['']}

    def convert(self, schema_type, request_data):
        """
        Check to see if we need to use the 'other' value
        """
        select = request_data['select'][0]
        other = request_data['other'][0]
        if self.strip:
            other = other.strip()
        if select == '...':
            value = other
        else:
            if other != '':
                raise ConvertError('You entered text in the box but had not selected "%s" in the drop down. We have now selected it for you. please check and resubmit'%self.other_option[1])
            value = select
        if value == '':
            return self.empty
        return string_converter(schema_type).to_type(value)

    def get_other_option(self, schema_type):
        """
        Get the other option
        """
        return (string_converter(schema_type).from_type(
            self.other_option[0]), self.other_option[1])
            
    def selected(self, option, value, schema_type):
        """
        Check the value passed matches the actual value
        """
        if option[0] == '...' and value not in [value for value, label in self.options]:
            return ' selected="selected"'
        if option[0] == value:
            return ' selected="selected"'
        return ''

class RadioChoice(Widget):
    """
    Radio choice html element
    """

    _template = 'RadioChoice'

    none_option = ('', '- choose -')

    def __init__(self, options, **k):
        none_option = k.pop('none_option', UNSET)
        if none_option is not UNSET:
            self.none_option = none_option
        Widget.__init__(self, **k)
        self.options = _normalise_options(options)
            
    def convert(self, schema_type, request_data):
        """
        If we don't have a choice, set a blank value
        """

        if not request_data:
            string_data = ''
        else:
            string_data = request_data[0]

        if string_data == '':
            return self.empty

        return string_converter(schema_type).to_type(string_data)

    def selected(self, option, value, schema_type):
        """
        Check if the currently rendering input is the same as the value
        """
        if value and option[0] == self.convert(schema_type, [value]):
            return ' checked="checked"'
        else:
            return ''
    
    def get_none_option_value(self, schema_type):
        """
        Get the default option (the 'unselected' option)
        """
        none_val = string_converter(schema_type).from_type(
            self.none_option[0])
        return none_val
    
class CheckboxMultiChoice(Widget):
    """
    Checkbox multi choice is a set of checkboxes that for a sequence of data
    """

    _template = 'CheckboxMultiChoice'

    def __init__(self, options, css_class=None):
        self.options = _normalise_options(options)
        Widget.__init__(self, css_class=css_class)
            
    def pre_render(self, schema_type, data):
        """
        Iterate over the data, converting each one
        """
        if data is None: 
            return []
        return [string_converter(schema_type.attr).from_type(d) for d in data]
    
    def convert(self, schema_type, request_data):
        """
        Iterating to convert back to the source data
        """
        return [string_converter(schema_type.attr).to_type(d) \
                for d in request_data]

    def checked(self, option, values, schema_type):
        """
        For each value, convert it and check to see if it matches the input data
        """
        if values is not None:
            typed_values = self.convert(schema_type, values)
        if values is not None and option[0] in typed_values:
            return ' checked="checked"'
        else:
            return ''

class CheckboxMultiChoiceTree(Widget):
    """
    A more complicated checkbox select that
    """

    _template = 'CheckboxMultiChoiceTree'

    def __init__(self, options, cssClass=None):
        self.options = options
        self.optiontree = dottedDict._getDictFromDottedKeyDict(dict(options),noexcept=True) 
        Widget.__init__(self,cssClass=cssClass)
            
    def pre_render(self, schema_type, data):
        if data is None: 
            return []
        return [string_converter(schema_type.attr).from_type(d) for d in data]
    
    def convert(self, schema_type, data):
        return [string_converter(schema_type.attr).to_type(d) for d in data]

    def checked(self, option, values, schema_type):
        if values is not None:
            typed_values = self.convert(schema_type,values)
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

