

def extract(id):
    lines = open('testish/lib/forms.py').readlines()
    func_def = []
    in_function = False
    in_quotes = False
    for line in lines:
        if 'def %s('%id in line:
            in_function = True

        if in_function and not in_quotes and '    """' in line:
            in_quotes = True
        elif in_function and in_quotes and '   """' in line:
            in_quotes = False
        if '    return' in line:
            in_function = False

        if in_function and not in_quotes and '   """' not in line and 'def %s('%id not in line:
            func_def.append( line[4:] )

    func_def = ''.join(func_def)
    try:
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter
        return highlight(func_def, PythonLexer(), HtmlFormatter())
    except ImportError:
        return func_def



def extract_docstring_highlighted(id):
    lines = open('testish/lib/forms.py').readlines()
    docstring = []
    in_function = False
    in_quotes = False
    for line in lines:
        if 'def %s('%id in line:
            in_function = True
        elif 'def ' in line:
            in_function = False

        if in_function and not in_quotes and '    """' in line:
            in_quotes = True
        elif in_function and in_quotes and '   """' in line:
            in_quotes = False

        if in_quotes and in_function and '   """' not in line and 'def %s('%id not in line:
            docstring.append( line )

    docstring = ''.join(docstring)
    try:
        from pygments import highlight
        from pygments.lexers import MakoHtmlLexer
        from pygments.formatters import HtmlFormatter
        return highlight(docstring, MakoHtmlLexer(), HtmlFormatter())
    except ImportError:
        return docstring

def extract_docstring(id):
    lines = open('testish/lib/forms.py').readlines()
    docstring = []
    in_function = False
    in_quotes = False
    for line in lines:
        if 'def %s('%id in line:
            in_function = True
        elif 'def ' in line:
            in_function = False

        if in_function and not in_quotes and '    """' in line:
            in_quotes = True
        elif in_function and in_quotes and '   """' in line:
            in_quotes = False

        if in_quotes and in_function and '   """' not in line and 'def %s('%id not in line:
            docstring.append( line )

    docstring = ''.join(docstring)
    return docstring
