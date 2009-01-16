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

I think adding the simple 'pass in a bunch of keys' version is OK for most of what we'd like I'm sure.. 




