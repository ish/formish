import copy
from webob import MultiDict


def isInt(v):
    try:
        int(v)
        return True
    except ValueError:
        return False
    
    
def tryInt(v):
    try:
        return int(v)
    except ValueError:
        return v
    
def _setDict(data, keys, value):
    if len(keys) == 1:
        if isinstance(data, dict):
            data[keys[0]] = value
        else:
            raise KeyError('Already assigned data key %s value %s'%(keys[0], data))
    else:
        _setDict(data.setdefault(keys[0],{}), keys[1:], value)

def copyMultiDict(original):
    copy = {}
    for key in original.keys():
        copy[key] = original.getall(key)
    return copy

def _getDictFromDottedKeyDict(d):
    if isinstance(d, MultiDict):
        data = copyMultiDict(d)
    else:
        data = d
    if isinstance(d,list):
        return d
    keyslist=[key.split('.') for key in data.keys()]
    keyslist.sort(reverse=True)
    for keys in keyslist:
        if len(keys) > 1:
            dottedkey = '.'.join(keys)
            if not data.has_key(dottedkey):
                continue
            if hasattr(data,'getall'):
                value= data.getall(dottedkey)
            else:
                value = data[dottedkey]
            del data[dottedkey]
            _setDict(data, keys, value)
        else:
            if hasattr(data,'getall'):
                data[keys[0]] = data.getall(keys[0])
    return data

# Singleton used to represent no argument passed, for when None is a valid
# value for the arg.
NOARG = object()
NOVALUE = object()

def setdefault(self, dottedkey, default=NOARG):
    try:
        return self[dottedkey]
    except KeyError:
        pass
    keys = dottedkey.split('.')
    d = self.data

    for n,key in enumerate(keys[:-1]):
        if isinstance(d, list):
            l = len(d)
            if not isInt(key) or (isInt(key) and int(key) > l):
                raise ValueError
            d = d[int(key)]
        else:
            d = d.setdefault(key,{})
    if default is not NOARG:
        d[tryInt(keys[-1])] = default
    else:
        d[tryInt(keys[-1])] = None
    return self[dottedkey]
                

class dottedDict(object):
    """A dictionary that can be accessed and written to in dotted notation"""
    
    def __init__(self, value=None):
        if value is None:
            self.data = {}
        else:
            if isinstance(value, dottedDict):
                self.data = value.data
            else:
                self.data = _getDictFromDottedKeyDict(value)
            
    def get(self, dottedkey, default=NOARG):
        keys = str(dottedkey).split('.')
        d = self.data
        try:
            for n,key in enumerate(keys):
                try:
                    d = d[key]
                except TypeError:
                    d = d[tryInt(key)]
        except KeyError, e:
            if default is not NOARG:
                return default
            raise KeyError('Error accessing dotted key %s on %r. Only got to %s'%(dottedkey,self.data,'.'.join(keys[:n])))
        if isinstance(d, dict):
            return dottedDict(d)
        else:
            return d
        
    def __getitem__(self, item):
        return self.get(item)
        
    def __setitem__(self,dottedkey, value):
        keys = dottedkey.split('.')
        d = self
        for key in keys[:-1]:
            key = tryInt(key)
            d = setdefault(d, key, {})
        d.data[keys[-1]] = value
        
    def keys(self):
        keys = []
        if isinstance(self.data, list):
            for n, v in enumerate(self.data):
                keys.append(n)
        else:
            keys = self.data.keys()
        return keys
    
    def items(self):
        items = []
        for key in self.keys():
            items.append( (key, self[key]) )
        return items
        
    
    def dotteditems(self):
        store = []
        for key in self.dottedkeys():
            store.append((key, self[key]))
        return store
    
    def dottedkeys(self, value=None, store=None, prefix=None):
        if store is None:
            store = []
        if value is None:
            value = self.data
        if not isinstance(value, list) and not isinstance(value,dict):
            store.append(prefix)
            return store
        if isinstance(value, dict):
            for k, v in value.items():
                if prefix:
                    dkey = '%s.%s'%(prefix,k)
                else:
                    dkey = k
                self.dottedkeys(value=v, store=store, prefix=dkey)
        elif isinstance(value, list):
            for n, v in enumerate(value):
                if prefix:
                    dkey = '%s.%s'%(prefix,n)
                else:
                    dkey = n
                self.dottedkeys(value=v, store=store, prefix=dkey)
        return store
                
            
    
    def __eq__(self, other):
        return self.data == dottedDict(other).data
    

    def setdefault(self, dottedkey, default=NOARG):
        return setdefault(self, dottedkey, default=default)
            
    def __getattr__(self, key):
        try:
            value = self.get(key.split('.')[0], NOVALUE)
            if value is NOVALUE:
                raise KeyError('Dotted key \'%s\' does not exist'%key)
        except AttributeError, e:
            raise KeyError(e.message)
        
    def has_key(self, key):
        return key in self.keys()

    def has_dottedkey(self, dottedkey):
        try:
            temp = self[dottedkey]
        except KeyError:
            return False
        return True
    
    def __repr__(self):
        return '<dottedDict> %s'%self.data
    

if __name__ == '__main__':
    d = {'a': [1,2,3], 'b': [ {'a':2, 'b':3 }, {'a':4, 'b':5 }, {'a':6, 'b':7 } ]}
    D = dottedDict(d)
    print  D
    print "D['a.0'] -> ", D['a.0']
    print "D['b.1.a'] -> ",  D['b.1.a']
    print "setting D['b.1.a'] = 7"
    D['b.1.a'] = 7
    print "D['b.1.a'] -> ",  D['b.1.a']
    print "D.keys()", D.keys()
    print "D.dottedkeys()", D.dottedkeys()
    print "D.items()",D.items()
    print "D.dotteditems()", D.dotteditems()
    
    