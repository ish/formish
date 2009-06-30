ReCAPTCHA and Formish Custom Widgets
====================================

Someone posted a comment in my last blog entry about 'why another form library?' (as predicted I suppose). My personal opinion is that it's about easy of use but that is a difficult thing to describe. So I thought I'd challenge myself to port a Tosca Widget widget to see what it would look like in formish. I decided to include the ReCAPTCHA widget to make it a little more interesting.

First thing was to write the Widget python code which went roughly as follows. First we set up the widget header with some constants..

.. code-block:: python

    import urllib, urllib2
    from validatish import ConvertError
    from convertish.convert import string_converter

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



This was the easy bit.. next we need to add the recaptcha code.. 


.. code-block:: python

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

This code just prepares a request to make to the captcha server and reads the result. Now this would be it for the python code but unfortunately captcha widgets don't let you define your own name for the fields. This is just what the ``pre_parse_request`` method is for. It lets you munge some code up front if needed. In this case we move the captcha data into the right request field names.

.. code-block:: python

    def pre_parse_incoming_request_data(self, field, request_data):
        """ reCaptcha won't let you use your own field names so we move them """
        full_request_data = field.form.request_data
        print 'full_request_data',full_request_data
        return {'recaptcha_challenge_field': full_request_data['recaptcha_challenge_field'], 
                'recaptcha_response_field': full_request_data['recaptcha_response_field'],}

Finally we need a template

.. code-block:: mako

    <%page args="field" />
    <%
    if field.error:
        args = "k=%s&amp;error=incorrect-captcha-sol"%field.widget.publickey
    else: 
        args = "k=%s"%field.widget.publickey
    if field.widget.use_ssl:
        apiserver = field.widget.API_SSL_SERVER
    else:
        apiserver = field.widget.API_SERVER
    %>
    <script type="text/javascript" src="${apiserver}/challenge?${args|n}"></script>
    <noscript>
      <iframe src="${apiserver}/noscript?${args|n}" height="300" width="500" frameborder="0"></iframe><br />
      <textarea name="${field.name}.recaptcha_challenge_field" rows="3" cols="40"></textarea>
      <input type="hidden" name="${field.name}.recaptcha_response_field" value="manual_challenge" />
    </noscript>

So the widget just works out if there is an error and prepares the appropriate args and also plans for ssl if needed. 

And using the widget is as simple as .. (ReCAPTCHA isn't in the current release as I only wrote it tonight)

.. code-block:: python

    import schemaish, formish
    schema = schemaish.Structure()
    schema.add('recaptcha', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    publickey = '6LcSqgQAAAAAAA1A6MJZXGpY35ZsdvwxvsEq0KQD'
    privatekey = '6LcSqgQAA....................7ugn72Hi2va'
    form['recaptcha'].widget = formish.ReCAPTCHA(publickey, privatekey, request.environ)

Have a look at the widget in action at `http://ish.io:8891/ReCAPTCHA <http://ish.io:8891/ReCAPTCHA>`_ .

