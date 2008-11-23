from restish import http, resource, templating
from formish import *
from schemaish import *
from restish import http, resource, page, templating
from restish.url import URL
from schemaish import validators as v
from datetime import date
forms = {}
import tempfile, os

def make_form(request, *args, **kwargs):
    kwargs['renderer'] = request.environ['restish.templating.renderer']
    return Form(*args, **kwargs)


def getForms(request):
    ##
    # Simple Form
    
    schema = Structure()
    schema.add('email', String(validator=All(NotEmpty, Email)))
    schema.add('first_names', String(validator=NotEmpty))
    schema.add('last_name', String(validator=NotEmpty))
    schema.add('age', Integer(validator=NotEmpty))
    schema.add('description', String())
    
    form = make_form(request,schema)
    form['description'].widget = TextArea()
    
    forms['simple'] = ('Simple Form',"Some simple form fields", form)
    
    
    ##
    # Customisations
    
    schema = Structure()
    schema.add('email', String(validator=All(NotEmpty, Email)))
    schema.add('first_names', String(validator=NotEmpty))
    schema.add('last_name', String(validator=NotEmpty))
    schema.add('age', Integer(validator=NotEmpty))
    schema.add('description', String())
    
    form = make_form(request,schema)
    form['description'].widget = TextArea(cssClass='textytexty')
    form['age'].widget = Input(cssClass='mycssclass') 
    forms['customisation'] = ('Customising',"Changing the widgets, adding classes, etc.", form)
    
    ##
    # File Upload
    
    schema = Structure()
    schema.add('file', File())
    schema.add('string', String(validator=NotEmpty, description='Leave empty to check file upload round tripping'))
    
    
    form = make_form(request,schema)
    form['file'].widget = FileUpload(TempFileHandler(resource_root='/filehandler'),
               showImagePreview=True)
    
    forms['fileupload'] = ('File Upload',"Simple File Upload example", form)
        
    
    ##
    # Sequence
    
    schema = Structure()
    schema.add('list',Sequence(String()))
    schema.add('checkboxlist',Sequence(String()))
    
    
    form = make_form(request,schema)
    form.defaults = {'list': ['1','2','3']}
    
    form['checkboxlist'].widget = CheckboxMultiChoice([('opt1',"Options 1"),('opt2',"Option 2")])
    #sd
    
    forms['sequence'] = ('Sequence', "A Sequence of String Fields", form)

    ##
    # Sequence Text Area
    
    schema = Structure()
    schema.add('list',Sequence(String()))
    
    
    form = make_form(request,schema)
    form.defaults = {'list': ['1','2','3']}
    form['list'].widget = TextArea(converter_options={'delimiter':'\n'})
    forms['sequencetextarea'] = ('Sequence TextArea', "A Sequence of String Fields using TextArea widget", form)
    
    ##
    # Sequence of Structures
    
    schema = Structure()
    strings = Structure()
    strings.add('a',String(validator=NotEmpty))
    strings.add('b',String())
    schema.add('list',Sequence(strings))
    
    form = make_form(request,schema)
    form.defaults = {'list': [{'a':1,'b':2},{'a':3,'b':4}]}
    forms['sequencestructurestrings'] = ('Sequence of Structures', "A Sequence of Structures each containing two string fields", form)
    
    
    ##
    # Complex for from test_html
    
    one = Structure([("a", String(validator=v.Email(not_empty=True))), ("b", String()), ("c", Sequence(Integer(validator=v.NotEmpty())))])
    two = Structure([("a", String()), ("b", Date()), ('c', Sequence(String())), ("d", String()), ("e", Integer(validator=v.NotEmpty())), ("f", String(validator=v.NotEmpty())) ])
    schema = Structure([("one", one), ("two", two)])
    f = make_form(request,schema,name="form")

    f['one.b'].widget = TextArea()
    f['two.a'].widget = SelectChoice([('opt1',"Options 1"),('opt2',"Option 2")], noneOption=('-select option-',None))
    f['two.b'].widget = DateParts()
    f['two.c'].widget = CheckboxMultiChoice([('opt1',"Options 1"),('opt2',"Option 2")])
    f['two.d'].widget = RadioChoice([('opt1',"Options 1"),('opt2',"Option 2")])
    f['two.f'].widget = CheckedPassword()

    f.addAction(lambda x: x, 'submit', label="Submit Me")
    f.defaults = {'one': {'a' : 'ooteenee','c':['3','4','5']}, 'two': {'b': date(1966,1,3),'c':['opt2'],'d':'opt2'} }    
    forms['complexform'] = ('Complex Form','The complex form taken from the tests',f)
    
    ##
    # Sequence in Text Boxes
    
    schema = Structure()
    schema.add('a',Sequence(String()))
    
    
    f = make_form(request,schema, 'foo')
    f.defaults = {'a': ['one','two','three']}
    f['a.*'].widget = TextArea()
    forms['textareasequence'] = ('Sequence of Strings', "Sequence of Strings", f)

    ##
    # Sequence of sequences in Text Boxes
    schema = Structure()
    schema.add('a', Sequence(Sequence(Integer())))
    
    f= make_form(request,schema, 'foo')
    f.defaults = {'a': [[1, 2, 3], [4, 5, 6]]}
    f['a'].widget = TextArea()
    forms['textareasequencesequence'] = ('TextArea Sequence Sequence','A TextArea containing a sequence of sequences',f)

    ##
    # Sequence of tuples in Text Boxes
    schema = Structure()
    schema.add('a', Sequence(Tuple( (Integer(),String()) )))
    
    f= make_form(request,schema, 'foo')
    f.defaults = {'a': [(1,'a'),(2,'b')]}
    f['a'].widget = TextArea()
    forms['textareasequencetuple'] = ('TextArea Sequence Tuple','A TextArea containing a sequence of Tuples',f)

    ##
    # Tuple in an Input field
    schema = Structure()
    schema.add('a', Tuple( (Integer(),String()) ))
    
    f= make_form(request,schema, 'foo')
    f.defaults = {'a': (1,'a')}
    f['a'].widget = Input()
    forms['inputtuple'] = ('Input Tuple','A tuple in a basic input field',f)
        

    ##
    # Tuple in an Select Choice field
    schema = Structure()
    schema.add('a', Tuple( (Integer(),String()) ))
    
    f= make_form(request,schema, 'foo')
    f.defaults = {'a': (1,'a')}
    f['a'].widget = SelectChoice(options=[((1,'a'),'ONEA'),((2,'b'),'TWOB')])
    forms['selecttuple'] = ('Select Tuple','A tuple in a select choice',f)
        

    ##
    # Tuple in an Select Choice field
    schema = Structure()
    schema.add('a', Tuple( (Integer(),String()) ))
    schema.add('b', String(validator=NotEmpty))
    
    f= make_form(request,schema, 'foo')
    f.defaults = {'a': (1,'a')}
    f['a'].widget = SelectChoice(options=[((1,'a'),'ONEA'),((2,'b'),'TWOB')],noneOption=((0,'x'),'None'))
    forms['selecttuplenoneoption'] = ('Select Tuple','A tuple in a select choice with none option',f)
            
    
    ##
    # Sequence of Structs with Sequences

    subschema = Structure()
    subschema.add('email', String(validator=All(NotEmpty, Email)))
    subschema.add('first_names', String(validator=NotEmpty))
    subschema.add('last_name', String(validator=NotEmpty))
    subschema.add('description', Sequence(String()))
        
    
    schema = Structure()
    schema.add('a',Sequence(subschema))
    
    
    f = make_form(request,schema, 'foo')
    f.defaults = {'a': [{'email':'tim@jdi.net','first_names':'Tim','last_name':'Parkin','description':['a']},{}]}
    forms['sequenceofstructs'] = ('Sequence of Structs', "Sequence of Structs", f)
        

    ##
    # FormBuilder form
    field = Structure()
    field.add('name',String(validator=NotEmpty))
    field.add('type',String())
    field.add('display',String())
    field.add('required',Boolean())
    field.add('options', Sequence(String()))
    field.add('description',String())
    field.add('label',String())
    
    schema = Structure()
    schema.add('name',String(validator=NotEmpty))
    schema.add('fields',Sequence(field))
    
    f = make_form(request,schema, 'formbuilder')
    display_options = [
        ('text-input','Input'),
        ('text-area','Text Block'),
        ('checkbox','Tick Box'),
        ('date-parts','Y-M-D'),
        ('select-choice','Select'),
        ('radio-choice','Radio Buttons'),
        ('checkbox-multi-choice','Tick Boxes'),
        ('text-area-list','Text Box List'),
    ]
    field_type_options = [
        ('string','Text'),
        ('date','Date'),
        ('int','Integer'),
        ('float','Float'),
        ('bool','Yes/No'),
        ('list/string','Multiple Strings'),
        ('list/int','Multiple Integers'),
    ]
    f['fields.*.options'].widget = TextArea()
    f['fields.*.description'].widget = TextArea()
    f['fields.*.required'].widget = Checkbox()
    f['fields.*.type'].widget = SelectChoice(options=field_type_options)
    f['fields.*.display'].widget = SelectChoice(options=display_options)
    
    forms['formbuilder'] = ('FormBuilder', "A form to create forms", f)
       
    
    ##
    # Category Picker form    
    schema = Structure()
    schema.add('a',Sequence(String()))
    
    
    f = make_form(request,schema, 'foo')
    f.defaults = {'a': ['location','location.uk.dorset']}
    options = [
        ('location','Location'),
        ('location.uk','UK'),
        ('location.uk.dorset','Dorset'),
        ('location.uk.dorset','Cornwall'),
        ('location.foreign','Foreign'),
        ]
    f['a'].widget = CheckboxMultiChoiceTree(options)
    forms['checkboxmultichoice'] = ('CheckboxMultiChoiceTree', "Tree of checkboxes for a multichoice sequence", f)
    
    
    ###
    return forms
    
menu = [
    'simple',
    'customisation',
    'fileupload',
    'sequence',
    'sequencetextarea',
    'sequencestructurestrings',
    'complexform',
    'sequenceofstructs',
    'formbuilder',
    'textareasequence',
    'textareasequencesequence',
    'textareasequencetuple',
    'inputtuple',
    'selecttuple',
    'selecttuplenoneoption',
    'checkboxmultichoice'
    ]


class RootResource(resource.Resource):

    def __init__(self):
        self.forms = getForms
    
    @resource.GET()
    @templating.page('root.html')
    def root(self, request):
        return {'menu':menu,'forms':self.forms(request)}
    
    
    def resource_child(self, request, segments):
        # Formish builder example code..
        if segments[0] == 'filehandler':
            return FileResource(), segments[1:]
        elif segments[0] == 'formishbuilder':
            return FormishBuilderResource(), segments[1:]
        elif segments[0] == 'callable':
            return CallableFormResource(), segments[1:]
        forms = self.forms(request)
        return FormResource(forms[segments[0]]), segments[1:]
    
class CallableFormResource(resource.Resource):
   
    def f(self, request):
        schema = Structure()
        schema.add('email', String(validator=All(NotEmpty, Email)))
        schema.add('first_names', String(validator=NotEmpty))
        schema.add('last_name', String(validator=NotEmpty))
        schema.add('age', Integer(validator=NotEmpty))
        schema.add('description', String())
        
        form = make_form(request,schema, renderer=request.environ['restish.templating.renderer'])
        form['description'].widget = TextArea()
        return form
            
    
    @resource.GET()
    @templating.page('callable.html')
    def GET(self, request):
        return {'header':'yeah wahetvcer','description':'desc','form':self.f(request)}

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
        except FormError, e:
            return self.render_form(request, form)
        else:
            print 'Success! : ',data
        return http.see_other( URL(request.environ['PATH_INFO']) )

class FormishBuilderResource(resource.Resource):

    def __init__(self):
        forms = getForms(request)
        self.header = 'Formish Builder'
        self.description = 'Create your Own Form'
        self.form = forms['formbuilder'][2]
    
    @resource.GET()
    def GET(self, request):
        return self.render_form(request, self.form)

    @templating.page('formishbuilder.html')
    def render_form(self, request, form, data={}, fbf=None, fdata={}):
        return {'header': self.header, 'description': self.description, 'form': form, 'data': data,'fbf':fbf,'fdata':fdata}

    def getFormbuildForm(self, data):
        from formishbuilder import builder
        fd = builder.process_formishbuilder_form_definition(data)
        f = builder.build(fd, name="myform")
        return f
    
    @resource.POST()
    def POST(self, request):
        fdata = {}
        if request.POST['__formish_form__'] == 'myform':
            import simplejson
            data = simplejson.loads(request.POST['data'])
            f = self.getFormbuildForm(data)
            try:
                fdata = f.validate(request)
            except:
                pass
            else:
                f.defaults = {'data':simplejson.dumps(data)}

            form = self.form
            form.defaults = data
            data['fields'] = data['fields'][:-1]
            
            return self.render_form(request, form, data=data, fbf=f, fdata=fdata)
            
        form = self.form
        try:
            data = form.validate(request)
        except FormError, e:
            return self.render_form(request, form)
        else:
            data['fields'].append( {'name':'data','type':'string', 'display':'hidden', 'label':'', 'options':'', 'description':'', 'required':False} )
            f = self.getFormbuildForm(data)
            import simplejson
            f.defaults = {'data':simplejson.dumps(data.data)}
            data['fields'] = data['fields'][:-1]
            form.defaults = data
            return self.render_form(request, form, data=data.data, fbf=f)
            
