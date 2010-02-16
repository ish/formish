*********************
A Formish Walkthrough
*********************

Formish is a templating language agnostic form generation and handling library. 

Have a look at `http://ish.io:8891 <http://ish.io:8891>`_ for an example - if this isn't running, please email `support@ish.io <mailto://support@ish.io>`_

Introduction - A Simple Form
============================

Creating a schema
-----------------

First of all we need to create a data schema to define what types of data we want in the form. Schema's use the 'Schemaish' package which lets you define structures against which you can validate/convert data. Lets take a look at the structure of a Form instance to begin with

.. doctest::

    >>> import schemaish
    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfield', schemaish.String() )
    >>> schema.attrs
    [('myfield', schemaish.String())]

Creating a form
---------------

So we now have a single field in our schema which is defined as a string. We can now create a form from this

.. doctest::

    >>> import formish
    >>> form = formish.Form(schema)

Attributes of a form
^^^^^^^^^^^^^^^^^^^^

And what can we do with the form? Well at the moment we have a form name and some fields


.. doctest:: 

    >>> form.name
    

.. doctest::

    >>> for field in form.fields:
    ...     print field
    ... 
    formish.Field(name='myfield', attr=schemaish.String())

Attributes of a field
^^^^^^^^^^^^^^^^^^^^^

And what about our field? Well it's now become a form field, which means it has a few extra attributes to do with creating things like classes, ids, etc.

.. doctest:: 

    >>> field = form.fields.next()
    >>> field.name
    'myfield'

The name is as we defined it in the schema.

.. doctest::

    >>> field.widget
    BoundWidget(widget=formish.Input(), field=formish.Field(name='myfield', attr=schemaish.String()))

.. doctest::

    >>> field.title
    'Myfield'

The title, if not specified in the schema field, is derived from the form name by converting camel case into capitalised words.

.. doctest:: 

    >>> field.cssname
    'myfield'

This is the start of the templating stuff.. The cssname is an identifier that can be inserted into forms, used for ids and class names.

How to create HTML
------------------

We create our HTML by calling the form as follows..

.. doctest:: 

    >>> form()
    u'...<form action="" class="formish-form" method="post" accept-charset="utf-8">...'

I've skipped the majority of this output as it's probably better shown formatted

.. code-block:: html

    <form id="form" action="" class="formish-form" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <div>
        <input type="hidden" name="_charset_" />
        <input type="hidden" name="__formish_form__" value="form" />
        <div id="form-myfield--field" class="field type-string widget-input">
          <label for="form-myfield">Myfield</label>
          <div class="inputs">
            <input id="form-myfield" type="text" name="myfield" value="" />
          </div>
        </div>
        <div class="actions">
          <input type="submit" id="form-action-submit" name="submit" value="Submit" />
        </div>
      </div>
    </form>

If you want to see the HTML styled with a default CSS stylesheet, take a look at http://test.ish.io or look within the tests directory for a sample restish based website that includes a css file. 

What's in the HTML
------------------

Firstly we have the form setup itself. The form name/id can be set by passing it into the Form as follows.

.. doctest:: 

    >>> named_form = formish.Form(schema, name='myformname')
    >>> named_form
    formish.Form(schemaish.Structure("myfield": schemaish.String()), name='myformname', defaults={'myfield': None})

Otherwise the form defaults to 'formish'. 

The method at the moment is always 'post' but a future release will implement get forms also. The final two attributes, enctype and accept-charset make the form behave in as consistent a way as possible. Defaulting to content type of 'utf-8' and handling the form data accoring to http://www.ietf.org/rfc/rfc2388.txt 'multipart/form-data'. 

The form html element
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: html

    <!-- The Form -->
    <form id="form" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">

The first hidden field is '_charset_ which is a hack to help mozilla handle charsets as described here https://bugzilla.mozilla.org/show_bug.cgi?id=18643. The second is the name of the form, used after submission to work out which form has been returned.

The form configuration attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. code-block:: html

      <!-- Form Configuration Attributes -->
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="form" />


The field itself has an id, using the form name, field name and the suffix '-field' to help with javascript, css, etc. There are also a bunch of classes that allow global css to be applied to different widget types or schema types.

The label points at the field, which in this case is the only input field. In the case of a date parts widget (three input boxes), the label's for attribute would point at the first field.

The 'input's div is a container that holds the widget itself, in this case just a single input field with an id for the label to point at.

The input field(s)
^^^^^^^^^^^^^^^^^^

.. code-block:: html

      <!-- The String Field -->
      <div id="form-myfield--field" class="field type-string widget-input">
        <label for="form-myfield">Myfield</label>
        <div class="inputs">
          <input id="form-myfield" type="text" name="myfield" value="" />
        </div>
      </div>

The action(s)
^^^^^^^^^^^^^

Finally, the actions block contains all of the submit buttons - in this case just a single input with the default 'submit' value.

.. code-block:: html

      <!-- The Action(s) -->
      <div class="actions">
        <input type="submit" id="form-action-submit" name="submit" value="Submit" />
      </div>
    </form>


Processing the Submitted Form
-----------------------------

Once the form is submitted, we can get the data by calling 'validate'. In order to simulate this, we're going to create a request object by hand using webob.. 

.. doctest::

    >>> import webob
    >>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
    >>> r.POST['myfield'] = 'myvalue'
    >>> form.validate(r)
    {'myfield': u'myvalue'}

And that is our simple form overview complete. 

Introduction - A Slightly More Complex Form
===========================================

OK, We're going to put a more things together for this.. 

* A custom form name
* Different schema types
* different widgets
* Form errors

Creating the form
-----------------

For our contrived example, we'll build a simple registration form.

.. doctest::

    >>> import schemaish
    >>> schema = schemaish.Structure()
    >>> schema.add( 'firstName', schemaish.String() )
    >>> schema.add( 'surname', schemaish.String() )
    >>> schema.add( 'dateOfBirth', schemaish.Date() )
    >>> schema.add( 'streetNumber', schemaish.Integer() )
    >>> schema.add( 'country', schemaish.String() )
    >>> schema.add( 'termsAndConditions', schemaish.Boolean() )
    >>> form = formish.Form(schema)
    >>> form
    formish.Form(schemaish.Structure("firstName": schemaish.String(), "surname": schemaish.String(), "dateOfBirth": schemaish.Date(), "streetNumber": schemaish.Integer(), "country": schemaish.String(), "termsAndConditions": schemaish.Boolean()), name=None, defaults={'termsAndConditions': None, 'surname': None, 'firstName': None, 'country': None, 'dateOfBirth': None, 'streetNumber': None})

As you can see, we've got strings, an integer, a data and a boolean. 

We could also have built the schema using a declarative style

.. doctest::

    >>> class MySchema(schemaish.Structure):
    ...     firstName = schemaish.String()
    ...     surname = schemaish.String()
    ...     dateOfBirth = schemaish.Date()
    ...     streetNumber = schemaish.Integer()
    ...     country = schemaish.String()
    ...     termsAndConditions = schemaish.Boolean()
    ...
    >>> form = formish.Form(MySchema())
    >>> form
    formish.Form(schemaish.Structure("firstName": schemaish.String(), "surname": schemaish.String(), "dateOfBirth": schemaish.Date(), "streetNumber": schemaish.Integer(), "country": schemaish.String(), "termsAndConditions": schemaish.Boolean()), name=None, defaults={'termsAndConditions': None, 'surname': None, 'firstName': None, 'country': None, 'dateOfBirth': None, 'streetNumber': None})

By default, all of the fields use input boxes with the date asking for isoformat and the boolean asking for True or False. We want to make the form a little friendlier though. 

We'll start with the date widget. Date parts uses three input boxes instead of a single input and, by default, is in US month first format. We're in the UK so we change dayFirst to True

.. doctest::

    >>> form['dateOfBirth'].widget = formish.DateParts(day_first=True)
    >>> form['dateOfBirth'].widget
    BoundWidget(widget=formish.DateParts(day_first=True), field=formish.Field(name='dateOfBirth', attr=schemaish.Date()))


Next we'll make the country a select box. To do this we pass a series of options to the SelectChoice widget.

.. doctest::

    >>> form['country'].widget = formish.SelectChoice(options=['UK','US'])
    >>> form['country'].widget
    BoundWidget(widget=formish.SelectChoice(options=[('UK', 'UK'), ('US', 'US')], none_option=(None, '- choose -')), field=formish.Field(name='country', attr=schemaish.String()))

If we wanted different values for our options we would pass each option in as a tuple of ('value','label'). We could also set a label for the field that appears when there is no input value. This is called the 'none_option'. The none_options defaults to ('', '--choose--') so we could change it to ('','Pick a Country'). Here is an example

.. doctest::

    >>> options = [('UK','I live in the UK'),('US','I live in the US')]
    >>> none_option = ('','Where do you live')
    >>> form['country'].widget = formish.SelectChoice(options=options, none_option=none_option)
    >>> form['country'].widget
    BoundWidget(widget=formish.SelectChoice(options=[('UK', 'I live in the UK'), ('US', 'I live in the US')], none_option=('', 'Where do you live')), field=formish.Field(name='country', attr=schemaish.String()))

Finally, we'd like a checkbox for the Boolean value

.. doctest::

    >>> form['termsAndConditions'].widget = formish.Checkbox()
    >>> form['termsAndConditions'].widget
    BoundWidget(widget=formish.Checkbox(), field=formish.Field(name='termsAndConditions', attr=schemaish.Boolean()))


How does this form work?
------------------------

Well let's give it some default values and look at what we get. 

.. doctest::

    >>> import datetime
    >>> form.defaults = {'firstName': 'Tim', 'surname': 'Parkin', 'dateOfBirth': datetime.datetime(1966,12,18), 'streetNumber': 123, 'country': 'UK', 'termsAndConditions': False}


If we create the form now, we get the following fields. One thing to note is that most widgets within Formish use strings to serialise their values into forms. The exception here is the date parts widget. 

String fields
^^^^^^^^^^^^^

This is the same as our first example but note that the label for firstName has been expanded into 'First Name'.

.. code-block:: html

    <div id="form-firstName--field" class="field type-string widget-input">
      <label for="form-firstName">First Name</label>
      <div class="inputs">
        <input id="form-firstName" type="text" name="firstName" value="Tim" />
      </div>
    </div>

    <div id="form-surname--field" class="field type-string widget-input">
      <label for="form-surname">Surname</label>
      <div class="inputs">
        <input id="form-surname" type="text" name="surname" value="Parkin" />
      </div>
    </div>

Date Field
^^^^^^^^^^

The date field splits the date into three parts, each part indicated using dotted notation.

.. raw:: html

    <div id="form-dateOfBirth--field" class="field type-date widget-dateparts">
      <label for="form-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="form-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="form-dateOfBirth-month" type="text" name="dateOfBirth.month" value="12" size="2" /> /
        <input id="form-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
    </div>

.. code-block:: html

    <div id="form-dateOfBirt--field" class="field type-date widget-dateparts">
      <label for="form-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="form-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="form-dateOfBirth-month" type="text" name="dateOfBirth.month" value="12" size="2" /> /
        <input id="form-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
    </div>

Integer Field
^^^^^^^^^^^^^

.. code-block:: html

    <div id="form-streetNumber--field" class="field type-integer widget-input">
      <label for="form-streetNumber">Street Number</label>
      <div class="inputs">
        <input id="form-streetNumber" type="text" name="streetNumber" value="123" />
      </div>
    </div>

Select Field
^^^^^^^^^^^^

This uses the 'none_option' value to show 'Where do you live' by default but because we have set a default value, 'I live in the UK' is selected.

.. raw:: html

    <div id="form-country--field" class="field type-string widget-selectchoice">
      <label for="form-country">Country</label>
      <div class="inputs">
        <select id="form-country" name="country">
          <option value="">Where do you live</option>
          <option value="UK" selected="selected" >I live in the UK</option>
          <option value="US" >I live in the US</option>
        </select>
      </div>
    </div>

.. code-block:: html

    <div id="form-country--field" class="field type-string widget-selectchoice">
      <label for="form-country">Country</label>
      <div class="inputs">
        <select id="form-country" name="country">
          <option value="">Where do you live</option>
          <option value="UK" selected="selected" >I live in the UK</option>
          <option value="US" >I live in the US</option>
        </select>
      </div>
    </div>


Boolean Field
^^^^^^^^^^^^^

.. code-block:: html

    <div id="form-termsAndConditions--field" class="field type-boolean widget-checkbox">
      <label for="form-termsAndConditions">Terms And Conditions</label>
      <div class="inputs">
        <input id="form-termsAndConditions" type="checkbox" name="termsAndConditions" value="True" checked="checked"  />
      </div>
    </div>


Processing the submitted form
-----------------------------

Repeating the creation of a request using webob, setting some input values and validating gives us:

.. doctest::

    >>> import webob
    >>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
    >>> r.POST['firstName'] = 'Tim'
    >>> r.POST['surname'] = 'Parkin'
    >>> r.POST['streetNumber'] = '123'
    >>> r.POST['dateOfBirth.day'] = '18'
    >>> r.POST['dateOfBirth.month'] = '13'
    >>> r.POST['dateOfBirth.year'] = '1966'
    >>> r.POST['country'] = 'UK'
    >>> r.POST['termsAndConditions'] = 'True'
    >>> try:
    ...     form.validate(r)
    ... except formish.FormError, e:
    ...     print e
    ...
    Tried to access data but conversion from request failed with 1 errors

The observant amongst you will notice I put a month of 13 in which has triggered a FormError.

Let's look at some of the error states on the form now

.. doctest::

    >>> form.errors
    {'dateOfBirth': 'Invalid date: month must be in 1..12'}

The form has a dictionary of errors on it that map to the field names.

.. doctest::

    >>> field = form.get_field('dateOfBirth')
    >>> field.error
    Invalid date: month must be in 1..12

The dateOfBirth field shows it's own error.

Showing the errors
------------------

The whole form is now in an error state and we can interrogate it about the errors. The form will also render itself with these errors.

.. doctest::
    >>> field.classes
    'field date dateparts error'
    >>> field()
    '<div id="form-dateOfBirth--field" class="field form-dateOfBirth type-date widget-dateparts error">\n\n<label for="form-dateOfBirth">Date Of Birth</label>\n\n\n<div class="inputs">\n\n\n<input id="form-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /\n<input id="form-dateOfBirth-month" type="text" name="dateOfBirth.month" value="13" size="2" /> /\n<input id="form-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />\n\n\n</div>\n\n\n<span class="error">Invalid date: month must be in 1..12</span>\n\n\n\n</div>\n'

This produces the following - note the error 'span' below the form field.

.. raw:: html

    <div id="form-dateOfBirth--field" class="field type-date widget-dateparts error">
      <label for="form-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="form-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="form-dateOfBirth-month" type="text" name="dateOfBirth.month" value="13" size="2" /> /
        <input id="form-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
      <span class="error">Invalid date: month must be in 1..12</span>
    </div>

.. code-block:: html

    <div id="form-dateOfBirth--field" class="field type-date widget-dateparts error">
      <label for="form-dateOfBirth">Date Of Birth</label>
      <div class="inputs">
        <input id="form-dateOfBirth" type="text" name="dateOfBirth.day" value="18" size="2" /> /
        <input id="form-dateOfBirth-month" type="text" name="dateOfBirth.month" value="13" size="2" /> /
        <input id="form-dateOfBirth-year" type="text" name="dateOfBirth.year" value="1966" size="4" />
      </div>
      <span class="error">Invalid date: month must be in 1..12</span>
    </div>

Calling the 'form()' will render the whole form including the error messages.

Let's see what happens if we have an invalid integer - we'll fix the month first

.. doctest::

    >>> r.POST['dateOfBirth.month'] = '12'
    >>> r.POST['streetNumber'] = 'aa'
    >>> try:
    ...     form.validate(r)
    ... except formish.FormError, e:
    ...     print e
    ...
    Tried to access data but conversion from request failed with 1 errors
    >>> field = form.get_field('streetNumber')
    >>> field.error
    Not a valid integer

Customising Errors
------------------

The errors attribute is available for you to change if you like. You can add your own error to a form by updating or setting the dictionary.

.. doctest::

    >>> form.errors['country'] = 'You must be outside the UK'

This will automatically add the appropriate error messages in your form just as if you had used a schema validator


Success!
--------

Finally, lets see what valid data gives us.. 

.. doctest::

    >>> r.POST['streetNumber'] = '123'
    >>> try:
    ...     form.validate(r)
    ... except formish.FormError, e:
    ...     print e
    ...
    {'termsAndConditions': True, 'surname': u'Parkin', 'firstName': u'Tim', 'country': u'UK', 'dateOfBirth': datetime.date(1966, 12, 18), 'streetNumber': 123}





Validation
==========

Validation in Formish uses simple callable validators that raise an exception,
validatish.Invalid, if validation fails.

How Validators Work
-------------------

There is a library of validators called Validatish that has most of the typical examples you might need. Let's take a look at a simple integer validator.

.. code-block:: python

    def is_string(v):
        msg = "must be a string"
        if not isinstance(v,basestring):
            raise Invalid(msg)

the String validater get's called and raises an exception if the value is not an instance of 'basestring'. Lets take a look at another validator

.. note:: 
  
    Actual validators should not raise errors when None is passed. This is to make sure non-required fields don't raise errors if they are left empty.

Here we have an integer validator. This tries to convert the value to an integer and if it fails, raises an exception.

.. code-block:: python

    def is_integer(v):
        if v is None:
            return
        msg = "must be an integer"
        try:
            if v != int(v):
                raise Invalid(msg)
        except (ValueError, TypeError):
            raise Invalid(msg)

Let's see this one in action

.. doctest::

    >>> import validatish
    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfield', schemaish.Integer(validator=validatish.is_integer) )
    >>> form = formish.Form(schema)
    >>> r = webob.Request.blank('http://localhost/', environ={'REQUEST_METHOD': 'POST'})
    >>> r.POST['myfield'] = 'aa'
    >>> try:
    ...     form.validate(r)
    ... except formish.FormError, e:
    ...     print e
    ...
    Tried to access data but conversion from request failed with 1 errors

.. doctest::

    >>> form.errors
    {'myfield': 'Not a valid integer'}

Whilst it is perfectly acceptable to use functions for validation, our main library uses classes to aid type checking (for example to find out if our field is required for css styling) and in order to pass validator configuration.

The validatish library is split up into two main modules, validate and validator. Validate contains the functions that do the actual validation. Validators are class wrappers around the functions.

For example, here is our required validation function and validator


.. code-block:: python

    def is_required(v):
        if not v and v != 0:
            raise Invalid("is required")

.. code-block:: python

    class Required(Validator):
        """ Checks that the value is not empty """

        def __call__(self, v):
            validate.is_required(v)

The Required validator is sub-classing Validator but this is just an interface class (i.e. just documents the necessary methods - in this case just __call__)

So the validator is a callable and it uses the python 'non_zero' check so see if we have a value. Obviously we have to let zero through because if we're asking for an integer, zero is a valid answer; However, an empty string, empty list or None is invalid.

.. note:: The Required validator must be sub-classed if you want to create your own required validator. This is to ensure that formish inserts the appropriate css to mark up the required form fields


File Uploads 
============

Short Version
-------------

We handle files for you so that all you have to do is process the file handle given to you.. Here is an example using the default filehandlers..

.. doctest::

    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfile', schemaish.File() )
    >>> form = formish.Form(schema)
    >>> from formish import filestore
    >>> form['myfile'].widget = formish.FileUpload()

What does this produce?
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: html

    <div id="form-myfile--field" class="field type-file widget-fileupload">
      <label for="form-myfile">Myfile</label>
      <div class="inputs">
        <input id="form-myfile-remove" type="checkbox" name="myfile.remove" value="true" />
        <input id="form-myfile-id" type="hidden" name="myfile.name" value="" />
        <input id="form-myfile-default" type="hidden" name="myfile.default" value="" />
        <input id="form-myfile" type="file" name="myfile.file" />
      </div>
    </div>

and looks like

.. raw:: html 

    <div id="form-myfile-field" class="field type-file widget-fileupload">
      <label for="form-myfile">Myfile</label>
      <div class="inputs">
        <input id="form-myfile-remove" type="checkbox" name="myfile.remove" value="true" />
        <input id="form-myfile-id" type="hidden" name="myfile.name" value="" />
        <input id="form-myfile-default" type="hidden" name="myfile.default" value="" />
        <input id="form-myfile" type="file" name="myfile.file" />
      </div>
    </div>

The checkbox is included to allow you to remove a file if necessary. 

How does this return a file to me?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will get a schemaish.type.File object back which looks like this

.. code-block:: python

    class File(object):

        def __init__(self, file, filename, mimetype):
            self.file = file
            self.filename=filename
            self.mimetype=mimetype

Where file is a file like object, filename is the original filename and the mimetype is worked out from the file suffix. All you have to do is ``.read()`` from the file attribute to get the contents.

Longer Version
--------------

File uploads are quite often the most difficult aspect of form handling. Formish has tried to make some pragmatic decisions that should ease this process for you. The first of these decisions is what type of data to use to store a file. Because we are using webob, files that arrive in formish do so in FieldStorage representation.

Upload File Temporary Storage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Formish tries to ensure that fields are 'symmetric'. i.e. what goes in comes back out in the same format). For text fields this is quite simple but for a file upload things are a little more difficult. What formish does is to use a temporary store in order to save the file in a secure location for access later. You can implement this store if you wish, using sessions or databaseses, etc. Here is the signature for a filehandler..

.. code-block:: python

    class MinimalFilestore(object):
        """ Example of File handler for formish file upload support. """

        def get(self, key, cache_tag=None):
            pass

        def put(self, key, src, cache_tag, content_type, headers=None):
            pass

As you can see, the two important things are a method to store the file and a method to get the file back off disk given the filename. 

Our tempfile handler implements this as follows.

.. code-block:: python

    class CachedTempFilestore(object):

        def __init__(self, root_dir=None, name=None):
            if root_dir is None:
                self._root_dir = tempfile.gettempdir()
            else:
                self._root_dir = root_dir
            if name is None:
                self.name = ''
            else:
                self.name = name

        def get(self, key, cache_tag=None):
            headers, f = FileSystemHeaderedFilestore.get(self, key)
            headers = dict(headers)
            if cache_tag and headers.get('Cache-Tag') == cache_tag:
                f.close()
                return (cache_tag, None, None)
            return (headers.get('Cache-Tag'), headers.get('Content-Type'), f)

        def put(self, key, src, cache_tag, content_type, headers=None):
            if headers is None:
                headers = {}
            else:
                headers = dict(headers)
            if cache_tag:
                headers['Cache-Tag'] = cache_tag
            if content_type:
                headers['Content-Type'] = content_type
            FileSystemHeaderedFilestore.put(self, key, headers, src)



We typically want to access the file again from our widget however (especially in the case of image uploads!). A fileresource is available within formish that should return an appropriate image. The fileresource needs to be able to serve images from either the main image store (database? filesystem?) or from the temporary store if the form is in the middle of being processed (i.e. after a submission that fails through validation and needs to be redisplayed).

.. code-block:: python


    class FileResource(resource.Resource):
        """ A simple file serving utility """

        def __init__(self, filestores=None, filestore=None, segments=None, cache=None):
            pass

        @resource.child(resource.any)
        def child(self, request, segments):
            return FileResource(filestores=self.filestores, segments=segments, cache=self.cache), []

        def __call__(self, request):
            """ Find the appropriate image to return including cacheing and resizing """


        def get_file(self, request, filestore, filename, etag):
            """ get the file through the cache and possibly resizing """
       
So what happens when a file is uploaded?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If we're using the CachedTempFilestore the following steps take place.

.. note:: we'll presume that the first form submit has a missing field and so the form gets redisplayed.

The first time a file is uploaded, formish takes the FieldStorage object and copies the contents of the file to a tempfile using it's ``put`` method. It will generate a cachetag using uuid.uuid4().hex (the cache tag is used as an ETAG for cacheing purposes). 

When the form page is redisplayed, the widget uses its ``urlfactory``` method to work out a url for the file. The urlfactory either uses the ``url_ident_factory`` attribute (which can be supplied when a FileUpload widget is created) or, if there is a temporary file currently used, it uses its own internal method. This means you can customise the urlfactory for your own storage but temporary filestorage during widget use is handled separately.

.. note:: We're not covering how the file is actually displayed. This is framework specific but we'll give an example for restish after this section.

When the users completes the corrections to the form and resubmits, formish processes the file. It first checks to see if the a new file has been uploaded (the widget stores a reference to the old file so it can check) and if it isn't new, it returns a schema.type.File object with None for all of the attributes (i.e. an empty Schema.type.File object indicates an unchanged file.

If there is no file (i.e. no file was submitted on a clean form or a file was removed using the checkbox) then a None is returned.

If the file is new or has changed, formish generates the schemaish.type.File object from the data stored in the temporary file.

There is a default urlfactory on the FileUpload widget

What happens if I want to use my own tempfile storage and main storage?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first thing you would look at doing is writing your own Filestore. You can use the CachedTempFilestore as a model but you will replace the FileSystemHeaderedFilestore with your own class. The FileSystemHeaderedFilestore looks as follows.

.. code-block:: python

    class FileSystemHeaderedFilestore(object):
        """
        A general purpose readable and writable file store useful for storing data
        along with additional metadata (simple key-value pairs).

        This can be used to implement temporary file stores, local caches, etc.
        XXX file ownership?
        """

        def __init__(self, root_dir):
            self._root_dir = root_dir

        def get(self, key):
            try:
                f = open(os.path.join(self._root_dir, safefilename.encode(key)), 'rb')
            except IOError, AttributeError:
                raise KeyError(key)
            headers = []
            while True:
                line = f.readline().strip()
                if not line:
                    break
                name, value = line.split(': ', 1)
                headers.append((name, value.decode('utf-8')))
            return headers, f

        def put(self, key, headers, src):
            # XXX We should only allow strings as headers keys and values.
            dest = file(os.path.join(self._root_dir, safefilename.encode(key)), 'wb')
            try:
                if isinstance(headers, dict):
                   headers = headers.items()
                for name, value in headers:
                    if isinstance(value, unicode):
                        value = value.encode('utf-8')
                    dest.write('%s: %s\n' % (name, value))
                dest.write('\n')
                _copyfile.copyfileobj(src, dest)
            finally:
                dest.close()

        def delete(self, key, glob=False):
            # if glob is true will delete all with filename prefix
            if glob == True:
                for f in os.listdir(self._root_dir):
                    if f.startswith(safefilename.encode(key)):
                        os.remove(os.path.join(self._root_dir,f))
            else:
                os.remove( os.path.join(self._root_dir, safefilename.encode(key)))

The get method simply returns a file and some headers based on a key. The only heads that the system is interested in are 'Cache-Tag' and 'Content-Type'. Cache-Tag is just a unique id which will be used to work out if a file has changed or not. Content-Type is fairly obvious (i.e. 'image/jpeg' or 'text/html').

The put method supplies a key, some headers (as above) and src, which is an open filehandle. We've added a delete method too which isn't used within formish at the moment but may be in the future.

Once you have implemented this store, you can replicate the code in CachedTempFilestore but with your own instantiation of your store in place of the tempfile instantiation.

What else can I configure?
^^^^^^^^^^^^^^^^^^^^^^^^^^

The formish ``FileUpload`` widget takes the following arguments

.. automethod:: formish.widgets.FileUpload.__init__


Uploading large files
^^^^^^^^^^^^^^^^^^^^^

Uploading very large files can cause the OS's file system cache to fill up with
a file it doesn't really need to cache. If you're on a POSIX system and you
have Chris Lamb's fadvise package installed, formish will use a more efficent
file copier that tells the OS not to bother caching any temporary files.

You get fadvise from Chris Lamb's web site, http://chris-lamb.co.uk/projects/python-fadvise/.


Sequences
=========

Formish also handles sequences in fields, the basic example of this is the checkbox and the multi-select. However formish can also handle sequences in text areas and also sequences in separate fields. For examples of more complex sequences, look in the example code at http://test.ish.io . Especially SequenceOfDateParts, SequenceOfStructures, SequenceOfUploadStructures. These should give you an idea how more complicated forms can be constructed.

Checkbox Multi Choice
---------------------

Now we've talked through the basics.. I'll skip a lot of the detail and just demonstrate the process.. 


.. doctest::

    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfield', schemaish.Sequence(schemaish.Integer()) )
    >>> form = formish.Form(schema)
    >>> form.defaults = {'myfield': [2,4]}
    >>> form['myfield'].widget = formish.CheckboxMultiChoice(options=[1,2,3,4])
    >>> form['myfield'].widget
    BoundWidget(widget=formish.CheckboxMultiChoice(options=[(1, '1'), (2, '2'), (3, '3'), (4, '4')]), field=formish.Sequence(name='myfield', attr=schemaish.Sequence(schemaish.Integer())))

Let's take a look at the html that produced.. 

.. raw:: html

    <div id="form-myfield--field" class="field type-sequence widget-checkboxmultichoice">
      <label for="form-myfield">Myfield</label>
      <div class="inputs">
        <input id="form-myfield-0" name="myfield" type="checkbox" value="1" />
        <label for="form-myfield-0">1</label>
        <br />
        <input id="form-myfield-1" name="myfield" type="checkbox" value="2" checked="checked" />
        <label for="form-myfield-1">2</label>
        <br />
        <input id="form-myfield-2" name="myfield" type="checkbox" value="3" />
        <label for="form-myfield-2">3</label>
        <br />
        <input id="form-myfield-3" name="myfield" type="checkbox" value="4" checked="checked" />
        <label for="form-myfield-3">4</label>
        <br />
      </div>
    </div>
.. code-block:: html

    <div id="form-myfield--field" class="field type-sequence widget-checkboxmultichoice">
      <label for="form-myfield">Myfield</label>
      <div class="inputs">
        <input id="form-myfield-0" name="myfield" type="checkbox" value="1" />
        <label for="form-myfield-0">1</label>
        <br />
        <input id="form-myfield-1" name="myfield" type="checkbox" value="2" checked="checked" />
        <label for="form-myfield-1">2</label>
        <br />
        <input id="form-myfield-2" name="myfield" type="checkbox" value="3" />
        <label for="form-myfield-2">3</label>
        <br />
        <input id="form-myfield-3" name="myfield" type="checkbox" value="4" checked="checked" />
        <label for="form-myfield-3">4</label>
        <br />
      </div>
    </div>

Select Multi Choice
-------------------

.. warning:: Not implemented yet

Text Area Sequence
------------------

Sometimes it's easier to enter information directly into a textarea

.. doctest::

    >>> form['myfield'].widget = formish.TextArea()

Which produces a simple text area as html. When it processes this textarea, it uses the csv module to get the data (it also uses it to put the default data onto the form). By default, the conversion uses commas for a simple sequence. e.g.

.. doctest::

    >>> form.defaults = {'myfield': [1,3,5,7]}

.. raw:: html

    <div id="form-myfield--field" class="field type-sequence widget-textarea">
      <label for="form-myfield">Myfield</label>
      <div class="inputs">
        <textarea id="form-myfield" name="myfield">1,3,5,7</textarea>
      </div>
    </div>


.. code-block:: html

    <div id="form-myfield--field" class="field type-sequence widget-textarea">
      <label for="form-myfield">Myfield</label>
      <div class="inputs">
        <textarea id="form-myfield" name="myfield">1,3,5,7</textarea>
      </div>
    </div>

However you can change this behaviour by passing the Textarea widget a converter_option dictionary value .. e.g.

.. doctest::

    >>> form['myfield'].widget = formish.TextArea(converter_options={'delimiter': '\n'})

.. raw:: html

    <textarea id="form-myfield" name="myfield">1
  3
  5
  7</textarea>

.. code-block:: html

    <textarea id="form-myfield" name="myfield">1\n3\n5\n7</textarea>

Text Area Sequence of Sequences
-------------------------------

You can also use a textarea to represent a sequence of sequences... 

.. doctest::

    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfield', schemaish.Sequence(schemaish.Sequence(schemaish.Integer())))
    >>> form = formish.Form(schema)
    >>> form.defaults = {'myfield': [[2,4],[6,8]]}
    >>> form['myfield'].widget = formish.TextArea()

In this case, the default delimiter is a comma and is used on a row by row basis.

.. raw:: html

    <textarea id="form-myfield" name="myfield">2,4
  6,8</textarea>

.. code-block:: html

    <textarea id="form-myfield" name="myfield">2,4\n6,8</textarea>

Multiple Input Fields
---------------------

.. warning:: This code hasn't settled down yet, please check for updates.

If you just pass a sequence to a form without any widgets, a jquery powered sequence editor will be used. This will allow you to add and remove the fields within the sequence. Check the 'testish' application for more details.

Nested Form Structures
======================

Formish also allows you to create sub-sections in forms that can contain any other valid form part. We'll use an address and name section to expand out registration form.

A Structure of Structures
-------------------------

.. doctest::

    >>> class MyName(schemaish.Structure):
    ...     firstName = schemaish.String()
    ...     surname = schemaish.String()
    >>> class MyAddress(schemaish.Structure):
    ...     streetNumber = schemaish.Integer()
    ...     country = schemaish.String()
    >>> class MySchema(schemaish.Structure):
    ...     name = MyName()
    ...     address = MyAddress()
    ...     termsAndConditions = schemaish.Boolean()
    >>> form = formish.Form(MySchema())

This will create the following

.. raw:: html


    <form id="form" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="form" />
      <fieldset id="form-name--field" class="field myname sequencedefault sequencecontrols">
        <legend>Name</legend>
        <div id="form-name-firstName--field" class="field type-string widget-input">
          <label for="form-name-firstName">First Name</label>
          <div class="inputs">
            <input id="form-name-firstName" type="text" name="name.firstName" value="" />
          </div>
        </div>
        <div id="form-name-surname--field" class="field type-string widget-input">
          <label for="form-name-surname">Surname</label>
          <div class="inputs">
            <input id="form-name-surname" type="text" name="name.surname" value="" />
          </div>
        </div>
      </fieldset>
      <fieldset id="form-address--field" class="field myaddress widget-sequencedefault sequencecontrols">
        <legend>Address</legend>
        <div id="form-address-streetNumber--field" class="field type-integer widget-input">
          <label for="form-address-streetNumber">Street Number</label>
          <div class="inputs">
            <input id="form-address-streetNumber" type="text" name="address.streetNumber" value="" />
          </div>
        </div>
        <div id="form-address-country--field" class="field type-string widget-input">
          <label for="form-address-country">Country</label>
          <div class="inputs">
            <input id="form-address-country" type="text" name="address.country" value="" />
          </div>
        </div>
      </fieldset>
      <div id="form-termsAndConditions--field" class="field type-boolean widget-input">
        <label for="form-termsAndConditions">Terms And Conditions</label>
        <div class="inputs">
          <input id="form-termsAndConditions" type="text" name="termsAndConditions" value="" />
        </div>
      </div>
      <div class="actions">
        <input type="submit" id="form-action-submit" name="submit" value="Submit" />
      </div>
    </form>

.. code-block:: html

    <form id="form" action="" method="post" enctype="multipart/form-data" accept-charset="utf-8">
      <input type="hidden" name="_charset_" />
      <input type="hidden" name="__formish_form__" value="form" />
      <fieldset id="form-name--field" class="field myname sequencedefault sequencecontrols">
        <legend>Name</legend>
        <div id="form-name-firstName--field" class="field type-string widget-input">
          <label for="form-name-firstName">First Name</label>
          <div class="inputs">
            <input id="form-name-firstName" type="text" name="name.firstName" value="" />
          </div>
        </div>
        <div id="form-name-surname--field" class="field type-string widget-input">
          <label for="form-name-surname">Surname</label>
          <div class="inputs">
            <input id="form-name-surname" type="text" name="name.surname" value="" />
          </div>
        </div>
      </fieldset>
      <fieldset id="form-address--field" class="field myaddress widget-sequencedefault sequencecontrols">
        <legend>Address</legend>
        <div id="form-address-streetNumber--field" class="field type-integer widget-input">
          <label for="form-address-streetNumber">Street Number</label>
          <div class="inputs">
            <input id="form-address-streetNumber" type="text" name="address.streetNumber" value="" />
          </div>
        </div>
        <div id="form-address-country--field" class="field type-string widget-input">
          <label for="form-address-country">Country</label>
          <div class="inputs">
            <input id="form-address-country" type="text" name="address.country" value="" />
          </div>
        </div>
      </fieldset>
      <div id="form-termsAndConditions--field" class="field type-boolean widget-input">
        <label for="form-termsAndConditions">Terms And Conditions</label>
        <div class="inputs">
          <input id="form-termsAndConditions" type="text" name="termsAndConditions" value="" />
        </div>
      </div>
      <div class="actions">
        <input type="submit" id="form-action-submit" name="submit" value="Submit" />
      </div>
    </form>


This data will come back in dictionary form.. i.e.

.. code-block:: python

  {'name': {'firstName':'Tim', 'surname':'Tim'}, 'address': {'streetNumber': 123, 'country': 'UK'}, 'termsAndConditions': True}

Other Combinations
------------------

Formish will also let you build up a sequence of structures and will use it's jquery javascript to allow you to dynamically add and remove sections. This also works when recursively nested so it is perfectly possibly to have a list of addresses, each of which has a list of phone numbers.

Tuples
------

A tuple can be used to create a list that has different types in it. For instance, if we used the Sequence of Sequence example above, we have no control over how many items are in each row. Using a Sequence of Tuples allows us to define the length of the row and also the types of the items in the row.

Lets see how that works.

.. doctest::

    >>> schema = schemaish.Structure()
    >>> schema.add( 'myfield', schemaish.Sequence( schemaish.Tuple( (schemaish.Integer(), schemaish.Date()) ) ) )
    >>> form = formish.Form(schema)
    >>> form['myfield'].widget=formish.TextArea()

You will now get a textarea that will return validation messages if it is unable to convert to integers or strings and that will output appropriately typed data.































Class Documentation
===================


Form Class
----------

.. autoclass:: formish.forms.Form
  :members: action, add_action, fields, validate,__call__

Field Class
-----------

.. autoclass:: formish.forms.Field
  :members: title, description, cssname, classes, value, required, error, widget,__call__
