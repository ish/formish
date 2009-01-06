import logging, os.path
import formish, schemaish, validatish
from formish.filehandler import TempFileHandlerWeb

log = logging.getLogger(__name__)

##
# Make sure forms have the doc string with triple quotes 
# on a separate line as this file is parsed

def SimpleString():
    """
    A simple form with a single string field
    """
    schema = schemaish.Structure()
    schema.add('myStringField', schemaish.String())
    form = formish.Form(schema, 'form')
    return form

def functest_SimpleString(self, sel):
    sel.open("/SimpleString")

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

    return

def unittest_SimpleString(self):
    # Test no data
    f = SimpleString()
    self.assertIdHasValue(f, 'form-myStringField', '')
    # Test None data
    f = SimpleString()
    testdata = {'myStringField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = SimpleString()
    testdata = {'myStringField': '8'}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myStringField', '8')
    self.assertRoundTrip(f, testdata)


def SimpleInteger():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Integer())
    form = formish.Form(schema, 'form')
    return form

def functest_SimpleInteger(self,sel):
    sel.open("/SimpleInteger")

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

    return

def unittest_SimpleInteger(self):
    # Test no data
    f = SimpleInteger()
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    # Test None data
    f = SimpleInteger()
    testdata = {'myIntegerField': None}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '')
    self.assertRoundTrip(f, testdata)
    # Test sample data
    f = SimpleInteger()
    testdata = {'myIntegerField': 8}
    f.defaults = testdata
    self.assertIdHasValue(f, 'form-myIntegerField', '8')
    self.assertRoundTrip(f, testdata)

def SimpleDate():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myDateField', schemaish.Date())
    form = formish.Form(schema, 'form')
    return form

def functest_SimpleDate(self, sel):

    sel.open("/SimpleDate")

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

    return

def SimpleFloat():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myFloatField', schemaish.Float())
    form = formish.Form(schema, 'form')
    return form

def functest_SimpleFloat(self, sel):
    sel.open("/SimpleFloat")

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

    return



def SimpleBoolean():
    """
    A simple form with a single boolean field
    """
    schema = schemaish.Structure()
    schema.add('myBooleanField', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    return form

def functest_SimpleBoolean(self, sel):
    sel.open("/SimpleBoolean")

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

    return


def SimpleDecimal():
    """
    A simple form with a single decimal field
    """
    schema = schemaish.Structure()
    schema.add('myDecimalField', schemaish.Decimal())
    form = formish.Form(schema, 'form')
    return form


def functest_SimpleDecimal(self, sel):
    sel.open("/SimpleDecimal")

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

    return



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

def functest_RequiredStringAndCheckbox(self, sel):
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
    

    return


def SimpleFile():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myFileField', schemaish.File())
    form = formish.Form(schema, 'form')
    form['myFileField'].widget = formish.FileUpload(filehandler=TempFileHandlerWeb())
    return form

def functest_SimpleFile(self, sel):
    sel.open("/SimpleFile")

    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    try: self.failUnless(sel.is_text_present("{'myFileField': None}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    sel.type("form-myFileField", os.path.abspath("testdata/test.txt"))
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")
    

    try: self.failUnless(sel.is_text_present("{'myFileField': <schemaish.type.File object at"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return



def StringWidgets():
    """
    A demonstration of simple string type widgets

    * **Input** fields are the default and need not be specified but you might want to specify a 'strip' argument
    * **TextArea** take cols and rows keyword arguments (css usually overrides this). it can also take a 'strip' argument
    """
    schema = schemaish.Structure()
    schema.add('myInputStrip', schemaish.String())
    schema.add('myTextArea', schemaish.String())
    schema.add('myTextAreaCustom', schemaish.String())
    schema.add('myTextAreaStrip', schemaish.String())

    form = formish.Form(schema, 'form')
    form['myInputStrip'].widget = formish.Input(strip=True)
    form['myTextArea'].widget = formish.TextArea()
    form['myTextAreaCustom'].widget = formish.TextArea(cols=20,rows=4)
    form['myTextAreaStrip'].widget = formish.TextArea(strip=True)
    return form

def SelectWidgets():
    """
    A set of widget demonstrations using choices of various kinds
    """
    schema = schemaish.Structure()
    schema.add('mySelect', schemaish.String())
    options = [('a',1),('b',2),('c',3)]

    form = formish.Form(schema, 'form')
    form['mySelect'].widget = formish.SelectChoice(options)
    return form


def SequenceOfStructures():
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

def functest_SequenceOfUploadStructures(self, sel):

    sel.open("/SequenceOfUploadStructures")
    sel.wait_for_page_to_load("30000")
    sel.mouse_down("link=Add")

    sel.type("form-myList-0-a", os.path.abspath("testdata/test.txt"))
    sel.type("form-myList-0-b", "13")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("30000")

    try: self.failUnless(sel.is_text_present("{'myList': [{'a': <schemaish.type.File object at *, 'b': 13}]}"))
    except AssertionError, e: self.verificationErrors.append(str(e))

    return


    
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

def functest_SequenceOfStructuresWithSelects(self, sel):
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

    return

