"""
General purpose utility module.
"""

import re


_IDENTIFIER_REGEX = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')


def title_from_name(name):
    """
    Create a title from an attribute name.
    """
    def _():
        """
        Generator to convert parts of title
        """
        try:
            int(name)
            yield 'Item #%s'% name
            return
        except ValueError:
            pass

        it = iter(name)
        last = None

        while 1:
            ch = it.next()
            if ch == '_':
                if last != '_':
                    yield ' '
            elif last in (None,'_'):
                yield ch.upper()
            elif ch.isupper() and not last.isupper():
                yield ' '
                yield ch.upper()
            else:
                yield ch
            last = ch
    return ''.join(_())


def valid_identifier(name):
    """
    Test that name is a valid-ish Python identifier.
    """
    return _IDENTIFIER_REGEX.match(name) is not None


def form_in_request(request):
    """
    Return the name of the form for the request or None.
    """
    if request.method == 'POST':
        return request.POST.get('__formish_form__')
    if request.method == 'GET':
        return request.GET.get('__formish_form__')
    return None


def get_post_charset(request):
    """Locate the unicode encoding of the POST'ed form data.

    To work reliably you must do the following:

      - set the form's enctype attribute to 'multipart/form-data'
      - set the form's accept-charset attribute, probably to 'utf-8'
      - add a hidden form field called '_charset_'

    For instance::

      <form action="foo" method="post" enctype="multipart/form-data" accept-charset="utf-8">
        <input type="hidden" name="_charset_" />
        ...     
      </form> 
    """     
    # Try the magic '_charset_' field, Mozilla and IE set this.
    charset = request.POST.get('_charset_', None)
    if charset:
        return charset

    # Look in the 'content-type' request header
    content_type = request.headers.get('content-type')
    if content_type:
        charset = dict([ s.strip().split('=') \
                 for s in content_type.split(';')[1:] ]).get('charset')
        if charset:
            return charset

    return 'utf-8'

