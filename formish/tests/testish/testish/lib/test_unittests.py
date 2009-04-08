from testish.lib import forms
import unittest
import webob
import urllib
from BeautifulSoup import BeautifulSoup
from dottedish import dotted
from urllib import urlencode

def build_request(formname, data):
    d = dotted(data)
    e = {'REQUEST_METHOD': 'POST'}
    request = webob.Request.blank('/',environ=e)
    fields = []
    fields.append( ('_charset)','UTF-8') )
    fields.append( ('__formish_form__','form') )
    for k, v in d.dotteditems():
        fields.append( (k,v) )
    fields.append( ('submit','Submit') )
    request.body = urlencode( fields )

    return request

class Test(unittest.TestCase):

    def request(self, d):
        r = webob.Request.blank('http://localhost/')
        r.method = 'POST'
        r.content_type = 'application/x-www-form-urlencoded'
        kvpairs = [('__formish_form__', 'form')]
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
        return r

    def test_unit(self):
        for attr in dir(forms):
            if attr in ['form_ReCAPTCHA']:
                continue
            def default_unittest(formdef):
                """ We just make sure we can build the form """
                f = formdef(None)    
                return
                ## I'd like to do an automatic check on validation but how?
                #f.defaults = {}
                #request = build_request('form',f.request_data)
                #f.validate(request)


            if attr.startswith('form_'):
                formdef = getattr(forms,attr)
                unittest_attr = attr.replace('form_','unittest_')
                if hasattr(forms,unittest_attr):
                    # Pass the formdef into the unittest
                    getattr(forms,unittest_attr)(self,formdef)
                else:
                    default_unittest(formdef)

    def assertRoundTrip(self, f, testdata):
        r = self.request(f._get_request_data())
        d = f.validate(r)
        self.assertEquals(d, testdata)

    def assertIdHasValue(self, f, id, v):
        soup = BeautifulSoup(f())
        self.assertEquals(soup.find(id=id)['value'],v)
        
    def assertIdAttrHasValue(self, f, id, attr, v):
        soup = BeautifulSoup(f())
        s = soup.find(id=id)
        assert 'attr' in s
        self.assertEquals(s['attr'],v)

    def assertIdAttrHasNoValue(self, f, id, attr):
        soup = BeautifulSoup(f())
        s = soup.find(id=id)
        assert 'attr' not in s

    
if __name__ == '__main__':
    unittest.main()
