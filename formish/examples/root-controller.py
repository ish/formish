import logging

from pylons import request, response, session
from pylons import tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from mg.lib.base import BaseController, render
from mg import forms

log = logging.getLogger(__name__)

import wingdbstub
from formencode import validators as v


schema = forms.Schema()
schema.add(forms.String(name="one", title="One", validator = v.Email(not_empty=True)))
schema.add(forms.String(name="two", title="Two", description="Wibble, wobble, plop!"))   

class RootController(BaseController):

    def index(self):
        """
        You should be able to add widgets using a dictionary as follows
        >>>widgets = {"two": forms.TextArea(cols='20')}
        >>>c.form = forms.Form(schema, widgets)
        """        
        form = forms.Form('name',schema)
        if request.method == 'GET':
            c.form = form
            c.form.data["one"] = "Whatever"
            c.form.two.widget = forms.TextArea(cols='20')
            return render("root.html")
        elif request.method == 'POST':
            print 'submitted'
            if form.validateRequest(request):
                # Do some databse stuff with form.data
                return '' #redirect()
            else:
                print 'failed but data is ', form.data
                c.form = form
                return render("root.html")
            