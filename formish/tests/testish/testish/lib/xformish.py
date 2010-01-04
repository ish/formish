"""
General purpose formish extensions.
"""

from formish import widgets
from convertish.convert import ConvertError
from convertish.convert import string_converter

import urllib, urllib2

class DateParts(widgets.DateParts):

    def __init__(self, **k):
        k['day_first'] = k.pop('l10n').is_day_first()
        super(DateParts, self).__init__(**k)


class ApproximateDateParts(widgets.DateParts):

    template = 'field.ApproximateDateParts'

    def to_request_data(self, field, data):
        if data is None:
            return {'year': [''], 'month': [''], 'day': ['']}
        parts = [i for i in data.split('-')]
        parts.extend(['']*(3-len(parts)))
        return {'year': [parts[0]], 'month': [parts[1]], 'day': [parts[2]]}

    def from_request_data(self, field, data):
        # Collect all the parts from the request.
        parts = (data['year'][0].strip(), data['month'][0], data['day'][0])
        if not parts[0] and (parts[1] or parts[2]):
            raise ConvertError("Invalid date")
        elif not parts[1] and parts[2]:
            raise ConvertError("Invalid date")
        # Discard the unspecified parts
        parts = [p for p in parts if p]
        # Ensure they're all integers (don't record the result, we don't care).
        try:
            [int(p) for p in parts]
        except ValueError:
            raise ConvertError("Invalid date")
        return '-'.join(parts)


class ReCAPTCHA(widgets.Input):

    template = 'field.ReCAPTCHA'

    API_SSL_SERVER="https://api-secure.recaptcha.net"
    API_SERVER="http://api.recaptcha.net"
    VERIFY_SERVER="api-verify.recaptcha.net"
    USER_AGENT = "reCAPTCHA Formish"

    def __init__(self, publickey, privatekey, environ, **k):
        self.use_ssl = k.pop('use_ssl', False)
        widgets.Input.__init__(self, **k)
        self.publickey = publickey
        self.privatekey = privatekey
        self.remoteip = environ.get('REMOTE_ADDR', '127.0.0.1')

    def pre_parse_incoming_request_data(self, field, request_data):
        """ reCaptcha won't let you use your own field names so we move them """
        full_request_data = field.form.request_data
        print 'full_request_data',full_request_data
        return {'recaptcha_challenge_field': full_request_data['recaptcha_challenge_field'], 
                'recaptcha_response_field': full_request_data['recaptcha_response_field'],}

    def from_request_data(self, field, data):
        print 'in from ',data
        params = urllib.urlencode({
                        'privatekey': self.privatekey,
                        'remoteip' :  self.remoteip,
                        'challenge':  data['recaptcha_challenge_field'][0],
                        'response' :  data['recaptcha_response_field'][0],
                        })
        request = urllib2.Request (
            url = "http://%s/verify"%self.VERIFY_SERVER,
            data = params,
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "User-agent": self.USER_AGENT
                  }
            )
        response = urllib2.urlopen(request)
        return_values = response.read().splitlines()
        response.close()
        return_code = return_values[0]
        if (return_code == "true"):
            return string_converter(field.attr).to_type('True')
        else:
            raise ConvertError('reCAPTCHA failed')




