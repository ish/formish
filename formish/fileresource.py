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
import logging
log = logging.getLogger('formish')

# Binaries
IDENTIFY = '/usr/bin/identify'
CONVERT = '/usr/bin/convert'


class FileAccessorInterface(object):
    """
    A skeleton class that should be implemented so that the files resource can
    deliver files and operate a cache
    """
    mtime_cache = True

    def get_file(self, filename):
        """ Get the file contents """

    def cacheattr(self, filename, attr):
        """ get an attr on which the cache can base freshness """



class FileAccessor(object):

    def __init__(self):
        self.prefix = 'store-%s'%tempfile.gettempprefix()
        self.tempdir = tempfile.gettempdir()
        self.mtime_cache = True

    def _abs(self, filename):
        return '%s/%s%s'% (self.tempdir, self.prefix, filename)

    def get_file(self, filename):
        return open(self._abs(filename)).read()

    def cacheattr(self, filename):
        try:
            mtime = datetime.fromtimestamp( os.path.getmtime(self._abs(filename)) )
        except OSError:
            raise KeyError()
        return mtime




class FileResource(resource.Resource):
    """
    A simple file serving utility
    """

    def __init__(self, fileaccessor=None, filehandler=None, segments=None, cache=None):
        log.debug('formish.FileResource: initialising FileResource')
        if fileaccessor:
            self.fileaccessor = fileaccessor
        else:
            self.fileaccessor = FileAccessor()
        if filehandler:
            self.filehandler = filehandler
        else:
            self.filehandler = TempFileHandler()
        self.segments = segments
        if cache:
            self.cache = cache
        else:
            self.cache = Cache()


    @resource.child(resource.any)
    def child(self, request, segments):
        return FileResource(fileaccessor=self.fileaccessor, filehandler=self.filehandler, segments=segments, cache=self.cache), []


    def __call__(self, request):
        """
        Find the appropriate image to return including cacheing and resizing
        XXX ERROR CHECKING AND LOCKING NEEDED
        """
        if not self.segments:
            return None

        # get the requested filepath from the segments
        filename = self._get_requested_filename()
        f = self.get_file(request, filename, self.fileaccessor)
        if f:
            return f
        f = self.get_file(request, filename, self.filehandler)
        if f:
            return f


    def get_file(self, request, filename, fileaccessor):
        """ get the file through the cache and possibly resizing """
        mtime_cache = fileaccessor.mtime_cache
        # Check the file is up to date
        try:
            attr = fileaccessor.cacheattr(filename)
        except KeyError:
            return
        if attr is None or not self.cache.cache_ok(filename, attr, mtime=mtime_cache):
            data = fileaccessor.get_file(filename)
            self.cache.store(filename, data, attr, mtime=mtime_cache)

        # If we're trying to resize, check mtime on resized_cache
        size = get_size_from_dict(request.GET)
        size_suffix = self.get_size_suffix(size)
        if size:
            if attr is None or not self.cache.cache_ok(filename, attr, size_suffix, mtime=mtime_cache):
                resize_image(self.cache._abs(filename),
                             self.cache._abs(filename, size_suffix),
                             size, self.cache.resize_quality)
                self.cache.store_cacheattr(filename, attr, size_suffix, mtime=mtime_cache)

        data = self.cache.contents(filename, size_suffix)
        mimetype = self.cache.get_mimetype(filename, size_suffix)
        return http.ok([('content-type', mimetype )], data)


    def get_size_suffix(self, size):
        if size is None:
            return ''
        width, height = size
        if height or width:
            return '-%sx%s'% (width, height)


    def _get_requested_suffix(self):
        if '.' in self.segments[-1]:
            return self.segments[-1].split('.')[-1]
        return ''


    def _get_requested_filename(self):
        return '/'.join(self.segments)


    def _get_tempfile_path(self, filepath):
        return self.filehandler.get_path_for_file(urllib.unquote_plus(filepath))




def getmtime(f):
    if os.path.exists(f):
        return datetime.utcfromtimestamp(os.path.getmtime(f))
    return datetime(1970, 1, 1, 0, 0)



class Cache(object):
    # XXX ERROR CHECKING AND LOCKING NEEDED I THINK.. 

    def __init__(self,dir='cache', resize_quality=70):
        self.dir = dir
        self.resize_quality = resize_quality

    def contents(self, filename, size_suffix=''):
        return open(self._abs(filename,size_suffix=size_suffix), 'rb').read()


    def cacheattr(self, filename, size_suffix='', mtime=True):
        # By default the system uses the file mtime but if you set
        # a mtime_cache of false
        # you want to create a non temporal cache markerk
        if mtime == True:
            return getmtime(self._abs(filename, size_suffix=size_suffix))
        else:
            try:
                return open(self._abs('.%s-attrfile'%filename, size_suffix=size_suffix)).read()
            except IOError:
                return None


    def _abs(self, filename, size_suffix=''):
        return '%s/%s%s'% (self.dir, filename.replace('/','-'),size_suffix)


    def store(self, filename, data, attr, size_suffix='', mtime=True):
        open(self._abs(filename,size_suffix=size_suffix),'w').write(data)
        if mtime == False:
            # if we're not using mtimes for caching info, store with an attr file
            self.store_cacheattr(filename, attr, size_suffix='', mtime=mtime)


    def store_cacheattr(self, filename, attr, size_suffix='', mtime=True):
        open(self._abs('.%s-attrfile'%filename, size_suffix=size_suffix),'w').write(attr)


    def cache_ok(self, filename, attr, size_suffix='', mtime=True):
        cacheattr = self.cacheattr(filename, size_suffix=size_suffix, mtime=mtime)
        if mtime==True:
            return cacheattr >= attr
        return cacheattr == attr


    def get_mimetype(self, filename, size_suffix=''):
        return get_mimetype(self._abs(filename, size_suffix=size_suffix))



def resize_image(src_path, target_path, size, quality=70):
    """
    this is an example identify
    '/home/tim/Desktop/tim.jpg JPEG 48x48 48x48+0+0 DirectClass 8-bit 920b \n'
    """
    width, height = size
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
    if not width and not height:
        return None
    return (width, height)


def get_mimetype(filename):
    """
    use python-magic to guess the mimetype
    """
    mimetype = magic.from_file(filename, mime=True)
    return mimetype or 'application/octet-stream'

