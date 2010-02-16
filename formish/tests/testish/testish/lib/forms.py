import logging, os.path, subprocess
import formish, schemaish, validatish
from dottedish.api import dotted, flatten
from formish.filestore import CachedTempFilestore
from testish.lib import xformish
import webob
from urllib import urlencode
import datetime

log = logging.getLogger(__name__)



IDENTIFY = '/usr/bin/identify'

def build_request(formname, data, rawdata=False):
    e = {'REQUEST_METHOD': 'POST'}
    request = webob.Request.blank('/',environ=e)
    fields = []
    fields.append( ('_charset)','UTF-8') )
    fields.append( ('__formish_form__','form') )
    if rawdata is True:
        for d in data:
            fields.append(d) 
    else:
        d = dotted(data)
        for k, v in flatten(d):
            fields.append( (k,v) )
    fields.append( ('submit','Submit') )
    request.body = urlencode( fields )
    
    return request

##
# Make sure forms have the doc string with triple quotes 
# on a separate line as this file is parsed


################
#
#  Simple Types

def form_String(request):
    """
    A simple form with a single string field
    """
    schema = schemaish.Structure()
    schema.add('myStringField', schemaish.String())
    form = formish.Form(schema, 'form')
    return form

def functest_String(self):
    sel = self.selenium
    sel.open("/String")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myStringField': None}"))

    sel.type("form-myStringField", "Test")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myStringField': u'Test'}"))

    sel.type("form-myStringField", "80")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myStringField': u'80'}"))

    return

def unittest_String(self, formdef):
    # Test no data
    f = formdef(None)
    self.assertIdHasValue(f, 'form-myStringField', '')
    # Test None data
    f = formdef(None)
    testdata = {'myStringField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = formdef(None)
    testdata = {'myStringField': '8'}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '8')
    self.assertRoundTrip(f, testdata)

def form_StringDifferentEmpty(request):
    """
    Simple field but setting the ``empty`` value equal an empty string (instead of None)
    """
    schema = schemaish.Structure()
    schema.add('myStringField', schemaish.String())
    form = formish.Form(schema, 'form')
    form['myStringField'].widget = formish.Input(empty='')
    return form

def unittest_StringDifferentEmpty(self, formdef):
    # Test None data
    f = formdef(None)
    testdata = {'myStringField': ''}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f =  formdef(None)
    testdata = {'myStringField': '8'}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '8')
    self.assertRoundTrip(f, testdata)

def form_Tuple(request):
    """
    A simple form with a single tuple field of string, integer form
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Tuple(attrs=[schemaish.String(), schemaish.Integer()]))
    form = formish.Form(schema, 'form')
    return form

def form_Integer(request):
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Integer())
    form = formish.Form(schema, 'form')
    return form

def functest_Integer(self):
    sel = self.selenium
    sel.open("/Integer")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myIntegerField': None}"))

    sel.type("form-myIntegerField", "a")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Not a valid integer"))

    sel.type("form-myIntegerField", "8.0")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Not a valid integer"))

    sel.type("form-myIntegerField", "8")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myIntegerField': 8}"))

    return

def unittest_Integer(self, formdef):
    # Test no data
    f =  formdef(None)
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    # Test None data
    f = formdef(None)
    testdata = {'myIntegerField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = formdef(None)
    testdata = {'myIntegerField': 8}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '8')
    self.assertRoundTrip(f, testdata)

def form_IntegerNoneDefault(request):
    """
    An integer field defaulting to None
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Integer())
    form = formish.Form(schema, 'form')
    form.defaults = {'myIntegerField':None}
    return form

def form_Date(request):
    """
    A simple form with a single date field
    """
    schema = schemaish.Structure()
    schema.add('myDateField', schemaish.Date())
    form = formish.Form(schema, 'form')
    return form

def functest_Date(self):
    sel = self.selenium

    sel.open("/Date")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myDateField': None}"))

    sel.type("form-myDateField", "a")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Invalid date"))

    sel.type("form-myDateField", "18/12/1966")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Invalid date"))

    sel.type("form-myDateField", "2008-12-18")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myDateField': datetime.date(2008, 12, 18)}"))

    return

def form_DateDifferentEmpty(request):
    """
    A simple date field but with the ``empty`` attribute value set to todays date
    """
    schema = schemaish.Structure()
    schema.add('myDateField', schemaish.Date())
    form = formish.Form(schema, 'form')
    form['myDateField'].widget = formish.Input(empty=datetime.date.today())
    return form

def unittest_DateDifferentEmpty(self, formdef):
    # Test None data
    f = formdef(None)
    testdata = {'myDateField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myDateField', '')
    expected = {'myDateField': datetime.date.today()}
    self.assertRoundTrip(f, expected)
    return 

def form_Float(request):
    """
    A simple form with a single float field
    """
    schema = schemaish.Structure()
    schema.add('myFloatField', schemaish.Float())
    form = formish.Form(schema, 'form')
    return form

def functest_Float(self):
    sel = self.selenium
    sel.open("/Float")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myFloatField': None}"))

    sel.type("form-myFloatField", "a")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Not a valid number"))

    sel.type("form-myFloatField", "11")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myFloatField': 11.0}"))

    sel.type("form-myFloatField", "12.27")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myFloatField': 12.27}"))

    return

def unittest_Float(self, formdef):
    # Test no data
    f =  formdef(None)
    self.assertIdHasValue(f, 'form-myFloatField', '')
    # Test None data
    f = formdef(None)
    testdata = {'myFloatField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myFloatField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = formdef(None)
    testdata = {'myFloatField': 8.4}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myFloatField', '8.4')
    self.assertRoundTrip(f, testdata)


def form_Boolean(request):
    """
    A simple form with a single boolean field, defaults to a RadioChoice widget. Add a required validator if you want a checkbox widget.
    """
    schema = schemaish.Structure()
    schema.add('myBooleanField', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    return form


def form_BooleanWithDefaults(request):
    """
    A simple form with a single boolean field
    """
    schema = schemaish.Structure()
    schema.add('myBooleanTrue', schemaish.Boolean())
    schema.add('myBooleanFalse', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    form.defaults = {'myBooleanTrue':True,'myBooleanFalse':False}
    return form


def form_Decimal(request):
    """
    A simple form with a single decimal field
    """
    schema = schemaish.Structure()
    schema.add('myDecimalField', schemaish.Decimal())
    form = formish.Form(schema, 'form')
    return form


def functest_Decimal(self):
    sel = self.selenium
    sel.open("/Decimal")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myDecimalField': None}"))

    sel.type("form-myDecimalField", "a")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Not a valid number"))

    sel.type("form-myDecimalField", "1")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myDecimalField': Decimal('1')}"))

    sel.type("form-myDecimalField", "18.001")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myDecimalField': Decimal('18.001')}"))

    return

def form_RequiredStringAndCheckbox(request):
    """
    Testing that a checkbox is working properly when another required field is missing (i.e. when the form round trips on error)
    """
    schema = schemaish.Structure()
    schema.add('myString', schemaish.String(validator=validatish.Required()))
    schema.add('myBoolean', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    form['myBoolean'].widget=formish.Checkbox()
    return form

def unittest_RequiredStringAndCheckbox(self, formdef):
    # Test no data
    f =  formdef(None)
    self.assertIdAttrHasValue(f, 'form-myBoolean','value','True')
    self.assertRaisesValidationError(f)
    testdata = {'myString':'7', 'myBoolean': False}
    f.defaults = testdata
    self.assertRoundTrip(f, testdata)

def functest_RequiredStringAndCheckbox(self):
    sel = self.selenium
    sel.open("/RequiredStringAndCheckbox")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("is required"))

    sel.type("form-myString", "anything")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myBoolean': False, 'myString': u'anything'}"))

    sel.type("form-myString", "anythingelse")
    sel.click("form-myBoolean")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myBoolean': True, 'myString': u'anythingelse'}"))

    return

def form_File(request):
    """
    A simple form with a single file field
    """
    schema = schemaish.Structure()
    schema.add('myFile', schemaish.File())
    form = formish.Form(schema, 'form')
    return form

def functest_File(self):
    sel = self.selenium
    sel.open("/File")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myFile': None}"))

    sel.type("form-myFile", os.path.abspath("testdata/test.txt"))
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    

    self.failUnless(sel.is_text_present("{'myFile': <schemaish.type.File"))

    return

#########################
#
#   String Widgets
#

def form_Input(request):
    """
    Simple input field with a strip parameter
    """
    schema = schemaish.Structure()
    schema.add('inputStrip', schemaish.String())

    form = formish.Form(schema, 'form')
    form['inputStrip'].widget = formish.Input(strip=True)
    return form

def form_InputNoneValue(request):
    """
    Simple input field with a strip parameter and a substitue none_value (allows user to return a None and an empty string). Notice use of schema default value.
    """
    schema = schemaish.Structure()
    schema.add('inputStrip', schemaish.String(default=''))

    form = formish.Form(schema, 'form')
    form['inputStrip'].widget = formish.Input(strip=True, none_value='BANG')
    return form

def form_InputDateNoneValue(request):
    """
    Simple input field with a strip parameter and a substitue none_value (allows user to return a None and an empty string). Notice use of schema default value.
    """
    schema = schemaish.Structure()
    schema.add('inputStrip', schemaish.Date(default=datetime.date(1900,1,1)))

    form = formish.Form(schema, 'form')
    form['inputStrip'].widget = formish.Input(empty=datetime.date(1900,1,1),roundtrip_empty=True)
    return form

def form_Hidden(request):
    """
    Hidden Field with a visible friend.. 
    """
    schema = schemaish.Structure()
    schema.add('Visible', schemaish.String())
    schema.add('Hidden', schemaish.String())

    form = formish.Form(schema, 'form')
    form['Hidden'].widget = formish.Hidden()
    return form

def form_Password(request):
    """
    Password html widget with string
    """
    schema = schemaish.Structure()
    schema.add('Password', schemaish.String())

    form = formish.Form(schema, 'form')
    form['Password'].widget = formish.Password()
    return form

def form_CheckedPassword(request):
    """
    Checked Password widget
    """
    schema = schemaish.Structure()
    schema.add('CheckedPassword', schemaish.String())

    form = formish.Form(schema, 'form')
    form['CheckedPassword'].widget = formish.CheckedPassword()
    return form

def form_TextAreaSimple(request):
    """
    Simple text area
    """
    schema = schemaish.Structure()
    schema.add('textArea', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textArea'].widget = formish.TextArea()
    return form

def form_TextAreaColsAndRows(request):
    """
    Passing cols and rows to a text area
    """
    schema = schemaish.Structure()
    schema.add('textAreaCustom', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textAreaCustom'].widget = formish.TextArea(cols=20,rows=4)
    return form

def form_TextAreaStrip(request):
    """
    Text area input with strip true
    """
    schema = schemaish.Structure()
    schema.add('textAreaStrip', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textAreaStrip'].widget = formish.TextArea(strip=True)
    return form


class SimpleSchema(schemaish.Structure):
    """ A simple sommets form """
    email = schemaish.String(validator=validatish.All(validatish.Required(), validatish.Email()))
    first_names = schemaish.String(validator=validatish.Required())
    last_name = schemaish.String(validator=validatish.Required())
    comments = schemaish.String()


def form_RestishExample(request):
    """
    The form used in the restish examples
    """
    form = formish.Form(SimpleSchema())
    form['comments'].widget = formish.TextArea()
    return form


#######################
#
#   Validation

def form_Required(request):
    """
    Required Fields
    """
    schema = schemaish.Structure()
    schema.add('required', schemaish.String(validator=validatish.Required()))

    form = formish.Form(schema, 'form')
    return form



def form_CheckboxRequired(request):
    """
    Simple Boolean Checkbox with a required validator. Add an empty value if you want to force the user to add a tick
    """
    schema = schemaish.Structure()
    schema.add('checkbox', schemaish.Boolean(validator=validatish.Required()))

    form = formish.Form(schema, 'form')
    return form

def form_CheckboxRequiredWithEmptyValue(request):
    """
    Simple Boolean Checkbox
    """
    schema = schemaish.Structure()
    schema.add('checkbox', schemaish.Boolean(validator=validatish.Required()))

    form = formish.Form(schema, 'form')
    form['checkbox'].widget = formish.Checkbox(empty=None)
    return form

def form_RadioChoiceRequired(request):
    """
    A basic radio choice
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer(validator=validatish.Required()))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options)
    return form


def form_MinLength(request):
    """
    Minimum Length fields - this one is min length four chars
    """
    schema = schemaish.Structure()
    schema.add('min', schemaish.String(validator=validatish.Length(min=4)))

    form = formish.Form(schema, 'form')
    return form

def form_MaxLength(request):
    """
    Maximum Length fields - this one is max length eight chars
    """
    schema = schemaish.Structure()
    schema.add('max', schemaish.String(validator=validatish.Length(max=8)))

    form = formish.Form(schema, 'form')
    return form

def form_MinMaxLength(request):
    """
    Minimum and maximum length
    """
    schema = schemaish.Structure()
    schema.add('minmax', schemaish.String(validator=validatish.Length(min=4,max=8)))

    form = formish.Form(schema, 'form')
    return form

def form_MinLengthCheckboxMultiChoice(request):
    """
    A checkbox multi choice with minimum length 3 
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(
        schemaish.String(validator=validatish.Length(min=2))
        ))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoice(options)
    return form

def form_MinRange(request):
    """
    Minimum Value fields - this one is min value of 4
    """
    schema = schemaish.Structure()
    schema.add('min', schemaish.Float(validator=validatish.Range(min=4)))

    form = formish.Form(schema, 'form')
    return form

def form_MaxRange(request):
    """
    Maximum value for a field - this one is max of 8
    """
    schema = schemaish.Structure()
    schema.add('max', schemaish.Float(validator=validatish.Range(max=8)))

    form = formish.Form(schema, 'form')
    return form

def form_MinMaxRange(request):
    """
    Minimum and maximum value
    """
    schema = schemaish.Structure()
    schema.add('minmax', schemaish.Float(validator=validatish.Range(min=4,max=8)))

    form = formish.Form(schema, 'form')
    return form

def form_PlainText(request):
    """
    Plain Text (alphanum only)
    """
    schema = schemaish.Structure()
    schema.add('plainText', schemaish.String(validator=validatish.PlainText()))

    form = formish.Form(schema, 'form')
    return form

def form_OneOf(request):
    """
    One of a set of
    """
    schema = schemaish.Structure()
    items = ['one','two','three']
    schema.add('oneOf', schemaish.String(validator=validatish.OneOf(items)))

    form = formish.Form(schema, 'form')
    return form

def form_All(request):
    """
    Required, Integer and Value >= 18
    """
    schema = schemaish.Structure()
    schema.add('minAge', 
           schemaish.Integer(validator=validatish.All(
               validatish.Required(), validatish.Integer(), validatish.Range(min=18) 
           )))

    form = formish.Form(schema, 'form')
    return form

def form_Any(request):
    """
    Any of the validators passing will mean a pass - implements 'no teenagers please'
    """
    schema = schemaish.Structure()
    schema.add('noTeenagers', 
           schemaish.Integer(validator=validatish.Any(
               validatish.Range(max=12), validatish.Range(min=20),
           )))

    form = formish.Form(schema, 'form')
    return form

def form_ReCAPTCHA(request):
    """
    ReCAPTCHA widget
    """
    schema = schemaish.Structure()
    schema.add('recaptcha', schemaish.Boolean())

    form = formish.Form(schema, 'form')
    publickey = '6LcSqgQAAAAAAA1A6MJZXGpY35ZsdvwxvsEq0KQD'
    privatekey = '6LcSqgQAAAAAAGn0bfmasP0pGhKgF7ugn72Hi2va'
    form['recaptcha'].widget = xformish.ReCAPTCHA(publickey, privatekey, request.environ)
    return form

def form_ValidationOnSequenceItem(request):
    """
    Validation on a sequence item.
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String(validator=validatish.Required()) )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')
    return form

def form_ValidationOnSequenceItemTextArea(request):
    """
    Validation on a sequence item.
    """
    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.String(validator=validatish.Email()) ))

    form = formish.Form(schema, 'form')
    form['myList'].widget = formish.TextArea()
    return form

def form_ValidationOnSequence(request):
    """
    Validation on a collection (sequence).
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String() )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure, validator=validatish.Length(min=2)))

    form = formish.Form(schema, 'form')
    return form


def form_RequiredStringAndFile(request):
    """
    A required string and a file field configured for image upload. (so that we can check roundtripping temp file)
    """
    schema = schemaish.Structure()
    schema.add('required', schemaish.String(validator=validatish.Required()))
    schema.add('myFileField', schemaish.File())
    form = formish.Form(schema, 'form')
    form['myFileField'].widget = formish.FileUpload(
        filestore=CachedTempFilestore(),
        show_image_thumbnail=True,
        image_thumbnail_default='/images/nouploadyet.png',
        show_download_link=True
    )
    return form

def functest_RequiredStringAndFile(self):
    from formish import safefilename
    from formish import filestore
    import shutil

    sel = self.selenium
    sel.open("/RequiredStringAndFile")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
        
    self.assertEqual("", sel.get_value("myFileField.default"))

    self.assertEqual("", sel.get_value("myFileField.name"))


    sel.type("form-myFileField", os.path.abspath("testdata/photo.png"))
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
        
    self.assertEqual("", sel.get_value("myFileField.default"))

    self.assertTrue(sel.get_value("myFileField.name"))

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
        
    self.assertEqual("", sel.get_value("myFileField.default"))

    self.assertTrue(sel.get_value("myFileField.name"))

    sel.type("form-myFileField", os.path.abspath("testdata/photo.jpg"))
    sel.type("form-required", 'foo')
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")

    self.assertEqual(sel.get_attribute("//div[@id='actual']/img@src")[-9:],"photo.jpg")
    self.assertEqual(sel.get_attribute("//div[@id='resized']/img@src")[-22:-13],"photo.jpg")


    filesrc = sel.get_attribute("//div[@id='actual']/img@src")

    filesrc = filesrc.split('/')[-1]

    fs = filestore.FileSystemHeaderedFilestore(root_dir='store')
    headers, fp = fs.get(filesrc)
    actualfilepath = safefilename.encode(filesrc)
    assert os.path.exists(os.path.abspath('store/%s'%actualfilepath))
    f = open('/tmp/testish-functest','wb')
    shutil.copyfileobj(fp, f)
    f.close()

    stdout = subprocess.Popen([IDENTIFY, '/tmp/testish-functest'], stdout=subprocess.PIPE).communicate()[0]
    assert '/tmp/testish-functest JPEG 300x300' in stdout
    
    actualfilepath = '_%s-100x100'%filesrc
    actualfilepath = safefilename.encode(actualfilepath)
    assert os.path.exists('cache/%s'%actualfilepath)
    fs = filestore.FileSystemHeaderedFilestore(root_dir='cache')
    headers, fp = fs.get('_%s-100x100'%filesrc)
    f = open('/tmp/testish-functest','wb')
    shutil.copyfileobj(fp, f)
    f.close()
    stdout = subprocess.Popen([IDENTIFY, '/tmp/testish-functest'], stdout=subprocess.PIPE).communicate()[0]
    assert '/tmp/testish-functest JPEG 100x100' in stdout

          
    return


########################
#
#   Checkbox

def form_Checkbox(request):
    """
    Simple Boolean Checkbox
    """
    schema = schemaish.Structure()
    schema.add('checkbox', schemaish.Boolean())

    form = formish.Form(schema, 'form')
    form['checkbox'].widget = formish.Checkbox()
    return form

def form_CheckboxWithDefaults(request):
    """
    Simple Boolean Checkbox
    """
    schema = schemaish.Structure()
    schema.add('checkboxTrue', schemaish.Boolean())
    schema.add('checkboxFalse', schemaish.Boolean())

    form = formish.Form(schema, 'form')
    form['checkboxTrue'].widget = formish.Checkbox()
    form['checkboxFalse'].widget = formish.Checkbox()
    form.defaults = {'checkboxTrue':True,'checkboxFalse':False}
    return form


#########################
#
#   Select Widgets
#

def form_SelectChoice(request):
    """
    A basic select choice
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options)
    return form

def unittest_SelectChoice(self, formdef):
    f = formdef(None)
    testdata = {'mySelect': 3}
    f.defaults = testdata
    request = build_request('form',testdata)
    data = f.validate(request)
    assert data == testdata
    


def form_SelectChoiceNoneOption(request):
    """
    Setting a None Option on the select choice element
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options,none_option=(None, '--select--'))
    return form

def form_SelectChoiceWithEmptyString(request):
    """
    A select choice which includes an empty string and a none value
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.String())
    options = [('','empty string'),('b','b'),('c','c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options, none_value='BANG')
    return form

def form_SelectChoiceCallableOptions(request):
    """
    Passing in a callable list of options
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    def _():
        options = [(1,'a'),(2,'b'),(3,'c')]
        for option in options:
            yield option

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(_)
    return form

def form_SelectWithOtherChoice(request):
    """
    A basic select choice with input option
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectWithOtherChoice(options)
    return form

def functest_SelectWithOtherChoice(self):
    sel = self.selenium
    sel.open("/SelectWithOtherChoice")

    self.assertEqual("", sel.get_value("form-mySelect"))
    sel.select("form-mySelect", "label=a")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'mySelect': 1}"))
    sel.select("form-mySelect", "label=Other ...")
    sel.type("form-mySelect-other", "4")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'mySelect': 4}"))
    sel.select("form-mySelect", "label=Other ...")
    sel.type("form-mySelect-other", "d")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Not a valid integer"))

    self.assertEqual("...", sel.get_value("form-mySelect"))

    return

def unittest_SelectWithOtherChoice(self, formdef):
    # Test no data
    f = formdef(None)
    testdata = {'mySelect': 4}
    f.defaults = testdata
    reqdata = {'mySelect.other':'4','mySelect.select':'...'}
    request = build_request('form',reqdata)
    data = f.validate(request)
    assert data == testdata

    f = formdef(None)
    testdata = {'mySelect': 2}
    f.defaults = testdata
    reqdata = {'mySelect.other':'','mySelect.select':'2'}
    request = build_request('form',reqdata)
    data = f.validate(request)
    assert data == testdata
    return 

def form_RadioChoice(request):
    """
    A basic radio choice
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options)
    return form


def form_RadioChoiceNoneOption(request):
    """
    Setting a None Option on the radio choice element
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options,none_option=(None, '--select--'))
    return form

def unittest_RadioChoiceNoneOption(self, formdef):
    # Test no data
    f = formdef(None)
    self.assertIdHasValue(f, 'form-myRadio-noneoption', '')
    # Test None data
    f = formdef(None)
    testdata = {'myRadio': None}
    f.defaults = testdata
    self.assertIdAttrHasNoValue(f, 'form-myRadio-noneoption','selected')
    self.assertIdAttrHasNoValue(f, 'form-myRadio-0','selected')
    self.assertIdAttrHasNoValue(f, 'form-myRadio-1','selected')
    self.assertIdAttrHasNoValue(f, 'form-myRadio-2','selected')
    self.assertRoundTrip(f, testdata)

def functest_RadioChoiceNoneOption(self):
    sel = self.selenium
    sel.open("/RadioChoiceNoneOption")

    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myRadio': None}"))
    sel.click("form-myRadio-noneoption")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myRadio': None}"))
    sel.click("form-myRadio-0")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("{'myRadio': 1}"))

    return

def form_RadioChoiceNoneOptionNoneDefault(request):
    """
    Setting a None Option on the radio choice element - default value of None
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form.defaults = {'myRadio':None}
    form['myRadio'].widget = formish.RadioChoice(options,none_option=(None, '--select--'))
    return form

def form_RadioChoiceNoneOptionWithDefault(request):
    """
    Setting a None Option on the radio choice element - default value of 1
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form.defaults = {'myRadio':1}
    form['myRadio'].widget = formish.RadioChoice(options,none_option=(None, '--select--'))
    return form

def form_RadioChoiceCallableOptions(request):
    """
    Passing in a callable list of options
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    def _():
        options = [(1,'a'),(2,'b'),(3,'c')]
        for option in options:
            yield option

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(_)
    return form

def form_RadioChoiceWithDefaults(request):
    """
    Simple Radio Choice boolean with defaults
    """
    schema = schemaish.Structure()
    schema.add('radiochoiceTrue', schemaish.Boolean())
    schema.add('radiochoiceFalse', schemaish.Boolean())

    form = formish.Form(schema, 'form')
    form['radiochoiceTrue'].widget =  formish.RadioChoice(((True,'yes'),(False,'no')), none_option=None)
    form['radiochoiceFalse'].widget =  formish.RadioChoice(((True,'yes'),(False,'no')), none_option=None)
    form.defaults = {'radiochoiceTrue':True,'radiochoiceFalse':False}
    return form

def form_SelectChoiceDate(request):
    """
    A select choice that uses dates for values
    """
    schema = schemaish.Structure()
    schema.add('myDateSelect', schemaish.Date())
    options = [(datetime.date(1970,1,1),'a'),(datetime.date(1980,1,1),'b'),(datetime.date(1990,1,1),'c')]

    form = formish.Form(schema, 'form')
    form['myDateSelect'].widget = formish.SelectChoice(options)
    return form

def unittest_SelectChoiceDate(self, formdef):
    f = formdef(None)
    testdata = {'myDateSelect': datetime.date(1980,1,1)}
    f.defaults = testdata
    request = build_request('form',testdata)
    data = f.validate(request)
    assert data == testdata

def form_SelectChoiceSequenceInteger(request):
    """
    A select choice that uses dates for values
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Sequence(schemaish.Integer()))
    options = [([1,2,3],'a'),([4,5,6],'b'),([7,8,9],'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options)
    return form

def unittest_SelectChoiceSequenceInteger(self, formdef):
    f = formdef(None)
    testdata = {'mySelect': [4,5,6]}
    rawdata = [('mySelect', '4,5,6'),]
    f.defaults = testdata
    request = build_request('form',rawdata, rawdata=True)
    data = f.validate(request)
    assert data == testdata

#########################
#
#   Defaults
#

def form_SelectChoiceDefault(request):
    """
    A select choice that uses dates for values
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options)
    form['mySelect'].default = 2
    return form

def form_RadioChoiceDefault(request):
    """
    A select choice that uses dates for values
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options)
    form['myRadio'].default = 2
    return form

def form_CheckboxMultiChoiceDefault(request):
    """
    A checkbox representing a set of values
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(schemaish.Integer()))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoice(options)
    form['multiChoice'].default = [2]
    return form

def form_SelectWithOtherChoiceDefault(request):
    """
    A basic select choice with input option
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectWithOtherChoice(options)
    form['mySelect'].default = 2
    return form

def form_SequenceOfStringsWithDefault(request):
    """
    A sequence with some defaults
    """
    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.String() ))

    form = formish.Form(schema, 'form')
    form.defaults = {'myList': ['a','b']}
    return form

#########################
#
#   Multi Select Widgets
#

def form_CheckboxMultiChoice(request):
    """
    A checkbox representing a set of values
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(schemaish.String()))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoice(options)
    return form


def form_CheckboxMultiChoiceTree(request):
    """
    A checkbox representing a set of values displayed as tree (using dots for depth)
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(schemaish.String()))
    options = [('a','Top Level A'),
               ('a.x','Second Level X'),
               ('a.y','Second Level Y'),
               ('b','First Level B')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoiceTree(options)
    return form

#########################
#
#   Structures
#

def form_SimpleStructure(request):
    """
    A simple structure
    """
    structure = schemaish.Structure()
    structure.add( 'a', schemaish.String() )
    structure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myStruct', structure )

    form = formish.Form(schema, 'form')
    return form
  
def form_StructureWithReadonly(request):
    """
    A simple structure
    """
    structure = schemaish.Structure()
    structure.add( 'a', schemaish.String() )
    structure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myStruct', structure )

    form = formish.Form(schema, 'form')
    form['myStruct.b'].widget = formish.Input(readonly=True)
    form['myStruct.b'].default = 7
    return form

def form_UploadStructure(request):
    """
    A structure with a file upload
    """
    structure = schemaish.Structure()
    structure.add( 'a', schemaish.File() )
    structure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myStruct', structure)

    form = formish.Form(schema, 'form')

    form['myStruct.a'].widget = formish.FileUpload(filestore=CachedTempFilestore())
    return form

def form_NestedStructures(request):
    """
    Allow the emission of parts of a form schema using field names.
    """
    schema = schemaish.Structure()
    schema.add( 'a', schemaish.String())
    schema.add( 'b', schemaish.String())

    sub_schema = schemaish.Structure()
    sub_schema.add('x',schemaish.String())

    schema.add('c', sub_schema)


    form = formish.Form(schema, 'form')

    return form


#########################
#
#   Sequences
#

def form_SequenceOfStrings(request):
    """
    A sequence with some defaults
    """
    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.String() ))

    form = formish.Form(schema,'formname')
    return form

def functest_SequenceOfStrings(self):
    sel = self.selenium
    sel.open("/SequenceOfStrings")
    sel.click_at("css=#formname-myList--field > a", "")
    self.assertEqual("", sel.get_value("formname-myList-0"))
    self.assertEqual("", sel.get_value("formname-myList-1"))
    sel.click_at("css=#formname-myList--field > a", "")
    self.assertEqual("", sel.get_value("formname-myList-2"))
    sel.click_at("css=#formname-myList-0--field .remove", "")
    self.assertEqual("", sel.get_value("formname-myList-0"))
    self.assertEqual("", sel.get_value("formname-myList-1"))
    self.assertEqual(False, sel.is_element_present("css=#formname-myList-2"))
    
def form_SequenceOfStringsWithoutFormName(request):
    """
    A sequence with some defaults
    """
    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.String() ))

    form = formish.Form(schema)
    return form

def functest_SequenceOfStringsWithoutFormName(self):
    sel = self.selenium
    sel.open("/SequenceOfStringsWithoutFormName")
    sel.click_at("css=#myList--field > a", "")
    self.assertEqual("", sel.get_value("myList-0"))
    self.assertEqual("", sel.get_value("myList-1"))
    sel.click_at("css=#myList--field > a", "")
    self.assertEqual("", sel.get_value("myList-2"))
    sel.click_at("css=#myList-0--field .remove", "")
    self.assertEqual("", sel.get_value("myList-0"))
    self.assertEqual("", sel.get_value("myList-1"))
    self.assertEqual(False, sel.is_element_present("css=#myList-2"))

def form_SequenceOfSimpleStructures(request):
    """
    A structure witin a sequence, should be enhanced with javascript
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String() )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')
    form['myList'].widget = formish.SequenceDefault()
    return form

def functest_SequenceOfSimpleStructures(self):
    sel = self.selenium
    sel.open("/SequenceOfSimpleStructures")
    sel.type("form-myList-0-a", "form-myList-0-a")
    self.assertEqual("form-myList-0-a", sel.get_value("form-myList-0-a"))
    self.assertEqual("", sel.get_value("form-myList-0-b"))

    sel.click_at("css=#form-myList--field > a", "")

    sel.type("form-myList-1-a", "form-myList-1-a")
    self.assertEqual("form-myList-1-a", sel.get_value("form-myList-1-a"))
    self.assertEqual("", sel.get_value("form-myList-1-b"))

    sel.click_at("css=#form-myList--field > a", "")
    
    sel.type("form-myList-2-a", "form-myList-2-a")
    self.assertEqual("form-myList-2-a", sel.get_value("form-myList-2-a"))
    self.assertEqual("", sel.get_value("form-myList-2-b"))

    sel.mouse_down_at("css=#form-myList-1--field .remove", "")
    sel.mouse_up('body')

    self.assertEqual("form-myList-0-a", sel.get_value("form-myList-0-a"))
    self.assertEqual("form-myList-2-a", sel.get_value("form-myList-1-a"))
    self.assertEqual("", sel.get_value("form-myList-1-b"))
    self.assertEqual(False, sel.is_element_present("css=#form-myList-2"))



def form_SequenceOfSequences(request):
    """
    A structure witin a sequence, should be enhanced with javascript
    """

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.Sequence( schemaish.String() ) ))

    form = formish.Form(schema, 'form')
    return form

def functest_SequenceOfSequences(self):

    sel = self.selenium
    sel.open("/SequenceOfSequences")
    sel.type("form-myList-0-0", "form-myList-0-0")
    self.assertEqual("form-myList-0-0", sel.get_value("form-myList-0-0"))

    sel.click_at("css=#form-myList-0--field > a", "")

    sel.type("form-myList-0-1", "form-myList-0-1")
    self.assertEqual("form-myList-0-0", sel.get_value("form-myList-0-0"))
    self.assertEqual("form-myList-0-1", sel.get_value("form-myList-0-1"))

    sel.click_at("css=#form-myList--field > a", "")
    sel.click_at("css=#form-myList-1--field > a", "")
    
    sel.type("form-myList-1-0", "form-myList-1-0")
    self.assertEqual("form-myList-0-0", sel.get_value("form-myList-0-0"))
    self.assertEqual("form-myList-0-1", sel.get_value("form-myList-0-1"))
    self.assertEqual("form-myList-1-0", sel.get_value("form-myList-1-0"))

    sel.click_at("css=#form-myList-0--field > a", "")

    sel.type("form-myList-0-2", "form-myList-0-2")
    self.assertEqual("form-myList-0-0", sel.get_value("form-myList-0-0"))
    self.assertEqual("form-myList-0-1", sel.get_value("form-myList-0-1"))
    self.assertEqual("form-myList-0-2", sel.get_value("form-myList-0-2"))
    self.assertEqual("form-myList-1-0", sel.get_value("form-myList-1-0"))

    sel.mouse_down_at("css=#form-myList-0-1--field .remove", "")
    self.assertEqual("form-myList-0-0", sel.get_value("form-myList-0-0"))
    self.assertEqual("form-myList-0-2", sel.get_value("form-myList-0-1"))
    self.assertEqual(False, sel.is_element_present("css=#form-myList-0-2"))
    self.assertEqual("form-myList-1-0", sel.get_value("form-myList-1-0"))


def form_SequenceOfStringsWithSequenceWidgetOptions(request):
    """
    A sequence with some defaults
    """
    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( schemaish.String() ))

    form = formish.Form(schema, 'form')
    form['myList'].widget = formish.SequenceDefault(min_start_fields=1,min_empty_start_fields=0, batch_add_count=5)
    return form

  
def form_SequenceOfUploadStructures(request):
    """
    A structure witin a sequence, should be enhanced with javascript
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.File() )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')

    form['myList.*.a'].widget = formish.FileUpload(filestore=CachedTempFilestore())
    return form

def functest_SequenceOfUploadStructures(self):
    sel = self.selenium

    sel.open("/SequenceOfUploadStructures")
    sel.wait_for_page_to_load("30000")

    sel.type("form-myList-0-a", os.path.abspath("testdata/test.txt"))
    sel.type("form-myList-0-b", "13")
    sel.click("form-action")
    sel.wait_for_page_to_load("30000")

    self.failUnless(sel.is_text_present("{'myList': [{'a': <schemaish.type.File"))
    self.failUnless(sel.is_text_present("'b': 13}]}"))

    return

def form_SequenceOfStructuresWithSelects(request):
    """
    A sequence including selects
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String() )
    substructure.add( 'b', schemaish.String() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')

    options = [('a',1),('b',2),('c',3)]
    form['myList.*.b'].widget = formish.SelectChoice(options)

    form.defaults = {'myList': [{'a':'foo','b':'b'}]}
    return form

def functest_SequenceOfStructuresWithSelects(self):
    sel = self.selenium
    sel.open("/SequenceOfStructuresWithSelects")

    self.assertEqual("foo", sel.get_value("form-myList-0-a"))

    self.assertEqual("b", sel.get_value("form-myList-0-b"))

    sel.click_at("css=#form-myList--field > a", "")
    self.assertEqual("", sel.get_value("form-myList-1-a"))

    self.assertEqual("", sel.get_value("form-myList-1-b"))

    return

def form_SequenceOfDateParts(request):
    """
    A test of a sequence of more complicated structures
    """
    schema = schemaish.Structure()
    schema.add('birthdays',
    schemaish.Sequence(
        schemaish.Structure(
           [ ('date', schemaish.Date(validator=validatish.Required())), ]
           ))) 
    form = formish.Form(schema, 'form')
    form['birthdays.*.date'].widget = formish.DateParts()
    return form



def functest_SequenceOfDateParts(self):
    sel = self.selenium
    sel.open("/SequenceOfDateParts")

    sel.click_at("css=#form-birthdays--field > a", "")
    self.assertEqual("", sel.get_value("form-birthdays-0-date"))

    return

def form_SequenceOfSequencesAsTextArea(request):
    """
    A simple text area but representing a csv style data structure
    """
    schema = schemaish.Structure()
    schema.add('table', schemaish.Sequence(schemaish.Tuple( (schemaish.String(), schemaish.Integer(), schemaish.Date()) )))
    form = formish.Form(schema)
    form['table'].widget = formish.TextArea()
    return form
    
def form_SequenceAsInputWithDefaultAndDelimiter(request):
    """
    A simple text area but representing a csv style data structure
    """
    schema = schemaish.Structure()
    schema.add('a', schemaish.Tuple( (schemaish.String(), schemaish.Integer()) ))
    form = formish.Form(schema)
    form['a'].widget = formish.Input(converter_options={'delimiter':':'})
    form.defaults = {'a': ('a',3)}
    return form

def form_SequenceOfStructures(request):
    """
    A test of a sequence of more complicated structures
    """
    schema = schemaish.Structure()
    schema.add('employment', schemaish.Sequence(schemaish.Structure([
        ('job_title', schemaish.String(validator=validatish.Required())),
        ('joined', schemaish.String(validator=validatish.Required())),
        ('left', schemaish.String(validator=validatish.Required())),
        ('time_spent', schemaish.String(validator=validatish.Required())),
        ('num_employees', schemaish.String(validator=validatish.Required())),
        ('comments', schemaish.String(validator=validatish.Required())),
        ('primary', schemaish.Boolean())])))

    form = formish.Form(schema, 'form')
    form['employment.*.primary'].widget=formish.Checkbox()
    form['employment.*.joined'].widget = xformish.ApproximateDateParts()
    form['employment.*.left'].widget = xformish.ApproximateDateParts()
    return form


def form_SequenceOfStructuresGridWidget(request):
    """ 
    Using a table structure to edit a sequence of dicts
    """
    schema = schemaish.Structure()
    schema.add('rows', schemaish.Sequence(schemaish.Structure([
        ('a', schemaish.Boolean()),
        ('b', schemaish.String()),])))

    form = formish.Form(schema, 'form')
    form['rows'].widget = formish.Grid()
    form['rows.*.a'].widget = formish.Checkbox()
    form.defaults = {'rows': [{'a':True,'b':'2'},{'a':False,'b':'4'},{'a':False,'b':'6'}]}
    return form


def form_GranularFormLayout(request):
    """
    A simple demonstration of partial rendering of parts of forms.
    """

    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String(title='First Name', \
                     description='The name before your last one', \
                     validator=validatish.Required()) )

    form = formish.Form(schema, 'form')

    return form


def template_GranularFormLayout(request):
    """

${form()|n}

<h2>Form</h2>

<h3>Normal Form</h3>
<pre>
${form()}
</pre>

<h4>Form Header, metadata, actions and Footer</h4>
<pre>

${form.header()}
<hr />
${form.metadata()}
<hr />
${form.actions()}
<hr />
${form.footer()}
</pre>

<h4>First Name</h4>
<pre>
${form['firstName']()}
</pre>

<h3>First Name (.title)</h4>
<pre>
${form['firstName'].title}
</pre>

<h3>First Name (.label())</h4>
<pre>
${form['firstName'].label()}
</pre>

<h3>First Name (.inputs())</h4>
<pre>
${form['firstName'].inputs()}
</pre>

<h3>First Name (.widget())</h4>
<pre>
${form['firstName'].widget()}
</pre>

<h3>First Name (.error())</h4>
<pre>
${form['firstName'].error()}
</pre>

<h3>First Name (.error)</h4>
<pre>
${form['firstName'].error}
</pre>

<h3>First Name (.cssname)</h4>
<pre>
${form['firstName'].cssname}
</pre>

<h3>First Name (.classes)</h4>
<pre>
${form['firstName'].classes}
</pre>

<h3>First Name (.value)</h4>
<pre>
${form['firstName'].value}
</pre>

<h3>First Name (.required)</h4>
<pre>
${form['firstName'].required}
</pre>



<h3>First Name (.description)</h4>
<pre>
${form['firstName'].description}
</pre>

<h3>First Name (.description())</h4>
<pre>
${form['firstName'].description()}
</pre>
    """

    
def form_CustomisedFormLayout(request):
    """
    A custom form
    """
    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String())
    schema.add( 'surname', schemaish.String(description='THIS MUST BE YOUR SURNAME') )

    form = formish.Form(schema, 'form')

    form['surname'].widget = formish.Input(css_class="surnamewidget")

    return form


def template_CustomisedFormLayout(request):
    """
${form.header()|n}
${form.metadata()|n}

${form['firstName']()|n}

<div id="${form['surname'].cssname}--field" class="${form['surname'].classes}">
  <strong>${form['surname'].description}</strong>
  <em>${form['surname'].error}</em>
  ${form['surname'].widget()|n}
</div>

${form.actions()|n}
${form.footer()|n}

    """

def form_CustomisedFormLayoutWithSequence(request):
    """
    A custom form
    """
    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String())
    schema.add( 'surname', schemaish.String(description='THIS MUST BE YOUR SURNAME') )
    email = schemaish.Structure()
    email.add('type',schemaish.String())
    email.add('email',schemaish.String())
    schema.add( 'emails', schemaish.Sequence(email))

    form = formish.Form(schema, 'form')

    form['surname'].widget = formish.Input(css_class="surnamewidget")
    
    form.defaults = {'firstName': 'Tim', 'surname': 'Parkin','emails': [{'type':'home','email':'a@b.com'},{'type':'work','email':'c@d.com'}]}

    return form


def template_CustomisedFormLayoutWithSequence(request):
    """
${form.header()|n}
${form.metadata()|n}

${form['firstName']()|n}

<div id="${form['surname'].cssname}--field" class="${form['surname'].classes}">
  <strong>${form['surname'].description}</strong>
  <em>${form['surname'].error}</em>
  ${form['surname'].widget()|n}
  <br />
  <table>
  %for field in form['emails'].fields:
  <tr>
    <td>${field['email'].title|n}</td>
    <td> ${field['email'].widget()|n}</td>
    <td>${field['type'].title|n}</td>
    <td>${field['type'].widget()|n}</td>
  </tr>
  %endfor
  </table>
</div>

${form.actions()|n}
${form.footer()|n}

    """

def form_CustomisedFormLayoutFields(request):
    """
    Allow the emission of parts of a form schema using field names.
    """
    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String())
    schema.add( 'surname', schemaish.String())
    schema.add( 'age', schemaish.Integer())
    schema.add( 'sex', schemaish.String())

    form = formish.Form(schema, 'form')

    return form


def template_CustomisedFormLayoutFields(request):
    """
${form.header()|n}
${form.metadata()|n}

${form.fields(form.fields.keys()[:1])|n}
<div id="special">
${form.fields(['surname'])|n}
</div>
${form.fields(form.fields.keys()[2:])|n}

${form.actions()|n}
${form.footer()|n}

    """
