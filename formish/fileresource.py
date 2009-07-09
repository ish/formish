"""
The fileresource provides a basic restish fileresource for assets and images

Requires ImageMagick for image resizing
"""
import tempfile, os, subprocess, shutil
from restish import http, resource

from formish import util
from formish.filestore import CachedTempFilestore, FileSystemHeaderedFilestore

import logging
log = logging.getLogger('formish')

# Binaries
IDENTIFY = '/usr/bin/identify'
CONVERT = '/usr/bin/convert'


class FileResource(resource.Resource):
    """
    A simple file serving utility
    """

    @classmethod
    def quickstart(cls, store_dirname, cache_dirname):
        """
        Create a simple, file-system based FileResource configured with an
        application store and a caching store.
        """
        store = CachedTempFilestore(FileSystemHeaderedFilestore(root_dir=store_dirname))
        cache = CachedTempFilestore(FileSystemHeaderedFilestore(root_dir=cache_dirname))
        return cls(store, cache)

    def __init__(self, filestores=None, cache=None):
        """
        Create a FileResource to serve application and/or cached files.

        Configuring application filestore(s) will allow the resource to serve
        files stored by the application. Configuring a cache filestore will
        allow the resource to cache application files, including resized
        images.

        The resource is able to serve files from any number of application
        filestores. Passing a single filestore as 'filestores' configures the
        resource to serve all files from a single, unnamed store; passing a
        dict as 'filestores' configures the resource to serve files from a
        named filestore, using the dict keys as the filestore names. A dict key
        of None is used to represent the unnamed filestore, allowing an
        application to configure the resource to serve files from a default and
        a set of named filestores.
        """
        self.cache = cache
        # Build a dict of filestores.
        if filestores is None:
            filestores = {}
        elif not isinstance(filestores, dict):
            filestores = {None: filestores}
        # Add the 'tmp' filestore is not provided.
        if 'tmp' not in filestores:
            filestores['tmp'] = CachedTempFilestore()
        self.filestores = filestores
        self.resize_quality = 70

    @resource.child(resource.any)
    def child(self, request, segments):
        """
        Find the appropriate image to return including cacheing and resizing
        """
        # Build the full filename from the segments.
        filestore, key = util.decode_file_resource_path('/'.join(segments))
        # get the requested filepath from the segments
        etag = str(request.if_none_match)
        f = self.get_file(request, filestore, key, etag)
        if f:
            return f
        return http.not_found()

    def get_file(self, request, filestore_name, filename, etag):
        """ get the file through the cache and possibly resizing """

        # Turn the filestore name into a filestore
        try:
            filestore = self.filestores[filestore_name]
        except KeyError:
            return None

        # Check the file is up to date
        try:
            cache_tag, headers, f = filestore.get(filename, etag)
            content_type = dict(headers)['Content-Type']
        except KeyError:
            # XXX if the original is not their, clear resize cache (this would mean a globbing delete every request!)
            # cache_filename = filestore.name+'_'+filename
            # self.cache.delete(cache_filename, glob=True)
            return 
        width, height = get_size_from_dict(request.GET)
        if request.GET.get('crop'):
            crop = True
            cropmark = '-crop'
        else:
            crop = False
            cropmark = ''
        size= get_size_suffix(width, height)

        if not size:
            if f:
                data = f.read()
                f.close()
                return http.ok([('Content-Type', content_type ),('ETag', cache_tag)], data)
            else:
                return http.not_modified([('ETag', cache_tag)])

        try:
            cache_filename = (filestore_name or '')+'_'+filename+size+cropmark
            resized_cache_tag, headers, rf = self.cache.get(cache_filename, etag)
            content_type = dict(headers)['Content-Type']
            resize_needed = resized_cache_tag != cache_tag
            if resize_needed and rf is not None:
                rf.close()
            
        except KeyError:
            resize_needed = True

        if resize_needed:
            if f is None:
                try:
                    cache_tag, headers, f = filestore.get(filename)
                    content_type = dict(headers)['Content-Type']
                except KeyError:
                    return 
            rf = resize_image(f, (width, height), quality=self.resize_quality, crop=crop)
            f.close()
            self.cache.put(cache_filename, rf, cache_tag, [('Content-Type', content_type)])
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
       



def resize_image(src_fh, size, quality=70, crop=False):
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

    if crop:
        subprocess.call([CONVERT, '-thumbnail',
        '%sx%s^'% (width, height), '-crop','%sx%s+0+0'% (width, height),'-gravity','center', '-quality', str(quality), filename, resized_filename])
    else:
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

