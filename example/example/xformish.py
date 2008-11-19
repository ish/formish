"""
General purpose formish extensions.
"""

from formish import validation, widgets, Form

def make_form(request, *args, **kwargs):
    kwargs['renderer'] = request.environ['restish.templating.renderer']
    return Form(*args, **kwargs)

