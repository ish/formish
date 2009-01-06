"""
A dotted dict is a typical dotted nested dictionary implementation with a
twist. It also handles embedded sequences by using integers for keys.. hence
a.0 and a.1 are d['a'][0] and d['a'][1]
"""
from webob import MultiDict, UnicodeMultiDict


def is_int(v):
    """ raise error if not """
    try:
        int(v)
        return True
    except ValueError:
        return False
    
    
def try_int(v):
    """ try to convert if possible, otherwise just return the value """
    try:
        return int(v)
    except ValueError:
        return v
    
def _setDict(data, keys, value, overwrite=False):
    """
    Given a dottedDict, sets a new value based on a list of keys
    """
    if len(keys) == 1:
        key = try_int(keys[0])
        if is_int(key):
            if isinstance(data, dict) and len(data.keys()) == 0 and key == 0:
                data = [value]
            elif isinstance(data, list) and key == len(data):
                data.append(value)
            elif isinstance(data, list) and key > len(data):
                for i in xrange(len(data), key):
                    if isinstance(value, dict):
                        data.append({})
                    elif isinstance(value, list):
                        data.append([])
                    else:
                        data.append(None)
                data.append(value)
            elif isinstance(data, list) and key < len(data):
                data[key] = value
            else:
                raise KeyError('Can\'t set using an integer key here')
        else:
            if isinstance(data, dict):
                data[keys[0]] = value
            else:
                if overwrite is True:
                    data = {keys[0]: value}
                else:
                    raise KeyError( \
                'Already assigned data key %s value %s'%(keys[0], data))
    else:
        if is_int(keys[0]):
            if isinstance(data, list) or \
              (isinstance(data, dict) and len(data.keys()) == 0):
                if (isinstance(data, dict) and len(data.keys()) == 0):
                    # if we're trying to set using an integer key and we
                    # currently have an empty dict then make it a list. 
                    data = []
                if try_int(keys[0]) == 0:
                    # if we have a 0 as the first key, we need to make the data
                    # a list...
                    if len(data) == 0:
                        data = [{}]
                    d = _setDict(data[try_int(keys[0])], \
                                 keys[1:], value, overwrite=overwrite) 
                if len(data)>try_int(keys[0]):
                    d = _setDict(data[try_int(keys[0])], \
                                 keys[1:], value, overwrite=overwrite) 
                elif len(data) == try_int(keys[0]):
                    o = _setDict({}, keys[1:], value, overwrite=overwrite)
                    data.append( o )
                    d = o
                else:
                    raise KeyError
            else:
                raise KeyError
        else:
            if isinstance(data, dict) and \
             data.has_key(keys[0]) and not \
              isinstance(data[keys[0]],dict) and overwrite is True:
                data[keys[0]] = {}
            d = _setDict(_setdefault(data, keys[0], {}), \
                         keys[1:], value, overwrite=overwrite)
        data[try_int(keys[0])] = d
    return data

def copy_multi_dict(original):
    """
    copy all of the keys in the multidict
    """
    copy = {}
    for key in original.keys():
        copy[key] = original.getall(key)
    return copy

def keysort(a, b):
    """
    cmp function for sorting dotted key values
    """
    if len(a) != len(b):
        return cmp(len(a), len(b))
    for i in xrange(len(a)-1, -1, -1):
        if a[i] == b[i]:
            continue
        if is_int(a[i]):
            return cmp(int(a[i]), try_int(b[i]))
        else:
            return cmp(a[i], b[i])
    return 0
                    

def _getDictFromDottedKeyDict(d, noexcept=False):
    """
    Given a dictionary - creates a dotteddict
    """
    if isinstance(d, MultiDict) or isinstance(d, UnicodeMultiDict):
        data = copy_multi_dict(d)
    else:
        data = d
    if isinstance(d, list):
        return d
    keyslist = [key.split('.') for key in data.keys()]
    keyslist.sort(keysort)
    for keys in keyslist:
        if len(keys) > 1:
            dottedkey = '.'.join(keys)
            if not data.has_key(dottedkey):
                continue
            if hasattr(data,'getall'):
                value = data.getall(dottedkey)
            else:
                value = data[dottedkey]
            del data[dottedkey]
            try:
                data = _setDict(data, keys, value, overwrite=noexcept)
            except KeyError:
                if noexcept is True:
                    pass
                else:
                    raise
        else:
            if hasattr(data,'getall'):
                data[keys[0]] = data.getall(keys[0])
    return data

# Singleton used to represent no argument passed, for when None is a valid
# value for the arg.
NOARG = object()
NOVALUE = object()


def _setdefault(data, dottedkey, default=NOARG):
    """
    sets a value on a dict  based on a dottedKey - generates keys if not there
    already
    """
    # First of all check if we aleady have a value for this key and return it
    # if so...
    try:
        return _get(data, dottedkey)
    except:
        pass
    # We don't have the value so lets build a list of keys that we need to work
    # on
    keys = str(dottedkey).split('.')
    lastleaf = data
    K = None
    # Loop on the list of keys up to the next to last one (we already checked
    # the last one at the start of the run)
    for n, key in enumerate(keys[:-1]):
        K = '.'.join(keys[0:n+1])
        # Check to see if the data has this key, if it doesn't then break; if
        # it does then loop again
        if not _has_key(data, K):
            break
        lastkey = '.'.join(keys[0:n+1])
        restofkeys = keys[n+1:]
        lastleaf = _get(data, lastkey) 

    # We've drilled in as far as we can go.. 
    
    if K is None:
        # if we didn't find a K then we have a new var to set
        data = _setDict(data, keys, default)
    else:
        # We should have a K for which the last segment doesn't exist
        if isinstance(lastleaf, dict) and \
           len(lastleaf.keys()) == 0 and is_int(keys[n]):
            _set(data, lastkey, [])
            lastleaf = _get(data, lastkey)
        if isinstance(lastleaf, list) and try_int(keys[n]) == len(lastleaf):
            lastleaf.append(_setDict({}, keys[n+1:], default))
        else:
            if lastleaf == data:
                data = _setDict(data, keys, default)
            else:
                _setDict(lastleaf, restofkeys, default)

            
    return _get(data, dottedkey)
   
## 
# given a real dictionary, recursively sets a value based on a dottedkey
def _set(data, dottedkey, value):
    """ Set a dotted key on a dotted dict """
    keys = str(dottedkey).split('.')
    d = data
    try:
        for n, key in enumerate(keys[:-1]):
            d = d[try_int(key)]
    except KeyError, e:
        raise KeyError(
            'Error accessing dotted key %s on %r. Only got to %s'% \
            (dottedkey,data,'.'.join(keys[:n])))
    d[try_int(keys[-1])] = value
    return data

def _get(d, dottedkey):
    """ get a dottedkey value from a dottedict """
    keys = str(dottedkey).split('.')
    K_parts = []
    for n, key in enumerate(keys):
        K_parts.append(key)
        K = '.'.join(K_parts)
        try:
            d = d[try_int(K)]
            K_parts = []
        except (KeyError, TypeError), e:
            pass
    if K_parts != []:
        raise KeyError( \
            'Error accessing dotted key %s - key %s does not exist'% \
                       (dottedkey, key))
    return d
    
def _has_key(d, dottedkey):
    """ Does the dict have this dottedkey """
    try:
        out = _get(d, dottedkey)
        return True
    except:
        return False

class dottedDict(object):
    """ A dictionary that can be accessed and written to in dotted notation """
    
    def __init__(self, value=None):
        if value is None:
            self.data = {}
        else:
            if isinstance(value, dottedDict):
                self.data = value.data
            else:
                self.data = _getDictFromDottedKeyDict(value)
            
    def get(self, dottedkey, default=None):
        """ Get the dottedkey """
        try:
            d = _get(self.data, dottedkey)
        except KeyError, e:
            return default
        if isinstance(d, dict):
            return dottedDict(d)
        else:
            return d
        
    def __getitem__(self, dottedkey):
        """ implement the dict getitem """
        d = _get(self.data, dottedkey)
        if isinstance(d, dict):
            return dottedDict(d)
        else:
            return d
        
    def __setitem__(self, dottedkey, value):
        """ implement the dict setitem """
        _setdefault(self.data, dottedkey, value)
        _set(self.data, dottedkey, value)
        
    def keys(self):
        """ return the top level keys """
        keys = []
        if isinstance(self.data, list):
            for n, v in enumerate(self.data):
                keys.append(n)
        else:
            keys = self.data.keys()
        return keys
    
    def items(self):
        """ return the top level items """
        items = []
        for key in self.keys():
            items.append( (key, self[key]) )
        return items
        
    
    def dotteditems(self):
        """ return all ofthe items """
        store = []
        for key in self.dottedkeys():
            store.append((key, self[key]))
        return store
    
    def dottedkeys(self, value=NOARG, store=NOARG, prefix=None):
        """ return all of the keys """
        if store is NOARG:
            store = []
        if value is NOARG:
            value = self.data
        if not isinstance(value, list) and not isinstance(value, dict):
            store.append(prefix)
            return store
        if isinstance(value, dict):
            for k, v in value.items():
                if prefix:
                    dkey = '%s.%s'% (prefix, k)
                else:
                    dkey = k
                self.dottedkeys(value=v, store=store, prefix=dkey)
        elif isinstance(value, list):
            for n, v in enumerate(value):
                if prefix:
                    dkey = '%s.%s'% (prefix, n)
                else:
                    dkey = n
                self.dottedkeys(value=v, store=store, prefix=dkey)
        return store
                
            
    
    def __eq__(self, other):
        """ compare with another dictionary """
        return self.data == dottedDict(other).data
    

    def setdefault(self, dottedkey, default=NOARG):
        """ overrise setdefault dict method """
        # Check return value for list or dict - if dict, wrap in ddict
        return _setdefault(self.data, dottedkey, default=default)
            
    def __getattr__(self, key):
        """ Allow get attr style access """
        try:
            value = self.get(key.split('.')[0], NOVALUE)
            if value is NOVALUE:
                raise KeyError('Dotted key \'%s\' does not exist'%key)
        except AttributeError, e:
            raise KeyError(e.message)
        
    def has_key(self, key):
        """ does the key exist """
        return key in self.keys()
    
    def __contains__(self, key):
        """ is this key in the dict """
        return key in self.keys()

    def has_dottedkey(self, dottedkey):
        """ does this dotted key exist """
        try:
            temp = self[dottedkey]
        except KeyError:
            return False
        return True
    
    def __repr__(self):
        """ display a usefull repr """
        return '<dottedDict> %s'% self.data
