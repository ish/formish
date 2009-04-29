"""
Commonly needed form widgets.
"""

__all__ = ['Input', 'Password', 'CheckedPassword', 'Hidden', 'TextArea',
        'Checkbox', 'DateParts', 'FileUpload', 'SelectChoice','SelectWithOtherChoice','RadioChoice',
        'CheckboxMultiChoice', 'SequenceDefault','CheckboxMultiChoiceTree', 'Grid']

from convertish.convert import string_converter, \
        datetuple_converter,ConvertError
from schemaish.type import File as SchemaFile
from dottedish import get_dict_from_dotted_dict
import uuid


UNSET = object()


class Widget(object):
    """
    Base class for widgets
    """
    
    type = None
    template = None
    
    def __init__(self, **k):
        self.css_class = k.get('css_class', None)
        self.converttostring = True
        self.empty = k.get('empty', None)
        self.converter_options = k.get('converter_options', {})
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
    

    def to_request_data(self, schema_type, data):
        """
        Before the widget is rendered, the data is converted to a string
        format.If the data is None then we return an empty string. The sequence
        is request data representation.
        """
        if data is None:
            return ['']
        string_data = string_converter(schema_type).from_type(data)
        return [string_data]


    def pre_parse_incoming_request_data(self, schema_type, request_data, full_request_data):
        """
        Prior to convert being run, we have a chance to munge the data. This is
        only used by file upload at the moment
        """
        return request_data


    def from_request_data(self, schema_type, request_data):
        """
        after the form has been submitted, the request data is converted into
        to the schema type.
        """
        string_data = request_data[0]
        if string_data == '':
            return self.empty
        return string_converter(schema_type).to_type(string_data)



    def __call__(self, field):
        return field.form.renderer('/formish/widgets/%s.html'%self.template, {'f':field})

    def __repr__(self):
        attributes = []
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))



class Input(Widget):
    """
    Basic input widget type, used for text input
    """

    type = 'Input'
    template = 'field.Input'

    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

    def from_request_data(self, schema_type, request_data):
        """
        Default to stripping whitespace
        """
        string_data = request_data[0]
        if self.strip is True:
            string_data = string_data.strip()
        if string_data == '':
            return self.empty
        return string_converter(schema_type).to_type(string_data)

    def __repr__(self):
        attributes = []
        if self.strip is False:
            attributes.append('strip=%r'%self.strip)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))


class Password(Input):
    """
    Password widget is a basic input type but using password html input type
    """
    type = 'Password'
    template = 'field.Password'


   
class CheckedPassword(Input):
    """
    Checked Password ensures that the password has been entered twice
    """

    type = 'CheckedPassword'
    template = 'field.CheckedPassword'

    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.css_class = k.pop('css_class', None)
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
            
    def to_request_data(self, schema_type, data):
        """
        Extract both the password and confirm fields
        """
        string_data = string_converter(schema_type).from_type(data)
        if string_data is None:
            return {'password': [''], 'confirm': ['']}
        return {'password': [string_data], 'confirm': [string_data]}
    
    def from_request_data(self, schema_type, request_data):
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

    def __repr__(self):
        attributes = []
        if self.strip is False:
            attributes.append('strip=%r'%self.strip)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))


class Hidden(Input):
    """
    Basic input but using a hidden html input field
    """
    type = 'Hidden'
    template = 'field.Hidden'



class SequenceDefault(Widget):
    """
    Sequence handling widget - used by default for schema sequences

    :arg min: minimum number of sequence items to show
    :arg max: maximum number of sequence items to show
    :arg addremove: boolean whether to show the addremove buttons (jquery
        activated)
    """

    type = 'SequenceDefault'
    template = 'sequence.-'

    def __init__(self, **k):
        Widget.__init__(self, **k)
        self.max = k.get('max')
        self.min = k.get('min')
        self.addremove = k.get('addremove', True)
        self.sortable = k.get('sortable', True)
        self.converttostring = False

    def to_request_data(self, schema_type, data):
        """
        Short circuits the usual to_request_data
        """
        return data

    def __repr__(self):
        attributes = []
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)
        if self.min:
            attributes.append('min=%r'%self.min)
        if self.max:
            attributes.append('max=%r'%self.max)
        if self.addremove:
            attributes.append('addremove=%r'%self.addremove)
        if self.sortable:
            attributes.append('sortable=%r'%self.sortable)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
        
class TextArea(Input):
    """
    Textarea input field

    :arg cols: set the cols attr on the textarea element
    :arg rows: set the cols attr on the textarea element
    """

    type = 'TextArea'
    template = 'field.TextArea'
    
    def __init__(self, **k):
        self.cols = k.pop('cols', None)
        self.rows = k.pop('rows', None)
        self.strip = k.pop('strip', True)
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = '\n'
    
    def to_request_data(self, schema_type, data):
        """
        We're using the converter options to allow processing sequence data
        using the csv module
        """
        string_data = string_converter(schema_type).from_type(data, \
            converter_options=self.converter_options)
        if string_data is None:
            return ['']
        return [string_data]
    
    def from_request_data(self, schema_type, request_data):
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

    def __repr__(self):
        attributes = []
        if self.strip is False:
            attributes.append('strip=%r'%self.strip)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))

class Grid(Input):
    """
    Grid input field
    """

    type = 'Grid'
    template = 'field.Grid'
    
    def __init__(self, **k):
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = '\n'
        self.converttostring = False
    
    def to_request_data(self, schema_type, data):
        string_data = string_converter(schema_type).from_type(data, \
            converter_options=self.converter_options)
        return [string_data]
    
    def from_request_data(self, schema_type, request_data):
        string_data = request_data[0]
        return string_converter(schema_type).to_type(string_data,
            converter_options=self.converter_options)

    def __repr__(self):
        attributes = []
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
    
class Checkbox(Widget):
    """
    Checkbox widget, defaults to True or False
    """

    type = 'Checkbox'
    template = 'field.Checkbox'

    def from_request_data(self, schema_type, request_data):
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

    type = 'DateParts'
    template = 'field.DateParts'
    
    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.day_first = k.pop('day_first', None)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

        
    def to_request_data(self, schema_type, data):
        """
        Convert to date parts
        """
        dateparts = datetuple_converter(schema_type).from_type(data)
        if dateparts is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        return {'year': [dateparts[0]],
                'month': [dateparts[1]],
                'day': [dateparts[2]]}
    
    def from_request_data(self, schema_type, request_data):
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

    def __repr__(self):
        attributes = []
        if self.strip is False:
            attributes.append('strip=%r'%self.strip)
        if self.day_first is not None:
            attributes.append('day_first=%r'%self.day_first)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
        

class FileUpload(Widget):
    """
    File upload widget.
    """

    type = 'FileUpload'
    template = 'field.FileUpload'
    
    def __init__(self, filestore, show_file_preview=True, show_download_link=False, \
                 show_image_thumbnail=False, url_base=None, \
                 css_class=None, image_thumbnail_default=None, url_ident_factory=None):
        """
        :arg filestore: filestore is any object with the following methods:

            storeFile(self, f)
                where f is a file instance

        :arg show_image_thumbnail: a boolean that, if set, will include an image
            thumbnail with the widget
        :arg css_class: extra css classes to apply to the widget
        :arg image_thumbnail_default: a default url to 
        XXX image_thumbnail_default -> default_image 
        XXX allow_clear -> allow_delete 
        XXX url_ident_factory -> filestore_key_factory
        """
        Widget.__init__(self)
        self.filestore = filestore
        self.show_image_thumbnail = show_image_thumbnail
        self.image_thumbnail_default = image_thumbnail_default
        if url_base is None:
            self.url_base = '/filehandler'
        else:
            self.url_base = url_base
        self.show_download_link = show_download_link
        self.show_file_preview = show_file_preview
        if url_ident_factory is not None:
            self.url_ident_factory = url_ident_factory
        else:
            self.url_ident_factory = lambda i: i.filename

    def __repr__(self):
        attributes = []
        attributes.append('filestore=%r'%self.filestore)
        if self.show_image_thumbnail == True:
            attributes.append('show_image_thumbnail=True')
        if self.image_thumbnail_default:
            attributes.append('image_thumbnail_default=%r'%self.image_thumbnail_default)
        if self.url_base != "/filehandler":
            attributes.append('url_base=%r'%self.url_base)
        if self.show_download_link == True:
            attributes.append('show_download_link=True')
        if self.show_file_preview == False:
            attributes.append('show_file_preview=False')
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
          

    def urlfactory(self, data):
        if not data:
            return self.image_thumbnail_default
        if isinstance(data, SchemaFile):
            key = self.url_ident_factory(data)
        else:
            key = data
        return '%s/%s' % (self.url_base, key)
    
    def to_request_data(self, schema_type, data):
        """
        We use the url factory to get an identifier for the file which we use
        as the name. We also store it in the 'default' field so we can check if
        something has been uploaded (the identifier doesn't match the name)
        """
        mimetype = ''
        if isinstance(data, SchemaFile):
            default = self.url_ident_factory(data)
            mimetype = data.mimetype
        elif data is not None:
            default = data
        else:
            default = ''
        return {'name': [default], 'default':[default], 'mimetype':[mimetype]}
    
    def pre_parse_incoming_request_data(self, schema_type, data, full_request_data):
        """
        File uploads are wierd; in out case this means assymetric. We store the
        file in a temporary location and just store an identifier in the field.
        This at least makes the file look symmetric.
        """
        if data.get('remove', [None])[0] is not None:
            data['name'] = ['']
            data['mimetype'] = ['']
            return data

        fieldstorage = data.get('file', [''])[0]
        if getattr(fieldstorage,'file',None):
            filename = '%s-%s'%(uuid.uuid4().hex,fieldstorage.filename)
            self.filestore.put(filename, fieldstorage.file, fieldstorage.type, uuid.uuid4().hex)
            data['name'] = [filename]
            data['mimetype'] = [fieldstorage.type]
        return data
    
    def from_request_data(self, schema_type, request_data):
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
            try:
                content_type, cache_tag, f = self.filestore.get(filename)
            except KeyError:
                return None
            return SchemaFile(f, filename, content_type)

    
class SelectChoice(Widget):
    """
    Html Select element
    """

    type = 'SelectChoice'
    template = 'field.SelectChoice'

    none_option = (None, '- choose -')

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
        if value == '':
            v = self.empty
        else:
            v = value
        if option[0] == v:
            return ' selected="selected"'
        else:
            return ''

    def get_options(self, schema_type):
        """
        Return all of the options for the widget
        """
        options = []
        for value, label in self.options:
            if value == self.empty:
                options.append( ('',label) )
            else:
                options.append( (string_converter(schema_type).from_type(value),label) )
        return options
    
    def get_none_option_value(self, schema_type):
        """
        Get the default option (the 'unselected' option)
        """
        none_option =  string_converter(schema_type).from_type(self.none_option[0])
        if none_option is self.empty:
            return ''
        return none_option

    def __repr__(self):
        attributes = []
        attributes.append('options=%s'%repr(self.options))
        if self.none_option is not UNSET:
            attributes.append('none_option=%s'%repr(self.none_option))
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
    
class SelectWithOtherChoice(SelectChoice):
    """
    Html Select element
    """
    type = 'SelectWithOtherChoice'
    template = 'field.SelectWithOtherChoice'

    other_option = ('...', 'Other ...')

    def __init__(self, options, **k):
        other_option = k.pop('other_option', UNSET)
        if other_option is not UNSET:
            self.other_option = other_option
        self.strip = k.pop('strip',True)
        SelectChoice.__init__(self, options, **k)

    def to_request_data(self, schema_type, data):
        """
        populate the other choice if needed
        """
        string_data = string_converter(schema_type).from_type(data)
        if string_data in [value for value, label in self.options]:
            return {'select': ['...'], 'other': [string_data]}
        return {'select': [string_data], 'other': ['']}

    def from_request_data(self, schema_type, request_data):
        """
        Check to see if we need to use the 'other' value
        """
        select = request_data['select'][0]
        other = request_data['other'][0]
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
        """ Get the other option """
        return (string_converter(schema_type).from_type( self.other_option[0]), self.other_option[1] )
            
    def selected(self, option, value, schema_type):
        """ Check the value passed matches the actual value """
        if option[0] == '...' and value not in [value for value, label in self.get_options(schema_type)]:
            return ' selected="selected"'
        # Map the empty value
        if value == '':
            v = self.empty
        else:
            v = value
        # Check for selected
        if option[0] == v:
            return ' selected="selected"'
        else:
            return ''

    def __repr__(self):
        attributes = []
        attributes.append('options=%r'%self.options)
        if self.none_option is not UNSET:
            attributes.append('none_option=%r'%list(self.none_option))
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))

class RadioChoice(SelectChoice):
    """
    Radio choice html element
    """

    type = 'RadioChoice'
    template = 'field.RadioChoice'

    none_option = (None, '- choose -')

    def selected(self, option, value, schema_type):
        """
        Check if the currently rendering input is the same as the value
        """
        if value == '':
            v = self.empty
        else:
            v = value
        if option[0] == v:
            return ' checked="checked"'
        else:
            return ''

    def from_request_data(self, schema_type, request_data):
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
    
    def get_none_option_value(self, schema_type):
        """
        Get the default option (the 'unselected' option)
        """
        none_option =  string_converter(schema_type).from_type(self.none_option[0])
        if none_option is self.empty:
            return ''
        return none_option

    def __repr__(self):
        attributes = []
        attributes.append('options=%r'%self.options)
        if self.none_option is not UNSET:
            attributes.append('none_option=%r'%list(self.none_option))
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
    
class CheckboxMultiChoice(Widget):
    """
    Checkbox multi choice is a set of checkboxes that for a sequence of data
    """

    type = 'CheckboxMultiChoice'
    template = 'field.CheckboxMultiChoice'

    def __init__(self, options, css_class=None):
        self.options = _normalise_options(options)
        Widget.__init__(self, css_class=css_class)
            
    def to_request_data(self, schema_type, data):
        """
        Iterate over the data, converting each one
        """
        if data is None: 
            return []
        return [string_converter(schema_type.attr).from_type(d) for d in data]
    
    def from_request_data(self, schema_type, request_data):
        """
        Iterating to convert back to the source data
        """
        return [string_converter(schema_type.attr).to_type(d) \
                for d in request_data]

    def checked(self, option, values, schema_type):
        """
        For each value, convert it and check to see if it matches the input data
        """
        if values is None:
            return ''
        cvs = []
        for v in values:
            try:
                cvs.append( string_converter(schema_type.attr).to_type(v) )
            except ConvertError:
                continue
        if option[0] in cvs:
            return ' checked="checked"'
        else:
            return ''

    def __repr__(self):
        attributes = []
        attributes.append('options=%r'%self.options)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))

def get_parent(segments):
    if len(segments) == 1:
        return ''
    else:
        return '.'.join(segments[:-1])

def mktree(options):
    last_segments_len = 1
    root = {'': {'data':('root', 'Root'), 'children':[]} }
    for id, label in options:
        segments = id.split('.')
        parent = get_parent(segments)
        root[id] = {'data': (id, label), 'children':[]}
        root[parent]['children'].append(root[id])
    return root['']


class CheckboxMultiChoiceTree(Widget):
    """
    A more complicated checkbox select that
    """

    type = 'CheckboxMultiChoiceTree'
    template = 'field.CheckboxMultiChoiceTree'

    def __init__(self, options, cssClass=None):
        self.options = options
        self.optiontree = mktree(options)
        Widget.__init__(self,cssClass=cssClass)
            
    def to_request_data(self, schema_type, data):
        if data is None: 
            return []
        return [string_converter(schema_type.attr).from_type(d) for d in data]
    
    def from_request_data(self, schema_type, data):
        return [string_converter(schema_type.attr).to_type(d) for d in data]

    def checked(self, option, values, schema_type):
        if values is not None:
            typed_values = self.convert(schema_type,values)
        if values is not None and option[0] in typed_values:
            return ' checked="checked"'
        else:
            return ''        

    def __repr__(self):
        attributes = []
        attributes.append('options=%r'%self.options)
        if self.none_option is not UNSET:
            attributes.append('none_option=%r'%self.none_option)
        if self.strip is False:
            attributes.append('strip=%s'%self.strip)
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))
        
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

