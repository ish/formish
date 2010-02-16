"""
Commonly needed form widgets.
"""

__all__ = ['Input', 'Password', 'CheckedPassword', 'CheckedInput', 'Hidden', 'TextArea',
        'Checkbox', 'DateParts', 'FileUpload', 'SelectChoice','SelectWithOtherChoice','RadioChoice',
        'CheckboxMultiChoice', 'SequenceDefault','CheckboxMultiChoiceTree', 'Grid']

from convertish.convert import string_converter, \
        datetuple_converter,ConvertError
from schemaish.type import File as SchemaFile
import uuid

from formish import util
from formish.filestore import CachedTempFilestore
from validatish import Invalid


UNSET = object()

def recursive_convert_sequences(data):
    """
    recursively applies ``convert_sequences``
    """
    if not hasattr(data,'keys'):
        return data
    if len(data.keys()) == 0:
        return data
    try:
        int(data.keys()[0])
    except ValueError:
        tmp = {}
        for key, value in data.items():
            tmp[key] = recursive_convert_sequences(value)
        return tmp
    intkeys = []
    for key in data.keys():
        intkeys.append(int(key))
    intkeys.sort()
    out = []
    for key in intkeys:
        out.append(recursive_convert_sequences(data[str(key)]))
    return out


class Widget(object):
    """
    Base class for widgets
    """
    
    type = None
    template = None
    
    def __init__(self, **k):
        self.css_class = k.get('css_class', None)
        # what to show on the form (or embed in select) if the input is empty, this is specific to Input type fields
        self.none_value = k.get('none_value','')
        # what value is considered 'empty' for input data (i.e. what value to
        # use on the data side if the form is submitted with nothing in it)
        self.empty = k.get('empty',None)
        # Should we show and empty input box if the incoming data matches empty
        self.roundtrip_empty = k.get('roundtrip_empty',False)
        self.readonly = k.get('readonly',False)
        self.converter_options = k.get('converter_options', {})
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','
        # if none_value is something different e.g. 999, do we show 999 or '' when reshowing form.

    def none_value_as_request_data(self, field):
        return [self.none_value]

    def to_request_data(self, field, data):
        """
        Before the widget is rendered, the data is converted to a string
        format.If the data is None then we return an empty string. The sequence
        is request data representation.
        """
        if data is None or (data == self.empty and self.roundtrip_empty is True):
            return self.none_value_as_request_data(field)
        string_data = string_converter(field.attr).from_type(data, converter_options=self.converter_options)
        return [string_data]

    def pre_parse_incoming_request_data(self, field, request_data):
        """
        Prior to convert being run, we have a chance to munge the data. This is
        only used by file upload at the moment
        """
        return request_data or self.none_value_as_request_data(field)

    def from_request_data(self, field, request_data):
        """
        after the form has been submitted, the request data is converted into
        to the schema type.
        """
        if request_data == self.none_value_as_request_data(field):
            data = self.empty
        else:
            data = string_converter(field.attr).to_type(request_data[0], converter_options=self.converter_options)
        return data

    def __repr__(self):
        attributes = []
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))


class Container(Widget):
    type = 'Container'


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

    def from_request_data(self, field, request_data):
        """
        Default to stripping whitespace
        """
        if self.strip is True:
            request_data = [request_data[0].strip()]
        return super(Input, self).from_request_data(field, request_data)

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


   



class CheckedInput(Input):
    """
    Checked Input ensures that the input has been entered twice
    """

    type = 'CheckedInput'
    template = 'field.CheckedInput'
    confirm_label = None
    mismatch_message = 'Fields did not match'
    default_value = {'input': [''], 'confirm': ['']}

    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.css_class = k.pop('css_class', None)
        self.confirm_label = k.pop('confirm_label',None)
        Input.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

    def none_value_as_request_data(self, field):
        return {'input': [self.none_value], 'confirm': [self.none_value]}
            
    def to_request_data(self, field, data):
        """
        Extract both the input and confirm fields
        """
        if data is None or (data == self.empty and self.roundtrip_empty is True):
            return self.none_value_as_request_data(field)
        string_data = string_converter(field.attr).from_type(data)
        return {'input': [string_data], 'confirm': [string_data]}

    def from_request_data(self, field, request_data):
        """
        Check the input and confirm match (when stripped)
        """
        if request_data == self.none_value_as_request_data(field):
            return self.empty
        input = request_data['input'][0]
        confirm = request_data['confirm'][0]
        if self.strip is True:
            input = input.strip()
            confirm = confirm.strip()
        if input != confirm:
            raise ConvertError(self.mismatch_message)
        if input == self.none_value:
            return self.empty
        return string_converter(field.attr).to_type(input)

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


class CheckedPassword(CheckedInput):
    """
    Checked Password ensures that the password has been entered twice
    """

    type = 'CheckedPassword'
    template = 'field.CheckedPassword'
    mismatch_message = 'Passwords did not match'


class Hidden(Input):
    """
    Basic input but using a hidden html input field
    """
    type = 'Hidden'
    template = 'field.Hidden'


def default_empty_checker(v):
    try:
        _default_empty_checker(v)
    except ValueError:
        return False
    return True


def _default_empty_checker(v):
    if v == None:
        return
    if isinstance(v, basestring):
        if v != '':
            raise ValueError
        return
    if hasattr(v, 'values'):
        for i in v.values():
            _default_empty_checker(i) 
        return
    else:
        try:
            for i in v: 
                _default_empty_checker(i)
        except TypeError:
            raise ValueError

class SequenceDefault(Container):
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
        self.empty_checker = k.get('empty_checker',default_empty_checker)
        self.min_start_fields = k.get('min_start_fields',1)
        self.min_empty_start_fields = k.get('min_empty_start_fields',0)
        self.batch_add_count = k.get('batch_add_count',1)
        self.addremove = k.get('addremove', True)
        self.sortable = k.get('sortable', True)
        # you can specify strip_empty but if not then we only strip if you can add and remove items
        self.strip_empty = k.get('strip_empty',self.addremove)

    def to_request_data(self, field, data):
        """
        Short circuits the usual to_request_data
        """
        request_data = {}
        if data is None:
            data = {}
        for f in field.fields:
            try:
                try:
                    d = data[int(f.nodename)]
                except (KeyError, IndexError):
                    d = None
                request_data[f.nodename] = f.widget.to_request_data(f, d)
            except Invalid, e:
                f.errors[f.name] = e
                raise
        return request_data

    def pre_parse_incoming_request_data(self, field, request_data):
        """
        Some widgets (at the moment only files) need to have their data massaged in
        order to make sure that data->request and request->data is symmetric

        This pre parsing is a null operation for most widgets
        """
        data = {}

        for f in field.fields:
            try:
                r = request_data[int(f.nodename)]
            except (TypeError, KeyError):
                r = None
            d = f.widget.pre_parse_incoming_request_data(f, r)
            data[f.nodename] = d

        return data

    def from_request_data(self, field, request_data, skip_read_only_default=False):
        data = []
        if request_data is None:
            request_data = {}
        for f in field.fields:
            try:
                if f.widget.readonly is not True:
                    data.append( f.widget.from_request_data(f, request_data.get(f.nodename)) )
                else:
                    if skip_read_only_default is False:
                        data.append( f.defaults )
            except ConvertError, e:
                f.errors = e.message

        # Trim empty fields from the end of the list
        if self.strip_empty:
            n = None
            for n in xrange(len(data),0,-1):
                if not self.empty_checker(data[n-1]):
                    break
            else:
                # they are all empty
                n = 0
            if n is not None:
                return data[:n]
        return data


        

    def __repr__(self):
        attributes = []
        if self.converter_options != {'delimiter':','}:
            attributes.append('converter_options=%r'%self.converter_options)
        if self.css_class:
            attributes.append('css_class=%r'%self.css_class)
        if self.empty is not None:
            attributes.append('empty=%r'%self.empty)
        if self.batch_add_count:
            attributes.append('batch_add_count=%r'%self.batch_add_count)
        if self.min_start_fields:
            attributes.append('min_start_fields=%r'%self.min_start_fields)
        if self.min_empty_start_fields:
            attributes.append('min_empty_start_fields=%r'%self.min_empty_start_fields)
        if self.addremove:
            attributes.append('addremove=%r'%self.addremove)
        if self.sortable:
            attributes.append('sortable=%r'%self.sortable)

        return 'formish.%s(%s)'%(self.__class__.__name__, ', '.join(attributes))


class StructureDefault(Container):
    """
    Sequence handling widget - used by default for schema sequences

    :arg min: minimum number of sequence items to show
    :arg max: maximum number of sequence items to show
    :arg addremove: boolean whether to show the addremove buttons (jquery
        activated)
    """

    type = 'StructureDefault'
    template = 'structure.-'

    def to_request_data(self, field, data):
        """
        Short circuits the usual to_request_data
        """
        request_data = {}
        if data is None:
            data = {}
        for f in field.fields:
            try:
                request_data[f.nodename] = f.widget.to_request_data(f, data.get(f.nodename))
            except Invalid, e:
                f.errors[f.name] = e.message
                raise
        return request_data

    def pre_parse_incoming_request_data(self, field, request_data):
        """
        Some widgets (at the moment only files) need to have their data massaged in
        order to make sure that data->request and request->data is symmetric

        This pre parsing is a null operation for most widgets
        """
        data = {}

        for f in field.fields:
            if request_data is None:
                r = None
            else:
                r = request_data.get(f.nodename, None)
            d = f.widget.pre_parse_incoming_request_data(f, r)
            data[f.nodename] = d
        return data

    def from_request_data(self, field, request_data, skip_read_only_defaults=False):
        data = {}
        if request_data is None:
            request_data = {}
        for f in field.fields:
            try:
                if f.widget.readonly is not True:
                    data[f.nodename] = f.widget.from_request_data(f, request_data.get(f.nodename))
                else:
                    if skip_read_only_defaults is False:
                        data[f.nodename] = f.defaults
            except ConvertError, e:
                f.errors = e.message
        
        return data

    

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

class Grid(SequenceDefault):
    """
    Grid input field
    """
    type = 'Grid'
    template = 'field.Grid'
    
    
class Checkbox(Widget):
    """
    Checkbox widget, defaults to True or False
    """

    type = 'Checkbox'
    template = 'field.Checkbox'
    none_value=''
    empty = False

    def __init__(self, checked_value=True, unchecked_value=False, css_class=None, **k):
        self.checked_value = checked_value
        self.unchecked_value = unchecked_value
        self.empty = k.pop('empty',self.empty)
        Widget.__init__(self, css_class=css_class, none_value=self.none_value, empty=self.empty, **k)

    def to_request_data(self, field, data):
        """
        Before the widget is rendered, the data is converted to a string
        format.If the data is None then we return an empty string. The sequence
        is request data representation.
        """
        if data is None or (data == self.empty and self.roundtrip_empty is True):
            return self.none_value_as_request_data(field)
        string_data = string_converter(field.attr).from_type(data, converter_options=self.converter_options)
        return [string_data]


    def from_request_data(self, field, request_data):
        if request_data[0] == '':
            return self.empty
        if string_converter(field.attr).to_type(request_data[0]) == self.checked_value:
            return self.checked_value
        return self.unchecked_value

    def checked(self, field):
        """
        For each value, convert it and check to see if it matches the input data
        """
        if field.value and field.value[0] and string_converter(field.attr).to_type(field.value[0]) == self.checked_value:
            return ' checked="checked"'
        else:
            return ''

    
class DateParts(Widget):
    """
    Simple three part date entry form
    """

    type = 'DateParts'
    template = 'field.DateParts'
    default_value = {'year':[''], 'month':[''], 'day': ['']}
    
    def __init__(self, **k):
        self.strip = k.pop('strip', True)
        self.day_first = k.pop('day_first', None)
        Widget.__init__(self, **k)
        if not self.converter_options.has_key('delimiter'):
            self.converter_options['delimiter'] = ','

        
    def to_request_data(self, field, data):
        """
        Convert to date parts
        """
        dateparts = datetuple_converter(field.attr).from_type(data)
        if dateparts is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        return {'year': [dateparts[0]],
                'month': [dateparts[1]],
                'day': [dateparts[2]]}
    
    def from_request_data(self, field, request_data):
        """
        Pull out the parts and convert
        """
        if request_data == self.default_value:
            return self.empty
        year = request_data['year'][0].strip()
        month = request_data['month'][0].strip()
        day = request_data['day'][0].strip()
        if year or month or day:
            date_parts = (year, month, day)
        else:
            return self.empty
        return datetuple_converter(field.attr).to_type(date_parts)

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
    
    def __init__(self, filestore=UNSET, show_file_preview=True,
                 show_download_link=False, show_image_thumbnail=False,
                 url_base=None, css_class=None, image_thumbnail_default=None,
                 show_remove_checkbox=True, url_ident_factory=None):
        """
        :arg filestore: filestore for temporary files
        :arg show_image_thumbnail: a boolean that, if set, will include an image
            thumbnail with the widget
        :arg css_class: extra css classes to apply to the widget
        :arg image_thumbnail_default: a default url to 
        XXX image_thumbnail_default -> default_image 
        XXX allow_clear -> allow_delete 
        XXX url_ident_factory -> filestore_key_factory
        """
        # Setup defaults.
        if filestore is UNSET:
            filestore = CachedTempFilestore()
        if url_base is None:
            url_base = '/filehandler'
        if url_ident_factory is None:
            url_ident_factory = lambda i: i.filename
        # Initialise instance state
        Widget.__init__(self)
        self.filestore = filestore
        self.show_image_thumbnail = show_image_thumbnail
        self.image_thumbnail_default = image_thumbnail_default
        self.url_base = url_base
        self.show_download_link = show_download_link
        self.show_file_preview = show_file_preview
        self.url_ident_factory = url_ident_factory
        self.show_remove_checkbox = show_remove_checkbox

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
        return '%s/%s' % (self.url_base, data)
    
    def to_request_data(self, field, data):
        """
        We use the url factory to get an identifier for the file which we use
        as the name. We also store it in the 'default' field so we can check if
        something has been uploaded (the identifier doesn't match the name)
        """
        mimetype = ''
        if isinstance(data, SchemaFile):
            default = util.encode_file_resource_path(None, self.url_ident_factory(data))
            mimetype = data.mimetype
        elif data is not None:
            default = util.encode_file_resource_path(None, data)
        else:
            default = ''
        return {'name': [default], 'default':[default], 'mimetype':[mimetype]}
    
    def pre_parse_incoming_request_data(self, field, data):
        """
        File uploads are wierd; in out case this means assymetric. We store the
        file in a temporary location and just store an identifier in the field.
        This at least makes the file look symmetric.
        """
        if data is None:
            data = {}
        if data.get('remove', [None])[0] is not None:
            data['name'] = ['']
            data['mimetype'] = ['']
            return data

        fieldstorage = data.get('file', [''])[0]
        if getattr(fieldstorage,'file',None):
            # XXX Can we reuse the key from a previous temp upload to avoid
            # creating an additional temp file?
            key = uuid.uuid4().hex
            cache_tag = uuid.uuid4().hex
            self.filestore.put(key, fieldstorage.file, cache_tag,
                               [('Content-Type', fieldstorage.type),
                                ('Filename', fieldstorage.filename)])
            data['name'] = [util.encode_file_resource_path('tmp', key)]
            data['mimetype'] = [fieldstorage.type]
        return data
    
    def from_request_data(self, field, request_data):
        """
        Creates a File object if possible
        """
        # XXX We could add a file converter that converts this to a string data?

        if request_data['name'] == ['']:
            return None
        elif request_data['name'] == request_data['default']:
            return SchemaFile(None, None, None)
        else:
            key = util.decode_file_resource_path(request_data['name'][0])[1]
            try:
                cache_tag, headers, f = self.filestore.get(key)
            except KeyError:
                return None
            headers = dict(headers)
            return SchemaFile(f, headers['Filename'], headers['Content-Type'])

    
class SelectChoice(Widget):
    """
    Html Select element
    """

    type = 'SelectChoice'
    template = 'field.SelectChoice'

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
        if self.none_option and self.none_option[0] and 'none_value' not in k:
            k['none_value'] = self.none_option[0]
        else:
            k['none_value'] = ''
        Widget.__init__(self, **k)
        self.options = _normalise_options(options)

            
    def selected(self, option, field):
        """
        Check the value passed matches the actual value
        """
        if option[0] == field.value[0] and option[0] != self.empty:
            return ' selected="selected"'
        else:
            return ''

    def get_options(self, field):
        """
        Return all of the options for the widget
        """
        options = []
        for value, label in self.options:
            options.append( (string_converter(field.attr).from_type(value),label) )
        return options
    
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
    default_value = {'select': [''], 'other': ['']}

    other_option = ('...', 'Other ...')

    def __init__(self, options, **k):
        other_option = k.pop('other_option', UNSET)
        if other_option is not UNSET:
            self.other_option = other_option
        self.strip = k.pop('strip',True)
        SelectChoice.__init__(self, options, **k)

    def to_request_data(self, field, data):
        """
        populate the other choice if needed
        """
        string_data = string_converter(field.attr).from_type(data)
        if string_data is None:
            return self.none_value_as_request_data(field)
        if string_data in [value for value, label in self.options]:
            return {'select': [string_data], 'other': ['']}
        return {'select': [self.other_option[0]], 'other': [string_data]}

    def none_value_as_request_data(self, field):
        return {'select': [self.none_value], 'other': ['']}

    def from_request_data(self, field, request_data):
        """
        Check to see if we need to use the 'other' value
        """
        select = request_data['select'][0]
        other = request_data['other'][0]
        if select == self.other_option[0]:
            value = other
        else:
            if other != '':
                raise ConvertError('You entered text in the box but had not selected "%s" in the drop down. We have now selected it for you. please check and resubmit'%self.other_option[1])
            value = select
        if value == '':
            return self.empty
        return string_converter(field.attr).to_type(value)

    def selected(self, option, field):
        """ Check the value passed matches the actual value """
        value = field.value['select']
        if option[0] == self.other_option[0] and value[0] not in [value for value, label in self.get_options(field)]:
            return ' selected="selected"'
        # Check for selected
        if option[0] == value[0]:
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

    none_option = None

    def selected(self, option, field):
        """
        Check if the currently rendering input is the same as the value
        """
        if option[0] == field.value[0]:
            return ' checked="checked"'
        else:
            return ''

    def from_request_data(self, field, request_data):
        """
        If we don't have a choice, set a blank value
        """
        string_data = request_data[0]

        if string_data == '':
            return self.empty

        return string_converter(field.attr).to_type(string_data)
    
    def get_none_option_value(self, field):
        """
        Get the default option (the 'unselected' option)
        """
        none_option =  string_converter(field.attr).from_type(self.none_option[0])
        if none_option is self.empty:
            return ''
        return none_option

    def __repr__(self):
        attributes = []
        attributes.append('options=%r'%self.options)
        if self.none_option and self.none_option is not UNSET:
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
    default_value = []

    def __init__(self, options, css_class=None):
        self.options = _normalise_options(options)
        Widget.__init__(self, css_class=css_class)
            
    def to_request_data(self, field, data):
        """
        Iterate over the data, converting each one
        """
        return [string_converter(field.attr.attr).from_type(d) for d in data]


    def pre_parse_incoming_request_data(self, field, request_data):
        return  request_data or []

    
    def from_request_data(self, field, request_data):
        """
        Iterating to convert back to the source data
        """
        return [string_converter(field.attr.attr).to_type(d) \
                for d in request_data]

    def checked(self, option, field):
        """
        For each value, convert it and check to see if it matches the input data
        """
        if field.value is None:
            return ''
        cvs = []
        for v in field.value:
            try:
                cvs.append( string_converter(field.attr.attr).to_type(v) )
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
    default_value = []

    def __init__(self, options, css_class=None):
        self.options = options
        self.optiontree = mktree(options)
        Widget.__init__(self,css_class=css_class)

    def to_request_data(self, field, data):
        if data is None:
            return []
        return [string_converter(field.attr.attr).from_type(d) for d in data]
    
    def from_request_data(self, field, request_data):
        if request_data is None:
            request_data = []
        return [string_converter(field.attr.attr).to_type(d) for d in request_data]

    def checked(self, option, field):
        if field.value is not None:
            typed_values = self.from_request_data(field.attr,field.value)
        if field.value is not None and option[0] in typed_values:
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

