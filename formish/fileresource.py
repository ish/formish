"""
The fileresource provides a basic restish fileresource for assets and images

Requires ImageMagick for image resizing
"""
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

    def get_mtime(self, identifier):
        """
        Get the last modified time
        """

    def get_file(self, identifier):
        """
        Get the file object for this id
        """

class FileResource(resource.Resource):
    """
    Resource for serving files from the database or temporary upload area.
    """

    def __init__(self, fileaccessor=FileAccessor(),
                 filehandler=TempFileHandler(), segments=None):
        resource.Resource.__init__(self)
        self.fileaccessor = fileaccessor
        self.filehandler = filehandler
        if segments is None:
            return
        # If it's a temp file, just return it... 
        # XXX This it wrong... it should still cache and resize
        filepath = '/'.join(segments)
        if '.' in filepath:
            splits = filepath.split('.')
            filename, suffix = '.'.join(splits[:-1]), splits[-1]
        else:
            filename = filepath
            suffix = ''
        self.tempfile = filehandler.get_path_for_file( \
            urllib.unquote_plus(filepath))
        if os.path.exists(self.tempfile):
            return 
        # Otherwise it must be a resource so check if it needs cacheing
        self.tempfile =  'cache/%s'% (filename.replace('/','-'))
        if segments[0] != '':
            if os.path.exists(self.tempfile):
                mtime = self.fileaccessor.get_mtime(filename)
                cache_mtime = datetime.utcfromtimestamp( \
                                    os.path.getmtime(self.tempfile))
                if mtime is None or mtime > cache_mtime:
                    rebuild_cache = True
                else:
                    rebuild_cache = False
            else:
                rebuild_cache = True
            if rebuild_cache:
                data = self.fileaccessor.get_file(filename)
                cache_fp = file(self.tempfile,'w')
                cache_fp.write(data)
                cache_fp.close()

    def resource_child(self, request, segments):
        """
        if we have any children, recurse deeper
        """
        return FileResource(self.fileaccessor, self.filehandler, segments), ()

    def make_response(self, filename, request):
        """
        build the http response
        """
        width, height = get_size_from_dict(request.GET)
        if not (width is None and height is None):
            mtime = datetime.utcfromtimestamp(os.path.getmtime(filename))
            filename = '%s-%sx%s'% (filename, width, height)
            if os.path.isfile(filename):
                cache_mtime = datetime.utcfromtimestamp( \
                                    os.path.getmtime(filename))
                if mtime > cache_mtime:
                    rebuild_cache = True
                else:
                    rebuild_cache = False
            else:
                rebuild_cache = True
            
            if not os.path.exists(filename) or rebuild_cache:
                resize_image(self.tempfile, filename, width, height)
                
        return http.ok([('content-type', get_mimetype(filename) )], \
                       open(filename, 'rb').read())

    @resource.GET()
    def get_file(self, request):
        """
        Get a http response for this tempfile
        """
        return self.make_response(self.tempfile, request)
    


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

