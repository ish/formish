import logging
import formish, schemaish, validatish

from testish.lib import base

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

def test_SimpleString(self, sel):
    sel.open("/SimpleString")
    sel.type("form-myStringField", "test")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myStringField': u'test'}" in sel.get_text('id=data'))
    return

def SimpleInteger():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myIntegerField', schemaish.Integer())
    form = formish.Form(schema, 'form')
    return form

def test_SimpleInteger(self,sel):
    sel.open("/SimpleInteger")
    sel.type("form-myIntegerField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("Not a valid number" in sel.get_text('id=form'))
    sel.type("form-myIntegerField", "8")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myIntegerField': 8}" in sel.get_text('id=data'))
    return

def SimpleDate():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myDateField', schemaish.Date())
    form = formish.Form(schema, 'form')
    return form

def test_SimpleDate(self, sel):
    sel.open("/SimpleDate")
    sel.type("form-myDateField", "8")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("Invalid date" in sel.get_text('id=form'))
    sel.type("form-myDateField", "2008-12-8")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myDateField': datetime.date(2008, 12, 8)}" in sel.get_text('id=data'))
    return

def SimpleFloat():
    """
    A simple form with a single integer field
    """
    schema = schemaish.Structure()
    schema.add('myFloatField', schemaish.Float())
    form = formish.Form(schema, 'form')
    return form

def test_SimpleFloat(self, sel):
    sel.open("/SimpleFloat")
    sel.type("form-myFloatField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("Not a valid number" in sel.get_text('id=form'))
    sel.type("form-myFloatField", "1.5")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myFloatField': 1.5}" in sel.get_text('id=data'))
    return

def SimpleBoolean():
    """
    A simple form with a single boolean field
    """
    schema = schemaish.Structure()
    schema.add('myBooleanField', schemaish.Boolean())
    form = formish.Form(schema, 'form')
    return form

def test_SimpleBoolean(self, sel):
    sel.open("/SimpleBoolean")
    sel.type("form-myBooleanField", "a")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("either True or False" in sel.get_text('id=form'))
    sel.type("form-myBooleanField", "True")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myBooleanField': True}" in sel.get_text('id=data'))
    sel.type("form-myBooleanField", "False")
    sel.click("form-action-submit")
    sel.wait_for_page_to_load("3000")
    self.failUnless("{'myBooleanField': False}" in sel.get_text('id=data'))
    return


