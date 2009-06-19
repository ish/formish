"""
The validation module converts data to and from request format (or at least
calls the converters that do so) and also converts dotted numeric formats into
sequences (e.g. a.0 and a.1 onto a[0] and a[1]). It also includes some
validation exceptions.
"""

class FormishError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """

    def __init__(self, message, *args):
        Exception.__init__(self, message, *args)
        self.message = message

    def __str__(self):
        return self.message
    __unicode__ = __str__

    # Hide Python 2.6 deprecation warnings.
    def _get_message(self): return self._message
    def _set_message(self, message): self._message = message
    message = property(_get_message, _set_message)


class FormError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass

    
class NoActionError(FormishError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass

