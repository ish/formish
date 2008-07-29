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

