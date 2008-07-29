"""
General purpose utility module.
"""


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

