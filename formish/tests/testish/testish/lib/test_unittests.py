from testish.lib.base import TestCase
from testish.lib import forms
import unittest
import webob
import urllib
from BeautifulSoup import BeautifulSoup

class Test(unittest.TestCase):

    def request(self, d):
        r = webob.Request.blank('http://localhost/')
        r.method = 'POST'
        r.content_type = 'application/x-www-form-urlencoded'
        kvpairs = []
        for k in d.dottedkeys():
            lastsegment = k.split('.')[-1]
            try:
                int(lastsegment)
                k = '.'.join(k.split('.')[:-1])
            except ValueError:
                pass
            for v in d[k]:
                kvpairs.append( (k,v) )

        r.body = urllib.urlencode(kvpairs)
        print r.body
        return r

    def test_unit(self):
        for attr in dir(forms):
            if attr.startswith('unittest_'):
                getattr(forms,attr)(self)

    def assertRoundTrip(self, f, testdata):
        r = self.request(f._get_request_data())
        d = f.validate(r)
        self.assertEquals(d, testdata)

    def assertIdHasValue(self, f, id, v):
        soup = BeautifulSoup(f())
        self.assertEquals(soup.find(id=id)['value'],v)
        


    
if __name__ == '__main__':
    unittest.main()
