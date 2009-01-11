"""
Standard filehandlers for temporary storage of file uploads. Uses tempfile to
make temporary files
"""
import tempfile
import os.path
import uuid, magic



class FileHandlerMinimal(object):
    """ Example of File handler for formish file upload support. """

    def store_file(self, fieldstorage):
        """ Method to store a file """

    def get_path_for_file(self, filename):
        """ Method to get a path for a file on disk """



class FileHandlerWeb(FileHandlerMinimal):
    """ include a url accessor """
    def get_url_for_file(self, identifier):
        """ return a url that can access the file """


class TempFileHandler(FileHandlerMinimal):
    """
    File handler using python tempfile module to store file
    """


    def store_file(self, fieldstorage):
        """
        Given a filehandle, store the file and return an identifier, in this
        case the original filename
        """
        fileno, filename = tempfile.mkstemp( \
                        suffix='%s-%s'% (uuid.uuid4().hex,fieldstorage.filename))
        filehandle = os.fdopen(fileno, 'wb')
        filehandle.write(fieldstorage.value)
        filehandle.close()
        prefix = tempfile.gettempprefix()
        tempdir = tempfile.gettempdir()
        filename = ''.join( filename[(len(tempdir)+len(prefix)+1):] )
        return filename

    def delete_file(self, filename):
        """
        remove the tempfile
        """
        prefix = tempfile.gettempprefix()
        tempdir = tempfile.gettempdir()
        filename = '%s/%s%s'% (tempdir, prefix, filename)
        os.remove(filename)


    def get_path_for_file(self, filename):
        """
        given the filename, get the path for the temporary file
        """
        prefix = tempfile.gettempprefix()
        tempdir = tempfile.gettempdir()
        return '%s/%s%s'% (tempdir, prefix, filename)

    def get_mimetype(self, filename):
        """
        use python-magic to guess the mimetype or use application/octet-stream
        if no guess
        """
        prefix = tempfile.gettempprefix()
        tempdir = tempfile.gettempdir()
        mimetype = magic.from_file('%s/%s%s'% \
                    (tempdir,prefix,filename),mime=True)
        return mimetype or 'application/octet-stream'


class TempFileHandlerWeb(TempFileHandler):
    """
    Same as the temporary file handler but includes ability to include a resource and a url generator (if you want access to the temporary files on the website, e.g. for previews)
    """

    def __init__(self, default_url=None,
                 resource_root='/filehandler',urlfactory=None):
        TempFileHandler.__init__(self)
        self.default_url = default_url
        self.resource_root = resource_root
        self.urlfactory = urlfactory

    def get_url_for_file(self, identifier):
        """
        Generate a url given an identifier
        """
        if self.urlfactory is not None:
            return self.urlfactory(identifier)
        if id is None:
            return self.default_url.replace(' ', '+')
        else:
            return '%s/%s'% (self.resource_root, identifier)
        





