************************************
Future Developments.. For Discussion
************************************

Customising Templates
=====================

Although we can override a widgets html by including an identically named widget in a projects local template directory (for any templating language that provides template lookup facilites), we need a way of making template customisation able to be used in an ad-hoc way (i.e. not replacing ALL textarea elements).

At the moment the template for a widget is defined by a widgets ``_template`` attribute. The first way of overriding templates would be to provide a way of substituting this value. Simply adding an ``id`` keyword argument would allow this. Using this you would be able to do the following.

During form creation
--------------------

.. code-block:: python

    >>> schema = schemaish.Structure()
    >>> schema.add( 'firstName', schemaish.String())
    >>> schema.add( 'surname', schemaish.String())

    >>> form = formish.Form()
    >>> form['firstName'].widget=TextArea()
    >>> form['firstName'].widget.id = 'TextAreaCustom'

This first example would look inside the ``formish/widgets/TextAreaCustom`` for its template parts.


.. code-block:: python

    >>> schema = schemaish.Structure()
    >>> schema.add( 'firstName', schemaish.String())
    >>> schema.add( 'surname', schemaish.String())

    >>> form = formish.Form()
    >>> form['firstName'].widget=TextArea(id='TextAreaCustom')

Because both of these override the folder for the widget, any of the field parts can also be overriden. So if you include ``field_label.html`` in your folder then just this part will be override

.. note::
 
  If a template is overridden but the directory only contains a ``field_label.html`` (for instance) should the widget default back to using the standard location?


At rendering time.. 
-------------------

.. code-block:: mako

    <%

    temporary_template = """
    <div id="${field.cssname}-field" class="${field.classes}">
    % if field.widget._template != 'Hidden':
      <label for="${field.cssname}">${field.title}</label>
    %endif
      <div class="inputs">
        <input id="${field.cssname}" type="text" name="${field.name}" value="${field.value[0]}" />
      </div>
    % if field.error:
      <span class="error">${unicode(field.error)}</span>
    % endif
    % if str(field.description) != '':
      <span class="description">${field.description}</span>
    % endif
    </div>
    """

    ${form.header()|n}
    ${form.metadata()|n}

    ${form['firstName'](template=temporary_template)|n}

    <div id="${form['surname'].cssname}-field" class="${form['surname'].classes}">
      <strong>${form['surname'].description}</strong>
      <em>${form['surname'].error}</em>
      ${form['surname'].widget()|n}
    </div>

    ${form.actions()|n}
    ${form.footer()|n}


Obviously a big widget like this is silly inline so you could/should/may/might.. 


``temporary_template.html``

.. code-block:: mako

    <div id="${field.cssname}-field" class="${field.classes}">
    % if field.widget._template != 'Hidden':
      <label for="${field.cssname}">${field.title}</label>
    %endif
      <div class="inputs">
        <input id="${field.cssname}" type="text" name="${field.name}" value="${field.value[0]}" />
      </div>
    % if field.error:
      <span class="error">${unicode(field.error)}</span>
    % endif
    % if str(field.description) != '':
      <span class="description">${field.description}</span>
    % endif
    </div>

.. code-block:: mako

    ${form.header()|n}
    ${form.metadata()|n}

    ${form['firstName'](template=open('temporary_template.html').read())|n}

    <div id="${form['surname'].cssname}-field" class="${form['surname'].classes}">
      <strong>${form['surname'].description}</strong>
      <em>${form['surname'].error}</em>
      ${form['surname'].widget()|n}
    </div>

    ${form.actions()|n}
    ${form.footer()|n}


Depending on your templating language you may be able to get that string into the call in a better way.


Filtering Field Emission
========================

It would be nice to be able to emit a bunch of fields by passing their ids to the fields() callable

.. code-block:: mako

    ${form.header()|n}
    ${form.metadata()|n}

    ${form.fields( ['title','firstname'] )|n}

    <div id="${form['surname'].cssname}-field" class="${form['surname'].classes}">
      <strong>${form['surname'].description}</strong>
      <em>${form['surname'].error}</em>
      ${form['surname'].widget()|n}
    </div>

    ${form.fields( ['surname','comments'] )

    ${form.actions()|n}
    ${form.footer()|n}

If we have a bunch of form fields we want to render with one custom one in the middle, we may want to spit out a slice of the fields.. e.g. fields[:4], then our custom one, then fields[5:]. If we can pass ``form.fields.keys`` to form.fields callable, we get lots of stuff for free.. We can apply filters, reductions, slices, etc, etc.. 


alternate syntaxes
------------------

personally I think using form.fields is OK.. Obviously the fields iterable is on one level though so we need a ``walk`` version of some sort.. Being as we are using dotted dicts omething like ``.dottedkeys`` which could then be reduced using different functions.. 

e.g.

.. code-block:: mako

    form.fields( form.fields.dottedkeys[1:4] )
    form.fields( form.fields.keys[-1] )

This would be a **lot** nicer as slices on key names soo... 

.. code-block:: mako

    form.fields( form.fields.keys[:'address'] )
    form.fields( form.fields.keys['title':'address.country'] )

But we have a problem in that we may want to have 'inclusive' slices??  I suppose you could just  

I think adding the simple 'pass in a bunch of keys' version is OK for most of what we'd like I'm sure.. 


Further possible example syntax
-------------------------------

Given this form (just listing a structure for now)

.. code-block:: yaml

   personal_details:
      title:
      firstName:
      surname:
      age:
      sex:
      fancywidget:

    address:
      street1:
      street2:
      city:
      county:
      postcode:
      country:
      continent:

    survey:
      question1:
      question2:
      question3:
      question4:
      question5:
      spam_me_please:
      terms_and_conditions:


The folllowing should render the whole form (i.e. they are all equivalent)

.. code-block:: python

   form()

   # or 

   form.header()
   form.metadata()

   form.fields( form.fields.keys )

   form.actions()
   form.footer()


we'll skip the header and footer for concisity (great word!)

.. code-block:: python

   form.fields( form.fields.keys )

   # or

   form.fields['personal_details']()
   form.fields['address']()
   form.fields['survey']()

   # or 

   form.fields['personal_details']()

   address = form['address']
   address.header()
   address.fields[:'county']()     # or address.fields( address.fields.keys[:'county'] )
   address.fields['county']() 
   address.fields['postcode':]()
   address.footer()

   form.fields['survey']()

The reason to split something up like this is to allow a single field to be tweaked.. e.g. the county field may want some custom html?

It's nice to be able to treat each sub template bit as it's own virtual form (from a templating point of view) but that all rendered id's and classes are correct. 


Matt was suggesting using some form of 'select' method on the form or fields.. e.g. 


.. code-block:: python

   form.fields['personal_details']()

   address = form['address']
   address.header()
   address.fields.select(':-county')()
   address.fields.select('county')()
   address.fields.select('-county:')()
   address.footer()

   form.fields['survey']()

This works as a slice operator but allowing us to be clever and use '-' as an inclusive or exclusive operator.. hence the following would be equivalent

.. code-block:: python

   form.fields['personal_details']()

   address = form['address']
   address.header()
   address.fields.select(':+city')()
   address.fields.select('county')()
   address.fields.select('+postcode:')()
   address.footer()

   form.fields['survey']()

I'm not sure whether the inclusive/exclusive operator should go at the front or back ... 

Having our own syntax at least allows us to do things like

.. code-block:: python

   form.fields['personal_details']()

   address = form['address']
   address.header()
   address.fields.select('street1,street2,street3,city')()
   address.fields.select('county')()
   address.fields.select('postcode,country,continent')()
   address.footer()

   form.fields['survey']()

   # and 

   address.fields.select('*,city')()
   address.fields.select('county')()
   address.fields.select('postcode,*')()
   




Deriving CSS class names from schemaish types and formish widgets
=================================================================

We need a consistent way of naming classes applied to elements when types of subclassed. The following show some possible examples?

Schemaish Types
---------------

+-----------------------------------------+---------------------------------------------------------+
|Declaration                              |  class output                                           |
+=========================================+=========================================================+
|'name': Structure(...)                   |  class="structure"                                      |
+-----------------------------------------+---------------------------------------------------------+
|class Name(Structure):                   |  class="structure name"                                 |
|    ...                                  |                                                         |
+-----------------------------------------+---------------------------------------------------------+
|'todo': Sequence(String())               |  class="sequence sequence-string"                       |
+-----------------------------------------+---------------------------------------------------------+
|'people': Sequence(Structure())          |  class="sequence sequence-structure"                    |
+-----------------------------------------+---------------------------------------------------------+
|'people': Sequence(Person())             |  class="sequence sequence-structure sequence-person"    |
+-----------------------------------------+---------------------------------------------------------+


Formish Widgets
---------------

+-----------------------------------------+---------------------------------------------------------+
|Declaration                              |  class output                                           | 
+=========================================+=========================================================+
|.widget = TextArea()                     |  class="textarea"                                       | 
+-----------------------------------------+---------------------------------------------------------+
|class RichTextArea(TextArea):            |                                                         | 
|    pass                                 |                                                         | 
+-----------------------------------------+---------------------------------------------------------+
|.widget = RichTextArea()                 |  class="textarea"                                       | 
+-----------------------------------------+---------------------------------------------------------+
|class RichTextArea(TextArea):            |                                                         | 
|    _type = 'richtextarea'               |                                                         | 
+-----------------------------------------+---------------------------------------------------------+
|.widget = RichTextArea()                 |  class="textarea richtextarea"                          | 
+-----------------------------------------+---------------------------------------------------------+
|class RichTextArea(TextArea):            |                                                         | 
|    _type = 'richtextarea'               |                                                         | 
+-----------------------------------------+---------------------------------------------------------+
|.widget = RichTextArea(type='special')   |  class="textarea richtextarea special"                  | 
+-----------------------------------------+---------------------------------------------------------+



