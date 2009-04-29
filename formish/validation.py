"""
The validation module converts data to and from request format (or at least
calls the converters that do so) and also converts dotted numeric formats into
sequences (e.g. a.0 and a.1 onto a[0] and a[1]). It also includes some
validation exceptions.
"""
from dottedish import dotted
from validatish import Invalid
from convertish import convert

def convert_sequences(data):
    """
    Converts numeric keyed dictionaries into sequences

    Converts ``{'0': 'foo', '1': 'bar'}`` into ``['foo','bar']``. leaves anything else alone
    """
    # must be a dict
    if not hasattr(data,'keys'):
        return data
    # if the first key cannot be converted to an int then we don't have a
    # sequence
    try:
        int(data.keys()[0])
    except ValueError:
        return dotted(data)
    # collect the keys as sorted integers
    intkeys = []
    for key in data.keys():
        intkeys.append(int(key))
    intkeys.sort()
    # construct the sequence
    out = []
    for key in intkeys:
        out.append(data[str(key)])
    return out

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

def getNestedProperty(data, dottedkey):
    """
    Gets's data out of structures using dotted strings

    Given a structure that may be a sequence or a dictionary or a combination
    (e.g. {'a': [1,2]}) and a dotted string, traverses the structure one
    segment of the dotted key at a time.

    e.g.

    .. code-block:: python
    
      getNestedProperty({'a': [1,{'b':'foo'}]} , 'a.1.b') == 'foo'

    :arg d: a dictionary or sequence or combination
    :arg dottedkey: a dotted string (e.g. ``a.1``)
    """
    if dottedkey == '':
        return data
    keys = dottedkey.split('.')
    firstkey = keys[0]
    remaining_dottedkey = '.'.join(keys[1:])
    try:
        firstkey = int(firstkey)
    except:
        pass
    try:
        return getNestedProperty(data[firstkey], remaining_dottedkey)
    except (KeyError, IndexError):
        return None


def to_request_data(form_structure, data, request_data=None, errors=None):
    """
    Take a form structure and use it's widgets to convert schema data (dict) to
    request data
    
    :arg form_structure: a formish form
    :arg data: a dictionary structure to be converted using the form
    :arg request_data: used to accumulate request
        data (internal - used while recursing)
    :arg errors: used to accumulate conversion 
        failures (internal - used while recursing)
    
    """
    if request_data is None:
        request_data = dotted()
    if errors is None:
        errors = dotted()
    for field in form_structure.fields:
        try:
            if field.type is 'group' or \
              (field.type is 'sequence' and \
                (field.widget is None or \
                  field.widget.converttostring is False)):
                to_request_data(field, data,
                        request_data=request_data, errors=errors)
            else:
                item_data = getNestedProperty(data, field.name)
                request_data[field.name] = \
                        field.widget.to_request_data(field.attr, item_data)
        except Invalid, e:
            errors[field.name] = e
            raise
    return request_data
        
def from_request_data(form_structure, request_data, data=None, errors=None):
    """
    Take a form structure and use it's widgets to convert request data to schema data (dict)
    
    :arg form_structure: a formish form
    :arg data: a webob.POST like dictionary
    :arg data: used to accumulate schema data (internal - used while recursing)
    :arg errors: used to accumulate conversion failures (internal - used while recursing)
    
    """
    if data is None:
        data = {}
    if errors is None:
        errors = {}

    for field in form_structure.fields:
        try:
            if field.type is 'group' or \
              (field.type == 'sequence' and \
                (field.widget._template is 'SequenceDefault' \
                 or field.widget.converttostring is False)):
                if field.type == 'sequence':
                    # Make sure we have an empty field at least. If we don't do
                    # this and there are no items in the list then this key
                    # wouldn't appear.
                    data[field.name] = []
                from_request_data(field, request_data,
                                          data=data, errors=errors)
            else: 
                data[field.name] = field.widget.from_request_data(field.attr, \
                                                request_data.get(field.name,[]))
        except convert.ConvertError, e:
            errors[field.name] = e.message
    
    data = recursive_convert_sequences(dotted(data))
    return data

def pre_parse_incoming_request_data(form_structure, request_data, data=None):
    """
    Some widgets (at the moment only files) need to have their data massaged in
    order to make sure that data->request and request->data is symmetric

    This pre parsing is a null operation for most widgets
    """
    if data is None:
        data = {}
    for field in form_structure.fields:
        if field.type is 'group' or \
          (field.type == 'sequence' and \
             field.widget._template is 'SequenceDefault'):
            pre_parse_incoming_request_data(field, request_data, data=data)
        else: 
            # This needs to be cleverer...
            item_data = request_data.get(field.name, [])
            data[field.name] = field.widget.pre_parse_incoming_request_data(field.attr, item_data, full_request_data=request_data)

    return dotted(data)


class FormishError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """
    def __init__(self, message, *args):
        Exception.__init__(self, message, *args)
        self.message = message
    def __str__(self):
        return self.message
    __unicode__ = __str__


class FormError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass

    
class NoActionError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass

