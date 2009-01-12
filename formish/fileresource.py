"""
The fileresource provides a basic restish fileresource for assets and images

Requires ImageMagick for image resizing
"""
import tempfile
from datetime import datetime
import os.path
import magic
import subprocess
import urllib
from restish import http, resource


from formish.filehandler import TempFileHandler


# Binaries
IDENTIFY = '/usr/bin/identify'
CONVERT = '/usr/bin/convert'

class FileAccessor(object): 
    """
    A skeleton class that should be implemented so that the files resource can
    build caches, etc
    """

    def __init__(self):
        self.prefix = 'store-%s'%tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()


    def get_mimetype(self, filename):
        """
        Get the mime type of the file with this id
        """
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename)
        return magic.from_file(actualfilename, mime=True)


    def get_mtime(self, filename):
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename)
        return datetime.fromtimestamp( os.path.getmtime(actualfilename) )


    def get_file(self, filename):
        """
        Get the file object for this id
        """
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename)
        return open(actualfilename).read()

    def file_exists(self, filename):
        actualfilename = '%s/%s%s'% (self.tempdir, self.prefix, filename)
        return os.path.exists(actualfilename)
       

class FileResource(resource.Resource):
    """
    A simple file serving utility
    """

    def __init__(self, fileaccessor=None, filehandler=None, segments=None):
        if fileaccessor is None:
            self.fileaccessor = FileAccessor()
        else:
            self.fileaccessor = fileaccessor
        if filehandler is None:
            self.filehandler = TempFileHandler()
        else:
            self.filehandler = filehandler
        self.segments = segments

    def __call__(self, request):
        if not self.segments:    
            return None

        # This is our input filepath
        requested_filepath = self._get_requested_filepath()
 
        # Get the raw cache file path and mtime
        raw_cached_filepath = self._get_cachefile_path(requested_filepath)
        raw_cached_mtime = self._get_file_mtime(raw_cached_filepath)

        # Check to see if fa and temp exist
        fileaccessor_exists = self.fileaccessor.file_exists(requested_filepath)
        tempfile_path = self._get_tempfile_path(requested_filepath)
        tempfile_exists = os.path.exists(tempfile_path)

        if not fileaccessor_exists and not tempfile_exists:
            return None
       
        # work out which has changed most recently (if either is newer than cache)
        fileaccessor_mtime = self.fileaccessor.get_mtime(requested_filepath)
        tempfile_mtime = self._get_file_mtime(tempfile_path)
        source_mtime = max(fileaccessor_mtime, tempfile_mtime)
        if source_mtime > raw_cached_mtime:
            if fileaccessor_mtime > tempfile_mtime:
                filedata = self.fileaccessor.get_file(requested_filepath)
                mimetype = self.fileaccessor.get_mimetype(requested_filepath)
            else:
                filedata = open(tempfile_path).read()
                mimetype = get_mimetype(tempfile_path)
            open(raw_cached_filepath,'w').write(filedata)
        else:
            mimetype = get_mimetype(raw_cached_filepath)

        # If we're trying to resize, check mtime on resized_cache
        size_suffix = self._get_size_suffix(request)
        if size_suffix:
            cached_filepath = self._get_cachefile_path(requested_filepath, size_suffix)
            cached_mtime = self._get_file_mtime(cached_filepath)

            if not os.path.exists(cached_filepath) or source_mtime > cached_mtime:
                width, height = get_size_from_dict(request.GET)
                resize_image(raw_cached_filepath, cached_filepath, width, height)
        else:
            cached_filepath = raw_cached_filepath

        return http.ok([('content-type', mimetype )], open(cached_filepath, 'rb').read())
         

    def _get_requested_suffix(self):
        if '.' in self.segments[-1]:
            return self.segments[-1].split('.')[-1]
        return ''

    def _get_requested_filepath(self):
        return '/'.join(self.segments)

    def _get_cachefile_path(self,filepath,size_suffix=''):
        return 'cache/%s%s'% (filepath.replace('/','-'),size_suffix)

    def _get_tempfile_path(self, filepath):
        return self.filehandler.get_path_for_file(urllib.unquote_plus(filepath))

    def _get_file_mtime(self, filepath,size_suffix=''):
        if os.path.exists(filepath):
            return datetime.utcfromtimestamp(os.path.getmtime(filepath))
        return datetime(1970, 1, 1, 0, 0)

    def _get_fileaccessor_mtime(self, filepath):
        return self.fileaccessor.get_mtime(filepath)

    def _get_size_suffix(self, request):
        width, height = get_size_from_dict(request.GET)
        if height and width:
            return '-%sx%s'% (width, height)
        return ''

        

def resize_image(src_path, target_path, width, height, quality=70):
    """
    this is an example identify
    '/home/tim/Desktop/tim.jpg JPEG 48x48 48x48+0+0 DirectClass 8-bit 920b \n'
    """
    stdout = subprocess.Popen([IDENTIFY, src_path], \
                            stdout=subprocess.PIPE).communicate()[0]
    iwidth, iheight = [ int(s) for s in stdout.split(' ')[2].split('x')]
    if width is None:
        width = int(iwidth*(float(height)/float(iheight)))
    if height is None:
        height = int(iheight*(float(width)/float(iwidth)))
    subprocess.call([CONVERT, '-thumbnail', 
        '%sx%s'% (width, height), '-quality', str(quality), src_path, target_path])


def get_size_from_dict(data):
    """
    parse the dict for a width and height
    """
    size = data.get('size', None)
    if size is not None:
        width = int(size.split('x')[0])
        height = int(size.split('x')[1])
    else:
        width = data.get('width', None)
        if width is not None:
            width = int(width)
        height = data.get('height', None)
        if height is not None:
            height = int(height)
    return (width, height)


def get_mimetype(filename):
    """
    use python-magic to guess the mimetype
    """
    mimetype = magic.from_file(filename, mime=True)
    return mimetype or 'application/octet-stream'

