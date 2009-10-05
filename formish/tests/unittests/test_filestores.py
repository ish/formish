# -*- coding: utf-8
from cStringIO import StringIO
import os.path
import shutil
import tempfile
import unittest

from formish.filestore import CachedTempFilestore, FileSystemHeaderedFilestore


class TestFileSystemHeaderedFileStore(unittest.TestCase):

    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.store = FileSystemHeaderedFilestore(self.dirname)

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_put(self):
        self.store.put('foo', [('Cache-Tag', '1'), ('Content-Type', 'text/plain')], StringIO("Yay!"))
        assert file(os.path.join(self.dirname, 'foo'), 'rb').read() == 'Cache-Tag: 1\nContent-Type: text/plain\n\nYay!'
        (headers, f) = self.store.get('foo')
        try:
            assert headers == [('Cache-Tag', '1'), ('Content-Type', 'text/plain')]
            assert f.read() == 'Yay!'
        finally:
            f.close()

    def test_put_headersdict(self):
        self.store.put('foo', {'Cache-Tag':'1', 'Content-Type':'text/plain'}, StringIO("Yay!"))
        assert file(os.path.join(self.dirname, 'foo'), 'rb').read() == 'Cache-Tag: 1\nContent-Type: text/plain\n\nYay!'

    def test_get(self):
        self.store.put('foo', [('Cache-Tag', '1'), ('Content-Type', 'text/plain')], StringIO("Yay!"))
        headers, f = self.store.get('foo')
        try:
            assert headers == [('Cache-Tag', '1'), ('Content-Type', 'text/plain')]
            assert f.read() == 'Yay!'
        finally:
            f.close()

    def test_headers(self):
        self.store.put('foo', [('foo', 'foo'), ('bar', 'bar')], StringIO('Yay!'))
        (headers, f) = self.store.get('foo')
        try:
            assert headers == [('foo', 'foo'), ('bar', 'bar')]
            assert f.read() == 'Yay!'
        finally:
            f.close()

    def test_not_found(self):
        self.assertRaises(KeyError, self.store.get, 'not_found')

    def test_delete(self):
        self.store.put('foo', [], StringIO('foo'))
        self.store.delete('foo')
        self.assertRaises(KeyError, self.store.get, 'foo')

    def test_delete_glob(self):
        self.store.put('foo', [], StringIO('foo'))
        self.store.delete('fo', glob=True)
        self.assertRaises(KeyError, self.store.get, 'foo')

    def test_unicode(self):
        gbp = '£'.decode('utf-8')
        self.store.put('foo', [('a', gbp)], StringIO('foo'))
        (headers, f) = self.store.get('foo')
        headers = dict(headers)
        assert isinstance(headers['a'], unicode)
        assert headers['a'] == gbp


class TestCachedTempFilestore(unittest.TestCase):

    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.store = CachedTempFilestore(FileSystemHeaderedFilestore(self.dirname))

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_put(self):
        self.store.put('foo', StringIO('bar'), '1', [('Content-Type', 'text/plain')])
        assert file(os.path.join(self.dirname, 'foo'), 'rb').read() == 'Cache-Tag: 1\nContent-Type: text/plain\n\nbar'

    def test_put_noheaders(self):
        self.store.put('foo', StringIO('bar'), '1')
        self.assertEqual(open(os.path.join(self.dirname, 'foo'), 'rb').read(),
        'Cache-Tag: 1\n\nbar')

    def test_get(self):
        self.store.put('foo', StringIO('bar'), '1', [('Content-Type', 'text/plain')])
        (cache_tag, headers, f) = self.store.get('foo')
        try:
            assert cache_tag == '1'
            assert headers == [('Content-Type', 'text/plain')]
            assert f.read() == 'bar'
        finally:
            f.close()

    def test_get_cache_hit(self):
        self.store.put('foo', StringIO('bar'), '1', [('Content-Type', 'text/plain')])
        (cache_tag, headers, f) = self.store.get('foo', cache_tag='1')
        assert cache_tag == '1'
        assert headers == [('Content-Type', 'text/plain')]
        assert f is None

    def test_get_cache_miss(self):
        self.store.put('foo', StringIO('bar'), '1', [('Content-Type', 'text/plain')])
        (cache_tag, headers, f) = self.store.get('foo', cache_tag='miss')
        try:
            assert cache_tag == '1'
            assert headers == [('Content-Type', 'text/plain')]
            assert f.read() == 'bar'
        finally:
            f.close()

    def test_missing(self):
        self.assertRaises(KeyError, self.store.get, 'not_found')

    def test_none_cache_tag(self):
        self.store.put('foo', StringIO('bar'), None, [('Content-Type', 'text/plain')])
        (cache_tag, headers, f) = self.store.get('foo', cache_tag='None')
        try:
            assert cache_tag is None
            assert headers == [('Content-Type', 'text/plain')]
            assert f
        finally:
            f.close()
        (cache_tag, content_type, f) = self.store.get('foo', cache_tag='')
        try:
            assert cache_tag is None
            assert headers == [('Content-Type', 'text/plain')]
            assert f
        finally:
            f.close()

    def test_delete(self):
        self.assertRaises(OSError, self.store.delete, 'not_found')

