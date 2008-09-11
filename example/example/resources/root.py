from restish import http, resource, templating
import formish
import schemaish
from restish import http, resource, page, templating
from restish.url import URL

forms = {}
#import wingdbstub


def getForms():
    ##
    # Simple Form
    
    schema = schemaish.Structure()
    schema.add('email', schemaish.String(validator=schemaish.All(schemaish.NotEmpty, schemaish.Email)))
    schema.add('first_names', schemaish.String(validator=schemaish.NotEmpty))
    schema.add('last_name', schemaish.String(validator=schemaish.NotEmpty))
    schema.add('description', schemaish.String())
    
    form = formish.Form(schema)
    form.description = formish.TextArea()
    
    forms['simple'] = ('Simple Form',"Some simple form fields", form)
    
    ##
    # Sequence
    
    schema = schemaish.Structure()
    schema.add('list',schemaish.Sequence(schemaish.String()))
    
    
    form = formish.Form(schema)
    form.defaults = {'list': ['1','2','3']}
    forms['sequence'] = ('Sequence', "A Sequence of String Fields", form)

    ##
    # Sequence Text Area
    
    schema = schemaish.Structure()
    schema.add('list',schemaish.Sequence(schemaish.String()))
    
    
    form = formish.Form(schema)
    form.defaults = {'list': ['1','2','3']}
    form['list'].widget = formish.TextArea()
    forms['sequence'] = ('Sequence', "A Sequence of String Fields", form)
    ##
    # Sequence Struct
    
    #schema = schemaish.Structure()
    #schema.add('a',schemaish.Sequence(schemaish.String()))
    
    
    #form = formish.Form(schema)
    #form['a'][0].widget = formish.TextArea()
    #forms['sequencestruct'] = ('Sequence of Structs', "Sequence of Strings", form)
    
    ###
    return forms
    
menu = [
    'simple',
    'sequence',
    #'sequencestruct',
    ]


class RootResource(resource.Resource):

    def __init__(self):
        self.forms = getForms
    
    @resource.GET()
    @templating.page('root.html')
    def root(self, request):
        return {'menu':menu,'forms':self.forms()}
    
    def resource_child(self, request, segments):
        forms = self.forms()
        return FormResource(forms[segments[0]]), segments[1:]


class FormResource(resource.Resource):

    def __init__(self, form):
        self.header = form[0]
        self.description = form[1]
        self.form = form[2]
    
    @resource.GET()
    def GET(self, request):
        return self.render_form(request, self.form)

    @templating.page('form.html')
    def render_form(self, request, form):
        return {'header': self.header, 'description': self.description, 'form': form}
    
    @resource.POST()
    def POST(self, request):
        form = self.form
        try:
            data = form.validate(request)
        except formish.FormError, e:
            return self.render_form(request, form)
        else:
            print 'Success! : ',data
        return http.see_other( URL.fromString(request.environ['PATH_INFO']) )


