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


class CachedTempFilestore(FileSystemHeaderedFilestore):

    def __init__(self, root_dir=None, name=None):
        if root_dir is None:
            self._root_dir = tempfile.gettempdir()
        else:
            self._root_dir = root_dir
        if name is None:
            self.name = ''
        else:
            self.name = name

    def get(self, key, cache_tag=None):
        headers, f = FileSystemHeaderedFilestore.get(self, key)
        headers = dict(headers)
        if cache_tag and headers.get('Cache-Tag') == cache_tag:
            f.close()
            return (cache_tag, None, None)
        return (headers.get('Cache-Tag'), headers.get('Content-Type'), f)

    def put(self, key, src, cache_tag, content_type, headers=None):
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        if cache_tag:
            headers['Cache-Tag'] = cache_tag
        if content_type:
            headers['Content-Type'] = content_type
        FileSystemHeaderedFilestore.put(self, key, headers, src)

