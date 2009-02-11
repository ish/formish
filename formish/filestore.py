"""
Standard filehandlers for temporary storage of file uploads. Uses tempfile to
make temporary files
"""
import tempfile
import os.path
import shutil
from formish import safefilename


class FileSystemHeaderedFilestore(object):
    """
    A general purpose readable and writable file store useful for storing data
    along with additional metadata (simple key-value pairs).

    This can be used to implement temporary file stores, local caches, etc.
    XXX file ownership?
    XXX delete
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
            headers.append((name, value))
        return headers, f

    def put(self, key, headers, src):
        dest = file(os.path.join(self._root_dir, safefilename.encode(key)), 'wb')
        try:
            if isinstance(headers, dict):
               headers = headers.items()
            for name, value in headers:
                dest.write('%s: %s\n' % (name, value))
            dest.write('\n')
            shutil.copyfileobj(src, dest)
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
        if not cache_tag and headers['Cache-Tag'] == cache_tag:
            f.close()
            return (headers['Cache-Tag'], None, None)
        return (headers['Cache-Tag'],headers['Content-Type'], f)


    def put(self, key, src, cache_tag, content_type, headers=None):
        if headers is None:
            headers = {}
        headers['Cache-Tag'] = cache_tag
        headers['Content-Type'] = content_type
        FileSystemHeaderedFilestore.put(self, key, headers, src)

