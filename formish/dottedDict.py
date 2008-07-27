def _setDict(data, keys, value):
    if len(keys) == 1:
        if isinstance(data, dict):
            data[keys[0]] = value
        else:
            raise KeyError('Already assigned data key %s value %s'%(keys[0], data))
    else:
        _setDict(data.setdefault(keys[0],{}), keys[1:], value)


def _getDictFromDottedDict(data):
    keyslist=[key.split('.') for key in data.keys()]
    keyslist.sort(reverse=True)
    for keys in keyslist:
        if len(keys) > 1:
            dottedkey = '.'.join(keys)
            if not data.has_key(dottedkey):
                continue
            if hasattr(data,'getall'):
                value=data.getall(dottedkey)
            else:
                value = data[dottedkey]
            del data[dottedkey]
            _setDict(data, keys, value)
    return data

# Singleton used to represent no argument passed, for when None is a valid
# value for the arg.
NOARG = object()
NOVALUE = object()

class dottedDict(object):
    """A dictionary that can be accessed and written to in dotted notation"""
    
    def __init__(self, value=None):
        if value is None:
            self.data = {}
        else:
            if isinstance(value, dottedDict):
                self.data = value.data
            else:
                self.data = _getDictFromDottedDict(value)
            
    def get(self, dottedkey, default=NOARG):
        keys = dottedkey.split('.')
        d = self.data
        try:
            for key in keys:
                d = d[key]
        except KeyError, e:
            if default is not NOARG:
                return default
            raise KeyError('Dotted key does not exist')
        if isinstance(d, dict):
            return dottedDict(d)
        else:
            return d
        
    def __getitem__(self, item):
        return self.get(item)
        
    def __setitem__(self,dottedkey, value):
        keys = dottedkey.split('.')
        d = self.data
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value
        
    def keys(self):
        return self.data.keys()
    
    def __eq__(self, other):
        return self.data == dottedDict(other).data
    

    def setdefault(self, dottedkey, default=NOARG):
        keys = dottedkey.split('.')
        d = self.data
        try:
            for key in keys:
                d = d[key]
        except KeyError, e:
            if default is not NOARG:
                d[dottedkey] = default
                return d[dottedkey]
            raise KeyError('Dotted key does not exist')
        if isinstance(d, dict):
            return dottedDict(d)
        else:
            return d
        
    def __getattr__(self, key):
        try:
            value = self.get(key.split('.')[0], NOVALUE)
            if value is NOVALUE:
                raise KeyError('Dotted key does not exist')
        except AttributeError, e:
            raise KeyError(e.message)
        
    def has_key(self, key):
        return key in self.keys()
    
    def __repr__(self):
        return '<dottedDict> %s'%self.data
        