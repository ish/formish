

def extract(id):
    lines = open('testish/lib/forms.py').readlines()
    func_def = []
    in_function = False
    in_quotes = False
    prev_line = ''
    for line in lines:
        if 'def %s'%id in line:
            in_function = True

        if in_function and not in_quotes and '    """' in line:
            in_quotes = True
        elif in_function and in_quotes and '   """' in line:
            in_quotes = False
        if '    return' in line:
            in_function = False

        if in_function and not in_quotes and '   """' not in line and 'def %s'%id not in line:
            func_def.append( line[4:] )

        prev_line = line

    func_def = ''.join(func_def)
    try:
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter
        return highlight(func_def, PythonLexer(), HtmlFormatter())
    except ImportError:
        return func_def

