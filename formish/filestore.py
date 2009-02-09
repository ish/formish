"""
Standard filehandlers for temporary storage of file uploads. Uses tempfile to
make temporary files
"""
import tempfile
import os.path
import uuid, magic
from datetime import datetime


class WritableFileStoreInterface(object):
    """ Example of file store for formish file upload support. """

    def store_file(self, fieldstorage):
        """ Method to store a file """

    def delete_file(self, filename):
        """ Method to delete a file """

    def get_file(self, filename):
        """ Method to get a file """

    def get_path_for_file(self, filename):
        """ Method to get a path for a file on disk """

    def cacheattr(self, filename):
        """ Method to get some cache freshness attribute """


class TempFileWritableFileStore(object):
    """
    Writable file store using python tempfile module to store file
    """

    def __init__(self):
        self.prefix = tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()
        self.mtime_cache = True

    def _abs(self, filename):
        return '%s/%s%s'% (self.tempdir, self.prefix, filename)

    def store_file(self, fieldstorage):
        fileno, filename = tempfile.mkstemp(suffix='%s-%s' % \
                                 (uuid.uuid4().hex,fieldstorage.filename))
        filehandle = os.fdopen(fileno, 'wb')
        filehandle.write(fieldstorage.value)
        filehandle.close()
        filename = ''.join( filename[(len(self.tempdir)+len(self.prefix)+1):] )
        return filename

    def delete_file(self, filename):
        os.remove(self._abs(filename))

    def get_file(self, filename):
        return open(self._abs(filename),'rb').read()

    def cacheattr(self, filename):
        try:
            mtime = datetime.fromtimestamp( os.path.getmtime(self._abs(filename)) )
        except OSError:
            raise KeyError()
        return mtime

    def get_path_for_file(self, filename):
        return self._abs(filename)



        





