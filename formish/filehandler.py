"""
Standard filehandlers for temporary storage of file uploads. Uses tempfile to
make temporary files
"""
import tempfile
import os.path
import uuid, magic
from datetime import datetime



class FileHandlerMinimal(object):
    """ Example of File handler for formish file upload support. """

    def store_file(self, fieldstorage):
        """ Method to store a file """

    def delete_file(self, filename):
        """ Method to delete a file """

    def get_file(self, filename):
        """ Method to delete a file """

    def file_exists(self, filename):
        """ Method to delete a file """

    def get_path_for_file(self, filename):
        """ Method to get a path for a file on disk """

    def cacheattr(self, filename):
        """ Method to get the mimetype of a file on disk """


class FileHandlerWeb(FileHandlerMinimal):
    """ include a url accessor """

    def get_url_for_file(self, identifier):
        """ return a url that can access the file """


class TempFileHandler(object):
    """
    File handler using python tempfile module to store file
    """

    def __init__(self):
        self.prefix = tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()

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

    def get_mimetype(self, filename):
        """ not required but might be handy """
        mimetype = magic.from_file(self._abs(filename), mime=True)
        return mimetype or 'application/octet-stream'

    def cacheattr(self, filename):
        try:
            mtime = datetime.fromtimestamp( os.path.getmtime(self._abs(filename)) )
        except OSError:
            raise KeyError
        return mtime

    def get_path_for_file(self, filename):
        return self._abs(filename)

    def get_file(self, filename):
        return open(self._abs(filename),'rb').read()

    def file_exists(self, filename):
        return os.path.exists(self._abs(filename))
    

class TempFileHandlerWeb(TempFileHandler):
    """
    Same as the temporary file handler but includes ability to include a resource and a url generator (if you want access to the temporary files on the website, e.g. for previews)
    """

    def __init__(self, default_url=None, resource_root='/filehandler',urlfactory=None):
        TempFileHandler.__init__(self)
        self.default_url = default_url
        self.resource_root = resource_root
        self.urlfactory = urlfactory

    def _urlfactory(self, identifier):
        return '%s/%s'% (self.resource_root, identifier)

    def get_url_for_file(self, identifier):
        """ Generate a url given an identifier """
        if identifier is None:
            return self.default_url.replace(' ', '+')
        if self.urlfactory:
            return self.urlfactory(identifier)
        return self._urlfactory(identifier)


        





