"""
Standard filehandlers for temporary storage of file uploads. Uses tempfile to
make temporary files
"""
import tempfile
import os.path
from formish import _copyfile, safefilename


class FileSystemHeaderedFilestore(object):
    """
    A general purpose readable and writable file store useful for storing data
    along with additional metadata (simple key-value pairs).

    This can be used to implement temporary file stores, local caches, etc.
    XXX file ownership?
    """

    def __init__(self, root_dir):
        self._root_dir = root_dir

    def get(self, key):
        try:
            f = open(os.path.join(self._root_dir, safefilename.encode(key)), 'rb')
        except IOError, AttributeError:
            raise KeyError(key)
        headers = []
        while True:
            line = f.readline().strip()
            if not line:
                break
            name, value = line.split(': ', 1)
            headers.append((name, value.decode('utf-8')))
        return headers, f

    def put(self, key, headers, src):
        # XXX We should only allow strings as headers keys and values.
        dest = file(os.path.join(self._root_dir, safefilename.encode(key)), 'wb')
        try:
            if isinstance(headers, dict):
               headers = headers.items()
            for name, value in headers:
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                dest.write('%s: %s\n' % (name, value))
            dest.write('\n')
            _copyfile.copyfileobj(src, dest)
        finally:
            dest.close()

    def delete(self, key, glob=False):
        # if glob is true will delete all with filename prefix
        if glob == True:
            for f in os.listdir(self._root_dir):
                if f.startswith(safefilename.encode(key)):
                    os.remove(os.path.join(self._root_dir,f))
        else:
            os.remove( os.path.join(self._root_dir, safefilename.encode(key)))


class CachedTempFilestore(object):

    def __init__(self, backend=None):
        if backend is None:
            backend = FileSystemHeaderedFilestore(tempfile.gettempdir())
        self.backend = backend

    def get(self, key, cache_tag=None):
        headers, f = self.backend.get(key)
        if headers and headers[0][0] == 'Cache-Tag':
            header_cache_tag = headers[0][1]
            headers = headers[1:]
        else:
            header_cache_tag = None
        if cache_tag and header_cache_tag == cache_tag:
            f.close()
            return (cache_tag, headers, None)
        return (header_cache_tag, headers, f)

    def put(self, key, src, cache_tag, headers=None):
        if headers is None:
            headers = []
        if cache_tag:
            headers = [('Cache-Tag', cache_tag)] + headers
        self.backend.put(key, headers, src)

    def delete(self, key):
        self.backend.delete(key)

