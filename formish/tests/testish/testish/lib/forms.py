import logging, os.path, tempfile, subprocess
import formish, schemaish, validatish
from formish.dottedDict import dottedDict
from formish.filehandler import TempFileHandlerWeb
from testish.lib import xformish
import webob
from urllib import urlencode

log = logging.getLogger(__name__)



IDENTIFY = '/usr/bin/identify'

def build_request(formname, data):
    d = dottedDict(data)
    e = {'REQUEST_METHOD': 'POST'}
    request = webob.Request.blank('/',environ=e)
    fields = []
    fields.append( ('_charset)','UTF-8') )
    fields.append( ('__formish_form__','form') )
    for k, v in d.dotteditems():
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

def String():
    """
    A simple form with a single string field
    """
    schema = schemaish.Structure()
    schema.add('myStringField', schemaish.String())
    form = formish.Form(schema, 'form')
    return form

def functest_String(self, sel):#{{{
    sel.open("/String")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myStringField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myStringField", "Test")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myStringField': u'Test'}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myStringField", "80")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myStringField': u'80'}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def unittest_String(self):#{{{
    # Test no data
    f = String()
    self.assertIdHasValue(f, 'form-myStringField', '')
    # Test None data
    f = String()
    testdata = {'myStringField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = String()
    testdata = {'myStringField': '8'}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '8')
    self.assertRoundTrip(f, testdata)#}}}


def Integer():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Integer())
    form = formish.Form(schema, 'form')
    return form

def functest_Integer(self,sel):#{{{
    sel.open("/Integer")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myIntegerField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myIntegerField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Not a valid number"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myIntegerField", "8.0")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Not a valid number"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myIntegerField", "8")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myIntegerField': 8}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def unittest_Integer(self):#{{{
    # Test no data
    f = Integer()
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    # Test None data
    f = Integer()
    testdata = {'myIntegerField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = Integer()
    testdata = {'myIntegerField': 8}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '8')
    self.assertRoundTrip(f, testdata)#}}}

def Date():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myDateField', schemaish.Date())
    form = formish.Form(schema, 'form')
    return form

def functest_Date(self, sel):#{{{

    sel.open("/Date")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myDateField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDateField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Invalid date"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDateField", "18/12/1966")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Invalid date"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDateField", "2008-12-18")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myDateField': datetime.date(2008, 12, 18)}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def Float():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myFloatField', schemaish.Float())
    form = formish.Form(schema, 'form')
    return form

def functest_Float(self, sel):#{{{
    sel.open("/Float")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myFloatField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFloatField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Not a valid number"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFloatField", "11")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myFloatField': 11.0}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFloatField", "12.27")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myFloatField': 12.27}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}



def Boolean():
    """
    A simple form with a single boolean field
    """
    schema = schemaish.Structure()
    schema.add('myBooleanField', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    return form

def functest_Boolean(self, sel):#{{{
    sel.open("/Boolean")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myBooleanField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myBooleanField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("u'a' should be either True or False"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myBooleanField", "t")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("u't' should be either True or False"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myBooleanField", "True")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myBooleanField': True}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myBooleanField", "False")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myBooleanField': False}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}


def Decimal():
    """
    A simple form with a single decimal field
    """
    schema = schemaish.Structure()
    schema.add('myDecimalField', schemaish.Decimal())
    form = formish.Form(schema, 'form')
    return form


def functest_Decimal(self, sel):#{{{
    sel.open("/Decimal")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myDecimalField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDecimalField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Not a valid number"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDecimalField", "1")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myDecimalField': Decimal(\"1\")}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myDecimalField", "18.001")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myDecimalField': Decimal(\"18.001\")}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def RequiredStringAndCheckbox():
    """
    Testing that a checkbox is working properly when another required field is missing
    """
    schema = schemaish.Structure()
    schema.add('myString', schemaish.String(validator=validatish.Required()))
    schema.add('myBoolean', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    form['myBoolean'].widget=formish.Checkbox()
    return form

def functest_RequiredStringAndCheckbox(self, sel):#{{{
    sel.open("/RequiredStringAndCheckbox")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("is required"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myString", "anything")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myBoolean': False, 'myString': u'anything'}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myString", "anythingelse")
    sel.click("form-myBoolean")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myBoolean': True, 'myString': u'anythingelse'}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def File():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myFile', schemaish.File())
    form = formish.Form(schema, 'form')
    form['myFile'].widget = formish.FileUpload(filehandler=TempFileHandlerWeb())
    return form

def functest_File(self, sel):#{{{
    sel.open("/File")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myFile': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFile", os.path.abspath("testdata/test.txt"))
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    

    try: self.failUnless(sel.is_text_present("{'myFile': <schemaish.type.File"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

#########################
#
#   String Widgets
#

def Input():
    """
    Simple input field with a strip parameter
    """
    schema = schemaish.Structure()
    schema.add('inputStrip', schemaish.String())

    form = formish.Form(schema, 'form')
    form['inputStrip'].widget = formish.Input(strip=True)
    return form

def Hidden():
    """
    Hidden Field with a visible friend.. 
    """
    schema = schemaish.Structure()
    schema.add('Visible', schemaish.String())
    schema.add('Hidden', schemaish.String())

    form = formish.Form(schema, 'form')
    form['Hidden'].widget = formish.Hidden()
    return form

def Password():
    """
    Using a password html element
    """
    schema = schemaish.Structure()
    schema.add('Password', schemaish.String())

    form = formish.Form(schema, 'form')
    form['Password'].widget = formish.Password()
    return form

def CheckedPassword():
    """
    Simple input field with a strip parameter
    """
    schema = schemaish.Structure()
    schema.add('CheckedPassword', schemaish.String())

    form = formish.Form(schema, 'form')
    form['CheckedPassword'].widget = formish.CheckedPassword()
    return form

def TextAreaSimple():
    """
    Simple text area
    """
    schema = schemaish.Structure()
    schema.add('textArea', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textArea'].widget = formish.TextArea()
    return form

def TextAreaColsAndRows():
    """
    Passing cols and rows to a text area
    """
    schema = schemaish.Structure()
    schema.add('textAreaCustom', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textAreaCustom'].widget = formish.TextArea(cols=20,rows=4)
    return form

def TextAreaStrip():
    """
    Stripping text area input
    """
    schema = schemaish.Structure()
    schema.add('textAreaStrip', schemaish.String())

    form = formish.Form(schema, 'form')
    form['textAreaStrip'].widget = formish.TextArea(strip=True)
    return form

#######################
#
#   Validation

def Required():
    """
    Required Fields
    """
    schema = schemaish.Structure()
    schema.add('required', schemaish.String(validator=validatish.Required()))

    form = formish.Form(schema, 'form')
    return form

def MinLength():
    """
    Minimum Length fields - this one is min length four chars
    """
    schema = schemaish.Structure()
    schema.add('min', schemaish.String(validator=validatish.Length(min=4)))

    form = formish.Form(schema, 'form')
    return form

def MaxLength():
    """
    Maximum Length fields - this one is max length eight chars
    """
    schema = schemaish.Structure()
    schema.add('max', schemaish.String(validator=validatish.Length(max=8)))

    form = formish.Form(schema, 'form')
    return form

def MinMaxLength():
    """
    Minimum and maximum length
    """
    schema = schemaish.Structure()
    schema.add('minmax', schemaish.String(validator=validatish.Length(min=4,max=8)))

    form = formish.Form(schema, 'form')
    return form

def MinLengthCheckboxMultiChoice():
    """
    A checkbox multi choice with minimum length 3 (NOT WORKING)
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(
        schemaish.String(validation=validatish.Length(min=2))
        ))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoice(options)
    return form

def MinRange():
    """
    Minimum Value fields - this one is min value of 4
    """
    schema = schemaish.Structure()
    schema.add('min', schemaish.Float(validator=validatish.Range(min=4)))

    form = formish.Form(schema, 'form')
    return form

def MaxRange():
    """
    Maximum value for a field - this one is max of 8
    """
    schema = schemaish.Structure()
    schema.add('max', schemaish.Float(validator=validatish.Range(max=8)))

    form = formish.Form(schema, 'form')
    return form

def MinMaxRange():
    """
    Minimum and maximum value
    """
    schema = schemaish.Structure()
    schema.add('minmax', schemaish.Float(validator=validatish.Range(min=4,max=8)))

    form = formish.Form(schema, 'form')
    return form

def PlainText():
    """
    Plain Text (alphanum only)
    """
    schema = schemaish.Structure()
    schema.add('plainText', schemaish.String(validator=validatish.PlainText()))

    form = formish.Form(schema, 'form')
    return form

def OneOf():
    """
    One of a set of
    """
    schema = schemaish.Structure()
    items = ['one','two','three']
    schema.add('oneOf', schemaish.String(validator=validatish.OneOf(items)))

    form = formish.Form(schema, 'form')
    return form

def All():
    """
    Required and Plain Text (alphanum only plus _ and -)
    """
    schema = schemaish.Structure()
    schema.add('requiredPlainText', 
           schemaish.String(validator=validatish.All(
               validatish.Required(),validatish.PlainText(extra='-_')
           )))

    form = formish.Form(schema, 'form')
    return form


def ValidationOnSequenceItem():
    """
    A structure witin a sequence, should be enhanced with javascript
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String(validator=validatish.Required()) )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')
    return form

def RequiredStringAndFile():
    """
    A required string and a file field configured for image upload.
    """
    schema = schemaish.Structure()
    schema.add('required', schemaish.String(validator=validatish.Required()))
    schema.add('myFileField', schemaish.File())
    form = formish.Form(schema, 'form')
    form['myFileField'].widget = formish.FileUpload(filehandler=TempFileHandlerWeb(),show_image_preview=True,originalurl='/images/nouploadyet.png')
    return form

def functest_RequiredStringAndFile(self, sel):#{{{
    sel.open("/RequiredStringAndFile")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
        
    try: self.assertEqual("", sel.get_value("myFileField.default"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("", sel.get_value("myFileField.name"))
    except AssertionError, e: self.verificationErrors.append(str(e))


    sel.type("form-myFileField", os.path.abspath("testdata/photo.png"))
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
        
    try: self.assertEqual("", sel.get_value("myFileField.default"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("-photo.png", sel.get_value("myFileField.name")[-10:])
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
        
    try: self.assertEqual("", sel.get_value("myFileField.default"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("-photo.png", sel.get_value("myFileField.name")[-10:])
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFileField", os.path.abspath("testdata/photo.jpg"))
    sel.type("form-required", 'foo')
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")

    try: self.assertEqual(sel.get_attribute("//div[@id='actual']/img@src")[-9:],"photo.jpg")
    except AssertionError, e: self.verificationErrors.append(str(e))
    try: self.assertEqual(sel.get_attribute("//div[@id='resized']/img@src")[-22:-13],"photo.jpg")
    except AssertionError, e: self.verificationErrors.append(str(e))


    filesrc = sel.get_attribute("//div[@id='actual']/img@src")
    filesrc = filesrc.split('/')[-1]
    actualfilepath = 'cache/%s'%filesrc
    assert os.path.exists(actualfilepath)
    stdout = subprocess.Popen([IDENTIFY, actualfilepath], stdout=subprocess.PIPE).communicate()[0]
    assert stdout.endswith('photo.jpg JPEG 300x300 300x300+0+0 DirectClass 8-bit 4.36133kb \n')
    
    actualfilepath = '%s-100x100'%actualfilepath
    assert os.path.exists(actualfilepath)
    stdout = subprocess.Popen([IDENTIFY, actualfilepath], stdout=subprocess.PIPE).communicate()[0]
    assert stdout.endswith('photo.jpg-100x100 JPEG 100x100 100x100+0+0 DirectClass 8-bit 1.70703kb \n')

          
    return#}}}

########################
#
#   Checkbox

def Checkbox():
    """
    Simple Boolean Checkbox
    """
    schema = schemaish.Structure()
    schema.add('checkbox', schemaish.Boolean())

    form = formish.Form(schema, 'form')
    form['checkbox'].widget = formish.Checkbox()
    return form


#########################
#
#   Select Widgets
#

def SelectChoice():
    """
    A basic select choice
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options)
    return form

def unittest_SelectChoice(self):#{{{
    f = SelectChoice()
    testdata = {'mySelect': 3}
    f.defaults = testdata
    request = build_request('form',testdata)
    data = f.validate(request)
    assert data == testdata
    #}}}


def SelectChoiceNoneOption():
    """
    Setting a None Option on the select choice element
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options,none_option=(None, '--select--'))
    return form

def SelectChoiceCallableOptions():
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

def SelectWithOtherChoice():
    """
    A basic select choice
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectWithOtherChoice(options)
    return form

def functest_SelectWithOtherChoice(self, sel):#{{{
    sel.open("/SelectWithOtherChoice")

    try: self.assertEqual("", sel.get_value("form-mySelect"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.select("form-mySelect", "label=a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'mySelect': 1}"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.select("form-mySelect", "label=Other ...")
    sel.type("form-mySelect-other", "4")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'mySelect': 4}"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    sel.select("form-mySelect", "label=Other ...")
    sel.type("form-mySelect-other", "d")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("Not a valid number"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("...", sel.get_value("form-mySelect"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def unittest_SelectWithOtherChoice(self):#{{{
    # Test no data
    f = SelectWithOtherChoice()
    testdata = {'mySelect': 4}
    f.defaults = testdata
    reqdata = {'mySelect.other':'4','mySelect.select':'...'}
    request = build_request('form',reqdata)
    data = f.validate(request)
    assert data == testdata

    f = SelectWithOtherChoice()
    testdata = {'mySelect': 2}
    f.defaults = testdata
    reqdata = {'mySelect.other':'','mySelect.select':'2'}
    request = build_request('form',reqdata)
    data = f.validate(request)
    assert data == testdata
    return #}}}

def RadioChoice():
    """
    A basic select choice
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options)
    return form


def RadioChoiceNoneOption():
    """
    Setting a None Option on the select choice element
    """
    schema = schemaish.Structure()
    schema.add('myRadio', schemaish.Integer())
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['myRadio'].widget = formish.RadioChoice(options,none_option=(None, '--select--'))
    return form

def RadioChoiceCallableOptions():
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

#########################
#
#   Multi Select Widgets
#

def CheckboxMultiChoice():
    """
    A checkbox representing a set of values
    """
    schema = schemaish.Structure()
    schema.add('multiChoice', schemaish.Sequence(schemaish.String()))
    options = [(1,'a'),(2,'b'),(3,'c')]

    form = formish.Form(schema, 'form')
    form['multiChoice'].widget = formish.CheckboxMultiChoice(options)
    return form


def CheckboxMultiChoiceTree():
    """
    A checkbox representing a set of values
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

def SimpleStructure():
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
  
def UploadStructure():
    """
    A structure with a file upload
    """
    structure = schemaish.Structure()
    structure.add( 'a', schemaish.File() )
    structure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myStruct', structure)

    form = formish.Form(schema, 'form')

    form['myStruct.a'].widget = formish.FileUpload(filehandler=TempFileHandlerWeb())
    return form



#########################
#
#   Sequences
#


def SequenceOfSimpleStructures():
    """
    A structure witin a sequence, should be enhanced with javascript
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.String() )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')
    return form
  
def SequenceOfUploadStructures():
    """
    A structure witin a sequence, should be enhanced with javascript
    """
    substructure = schemaish.Structure()
    substructure.add( 'a', schemaish.File() )
    substructure.add( 'b', schemaish.Integer() )

    schema = schemaish.Structure()
    schema.add( 'myList', schemaish.Sequence( substructure ))

    form = formish.Form(schema, 'form')

    form['myList.*.a'].widget = formish.FileUpload(filehandler=TempFileHandlerWeb())
    return form

def functest_SequenceOfUploadStructures(self, sel):#{{{

    sel.open("/SequenceOfUploadStructures")
    sel.wait_for_page_to_load("30000")
    sel.mouse_down("link=Add")

    sel.type("form-myList-0-a", os.path.abspath("testdata/test.txt"))
    sel.type("form-myList-0-b", "13")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")

    try: self.failUnless(sel.is_text_present("{'myList': [{'a': <schemaish.type.File"))
    except AssertionError, e: self.verificationErrors.append(str(e))
    try: self.failUnless(sel.is_text_present("'b': 13}]}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def SequenceOfStructuresWithSelects():
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

def functest_SequenceOfStructuresWithSelects(self, sel):#{{{
    sel.open("/SequenceOfStructuresWithSelects")

    try: self.assertEqual("foo", sel.get_value("form-myList-0-a"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("b", sel.get_value("form-myList-0-b"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.click_at("css=#form-myList-field > a", "")
    try: self.assertEqual("", sel.get_value("form-myList-1-a"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    try: self.assertEqual("", sel.get_value("form-myList-1-b"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}

def SequenceOfDateParts():
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

def functest_SequenceOfDateParts(self, sel):#{{{
    sel.open("/SequenceOfDateParts")

    sel.click_at("css=#form-birthdays-field > a", "")
    try: self.assertEqual("", sel.get_value("form-birthdays-0-date"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return#}}}


def SequenceOfStructures():
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


def GranularFormLayout():
    """
    A simple demonstration of partial rendering of parts of forms.
    """

    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String(title='First Name', \
                     description='The name before your last one', \
                     validator=validatish.Required()) )

    form = formish.Form(schema, 'form')

    return form


def template_GranularFormLayout():
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

    
def CustomisedFormLayout():
    """
    A custom form
    """
    schema = schemaish.Structure()
    schema.add( 'firstName', schemaish.String())
    schema.add( 'surname', schemaish.String(description='THIS MUST BE YOUR SURNAME') )

    form = formish.Form(schema, 'form')

    form['surname'].widget = formish.Input(css_class="surnamewidget")

    return form


def template_CustomisedFormLayout():
    """
${form.header()|n}
${form.metadata()|n}

${form['firstName']()|n}

<div id="${form['surname'].cssname}-field" class="${form['surname'].classes}">
  <strong>${form['surname'].description}</strong>
  <em>${form['surname'].error}</em>
  ${form['surname'].widget()|n}
</div>

${form.actions()|n}
${form.footer()|n}

    """

# vim: fdm=marker:foldclose=all
