import re


class FormsError(Exception):
    """
    Base class for all Forms errors. A single string, message, is accepted and
    stored as an attribute.
    
    The message is not passed on to the Exception base class because it doesn't
    seem to be able to handle unicode at all.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message


class FormError(FormsError):
    """
    Form validation error. Raise this, typically from a submit callback, to
    signal that the form (not an individual field) failed to validate.
    """
    pass
    
    
class FieldError(FormsError):
    """
    Base class for field-related exceptions. The failure message and the failing
    field name are stored as attributes.
    """
    def __init__(self, message, fieldName=None):
        FormsError.__init__(self, message)
        self.fieldName = fieldName

class ConversionError(FieldError):
    """
    Exception that signals that a type conversion failed.
    """
    pass        
    
class FieldValidationError(FieldError):
    """
    Exception that signals that a field failed to validate.
    """
    pass
    
    
class FieldRequiredError(FieldValidationError):
    """
    Exception that signals that a field that is marked as required was not
    entered.
    """
    pass
    
    
class RequiredValidator(object):
    
    def validate(self, field, value):
        if value is None:
            raise FieldRequiredError, 'Required'

    
class LengthValidator(object):
    """Validate the length of the value is within a given range. 
    """
    
    def __init__(self, min=None, max=None, unit="characters"):
        self.min = min
        self.max = max
        self.unit = unit
        assert self.min is not None or self.max is not None
        
    def validationErrorMessage(self, field):
        if self.min is not None and self.max is None:
            return 'Must be at least %r %s'%(self.min, self.unit)
        if self.min is None and self.max is not None:
            return 'Must be at most %r %s'%(self.max, self.unit)
        return 'Must be between %r and %r %s'%(self.min, self.max, self.unit)
    
    def validate(self, field, value):
        if value is None:
            return
        length = len(value)
        if self.min is not None and length < self.min:
            raise FieldValidationError, self.validationErrorMessage(field)
        if self.max is not None and length > self.max:
            raise FieldValidationError, self.validationErrorMessage(field)
            
            
class RangeValidator(object):
    """Validate the size of the value is within is given range.
    """
    
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max
        assert self.min is not None or self.max is not None
        
    def validationErrorMessage(self, field):
        if self.min is not None and self.max is None:
            return 'Must be %r or greater'%(self.min,)
        if self.min is None and self.max is not None:
            return 'Must be %r or less'%(self.max,)
        return 'Must be between %r and %r'%(self.min, self.max)
    
    def validate(self, field, value):
        if value is None:
            return
        if self.min is not None and value < self.min:
            raise FieldValidationError, self.validationErrorMessage(field)
        if self.max is not None and value > self.max:
            raise FieldValidationError, self.validationErrorMessage(field)

            
class PatternValidator(object):
    """Validate the value is a certain pattern.
    
    The required pattern is defined as a regular expression. The regex will be
    compiled automatically if necessary.
    """
    
    def __init__(self, regex):
        self.regex = regex
        
    def validate(self, field, value):
        if value is None:
            return
        # If it doesn't look like a regex object then compile it now
        if not hasattr(self.regex, 'match'):
            self.regex = re.compile(self.regex)
        if self.regex.match(value) is None:
            raise FieldValidationError, 'Invalid format'



class CallableValidator(object):
    """
    A validator that delegates the validation of non-None values to a callable
    with the same signature as IValidator.validate.
    """

    def __init__(self, callable):
        self.callable = callable


    def validate(self, field, value):
        if value is None:
            return
        return self.callable(field, value)
        
            
    
__all__ = [
    'FormError', 'FieldError', 'FieldValidationError', 'FieldRequiredError',
    'RequiredValidator', 'LengthValidator', 'RangeValidator', 'PatternValidator',
    'CallableValidator',
    ]

