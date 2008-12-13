
About Formish
=============

Formish is a templating language agnostic form generation and handling library. 

How do I try it out
+++++++++++++++++++

Creating a schema
-----------------

First of all we need to create a data schema to define what types of data we want in the form. Lets take a look at the structure of a Form instance to begin with


>>> import schemaish
>>> schema = schemaish.Structure()
>>> schema.add( 'myfield', schemaish.String() )
>>> schema.attrs
[('myfield', <schemaish.attr.String object at 0x...>)]

So we now have a single field in our schema which is defined as a string. We can now create a form from this

>>> import formish
>>> form = formish.Form(schema)

And what can we do with the form? Well at the moment we have a form name and some fields

>>> form.name
'formish'

>>> for field in form.fields:
...     print field
... 
<formish.forms.Field object at 0x...>

And what about our field? Well it's now become a form field, which means it has a few extra attributes to do with creating things like classes, ids, etc.

>>> field = form.fields.next()
>>> field.name
'myfield'

Obviously the name is what we have it.

>>> field.widget
<bound widget name="myfield", widget="Input", type="String">


>>> field.title
'Myfield'

The title, if not specified in the schema field, is derived from the form name by converting camel case into capitalised words.

>>> field.cssname
'formish-myfield'

This is the start of the templating stuff.. The cssname is an identifier that can be inserted into forms, used for ids and class names.



Form Class
----------

.. autoclass:: formish.forms.Form
  :members: action, add_action, fields, validate,__call__

Field Class
-----------

.. autoclass:: formish.forms.Field
  :members: title, description, cssname, classes, value, required, error, widget,__call__
