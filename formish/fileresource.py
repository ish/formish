import base64
from datetime import datetime
import os.path
import magic
import subprocess
import urllib
from restish import http, resource


# Binaries
IDENTIFY = '/usr/bin/identify'
CONVERT = '/usr/bin/convert'

class FileAccessor(object):
    """
    A skeleton class that should be implemented so that the files resource can
    build caches, etc
    """

    def get_mimetype(self, id):
        """
        Get the mime type of the file with this id
        """

    def get_file(self, id):
        """
        Get the file object for this id
        """

class FileResource(resource.Resource):
    """
    Resource for serving files from the database or temporary upload area.
    """

    def __init__(self, fileaccessor=FileAccessor(), segments=None):
        resource.Resource.__init__(self)
        if segments is None:
            return
        self.fileaccessor = fileaccessor
        # If it's a temp file, just return it... 
        # XXX This it wrong... it should still cache and resize
        filename = urllib.unquote_plus('/'.join(segments))
        self.tempfile = FileHandler().get_path_for_file(filename)
        if os.path.exists(self.tempfile):
            return
        # Otherwise it must be a resource so check if it needs cacheing
        self.tempfile =  'cache/%s'%(segments[0])
        if segments[0] != '':
            if os.path.exists(self.tempfile):
                mtime = self.fileaccessor.get_mtime(segments[0])
                cache_mtime = datetime.utcfromtimestamp(os.path.getmtime(self.tempfile))
                if mtime is None or mtime > cache_mtime:
                    rebuild_cache = True
                else:
                    rebuild_cache = False
            else:
                rebuild_cache = True
            if rebuild_cache:
                stored_fp = self.fileaccessor.get_file(segments[0])
                cache_fp = file(self.tempfile,'w')
                cache_fp.write(base64.b64decode(stored_fp.read()))
                cache_fp.close()

    def resource_child(self, request, segments):
        return FilesResource(self.fileaccessor, segments), ()

    def make_response(self, filename, request):
        width, height = getSizeFromDict(request.GET)
        if not (width is None and height is None):
            mtime = datetime.utcfromtimestamp(os.path.getmtime(filename))
            filename = '%s-%sx%s'%(filename,width,height)
            if os.path.isfile(filename):
                cache_mtime = datetime.utcfromtimestamp(os.path.getmtime(filename))
                if mtime > cache_mtime:
                    rebuild_cache = True
                else:
                    rebuild_cache = False
            else:
                rebuild_cache = True
            
            if not os.path.exists(filename) or rebuild_cache:
                resizeImage(self.tempfile, filename, width, height)
                
        return http.ok([('content-type', get_mimetype(filename) )],open(filename, 'rb').read())

    @resource.GET()
    def get_file(self, request):
        return self.make_response(self.tempfile, request)
    


def resizeImage(srcPath, targetPath, width, height, quality=70):
    # this is an example identify
    # '/home/tim/Desktop/tim.jpg JPEG 48x48 48x48+0+0 DirectClass 8-bit 920b \n'
    stdout = subprocess.Popen([IDENTIFY,srcPath],stdout=subprocess.PIPE).communicate()[0]
    iwidth, iheight = [ int(s) for s in stdout.split(' ')[2].split('x')]
    if width is None:
        width = int(iwidth*(float(height)/float(iheight)))
    if height is None:
        height = int(iheight*(float(width)/float(iwidth)))
    subprocess.call([CONVERT, '-thumbnail', '%sx%s'%(width, height), '-quality', str(quality), srcPath, targetPath])


def getSizeFromDict(d):
    size = d.get('size',None)
    if size is not None:
        width = int(size.split('x')[0])
        height = int(size.split('x')[1])
    else:
        width = d.get('width',None)
        if width is not None:
            width = int(width)
        height = d.get('height',None)
        if height is not None:
            height = int(height)
    return (width, height)


def get_mimetype(filename):
    mimetype = magic.from_file(filename,mime=True)
    return mimetype or 'application/octet-stream'

