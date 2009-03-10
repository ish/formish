"""
The fileresource provides a basic restish fileresource for assets and images

Requires ImageMagick for image resizing
"""
import tempfile, os, subprocess, shutil
from restish import http, resource

from formish.filestore import CachedTempFilestore

import logging
log = logging.getLogger('formish')

# Binaries
IDENTIFY = '/usr/bin/identify'
CONVERT = '/usr/bin/convert'


class FileResource(resource.Resource):
    """
    A simple file serving utility
    """

    def __init__(self, filestores=None, filestore=None, segments=None, cache=None):
        if cache:
            self.cache = cache
        else:
            self.cache =  CachedTempFilestore(root_dir='cache')
        if filestore is not None:
            self.filestores = [filestore]
        elif filestores is not None:
            self.filestores = filestores
        else:
            tempfilestore = CachedTempFilestore(name='tmp')
            filestore = CachedTempFilestore(root_dir='store', name='store')
            self.filestores = [filestore, tempfilestore]
        self.filestores.append(self.cache)
        self.segments = segments
        self.resize_quality = 70


    @resource.child(resource.any)
    def child(self, request, segments):
        return FileResource(filestores=self.filestores, segments=segments, cache=self.cache), []


    def __call__(self, request):
        """
        Find the appropriate image to return including cacheing and resizing
        """
        if not self.segments:
            return None
        filename = '/'.join(self.segments)

        # get the requested filepath from the segments
        etag = str(request.if_none_match)
        for filestore in self.filestores:
            f = self.get_file(request, filestore, filename, etag)
            if f:
                return f
        return http.not_found()


    def get_file(self, request, filestore, filename, etag):
        """ get the file through the cache and possibly resizing """
        # Check the file is up to date
        try:
            cache_tag, content_type, f = filestore.get(filename, etag)
        except KeyError:
            # XXX if the original is not their, clear resize cache (this would mean a globbing delete every request!)
            # cache_filename = filestore.name+'_'+filename
            # self.cache.delete(cache_filename, glob=True)
            return 
        width, height = get_size_from_dict(request.GET)
        size= get_size_suffix(width, height)

        if not size:
            if f:
                data = f.read()
                f.close()
                return http.ok([('Content-Type', content_type ),('ETag', cache_tag)], data)
            else:
                return http.not_modified([('ETag', cache_tag)])

        try:
            cache_filename = filestore.name+'_'+filename+size
            resized_cache_tag, content_type, rf = self.cache.get(cache_filename, etag)
            resize_needed = resized_cache_tag != cache_tag
            if resize_needed and rf is not None:
                rf.close()
            
        except KeyError:
            resize_needed = True

        if resize_needed:
            if f is None:
                try:
                    cache_tag, content_type, f = filestore.get(filename)
                except KeyError:
                    return 
            rf = resize_image(f, (width, height), self.resize_quality)
            f.close()
            self.cache.put(cache_filename, rf, cache_tag, content_type)
            rf.seek(0)
            data = rf.read()
            rf.close()
            return http.ok([('Content-Type', content_type ),('ETag', cache_tag)], data)
        
        if rf:
            data = rf.read()
            rf.close()
            return http.ok([('Content-Type', content_type ),('ETag', cache_tag)], data)
        else:
            return http.not_modified([('ETag', cache_tag)])
       



def resize_image(src_fh, size, quality=70):
    """
    this is an example identify
    '/home/tim/Desktop/tim.jpg JPEG 48x48 48x48+0+0 DirectClass 8-bit 920b \n'
    """
    fileno, filename = tempfile.mkstemp()
    fh = os.fdopen(fileno, 'wb')
    shutil.copyfileobj(src_fh, fh)
    fh.close()
    resized_filename = filename + '-resized'
    width, height = size
    stdout = subprocess.Popen([IDENTIFY, filename], \
                            stdout=subprocess.PIPE).communicate()[0]
    iwidth, iheight = [int(s) for s in stdout.split(' ')[2].split('x')]
    if width is None:
        width = int(iwidth*(float(height)/float(iheight)))
    if height is None:
        height = int(iheight*(float(width)/float(iwidth)))
    subprocess.call([CONVERT, '-thumbnail',
        '%sx%s'% (width, height), '-quality', str(quality), filename, resized_filename])
    return open(resized_filename,'rb')

def get_size_suffix(width, height):
    if width is None and height is None:
        return ''
    if height or width:
        return '-%sx%s'% (width, height)

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
        return (None, None)
    return (width, height)

