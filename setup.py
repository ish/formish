from setuptools import setup, find_packages
import sys, os, glob

version = '0.5.8'

setup(name='formish',
      version=version,
      description="Formish is a schema backed, templating language agnostic form generation and handling library.",
      long_description="""\
Formish is a schema backed, templating language agnostic form generation and handling library. It's main features are its granular components and its ability to create quite complex forms (including sequences, groups, sequences of groups, groups of sequences, etc). It has a built in mako templating library but should be straightforward to add other templating systems. It also has strong support for file uploads with a default tempfile storage handler. It uses schemaish for its schema, validatish for validation and convertish for type coercion. 

==========
Changlelog
==========

0.5.8 (2009-01-12)
------------------

* added a SelectWithOther choice and enhanced unit and func test capabilities in testish

0.5.7 (2009-01-11)
------------------

BUG FIX: Fixed various problems with File uploads.

* added a default file acccessor that uses python tempfile with a 'store-' file prefix.

0.5.6 (2009-01-09)
------------------

BUG FIX: Fixed bug when using multi part widgets (e.g. Date Parts) inside a sequence. Added example test case.

* changes to handle new schemaish Invalid exception format
* added a contains-error class to container classes that do.

0.5.5 (2009-01-08)
------------------

Add a granular template rendering system (have a look at http://ish.io:8891/CustomisedFormLayout)

0.5.4 (2009-01-06)
------------------

Removed all * imports apart from those at the module level. Checked against pyflakes.

0.5.3 (2009-01-06)
------------------

!! API CHANGES !!

* dateFirst becomes date_first (on dateParts widget)
* allowClear becomes allow_clear (on fileUpload widget)
* fileHandler becomes filehandler (on fileUpload widget)
* showImagePreview becomes show_image_preview (on fileUpload widget)
* noneOption becomes none_option (on select widgets)

Cleaned up repo and fixed bad style in some method attributes and method names

* Added files recommended by pypi including license


0.5.2 (2009-01-05)
------------------

BUG FIX: Added an import except wrapper around the default mako import


0.5.1 (2009-01-05)
------------------

BUG FIX: Problem with redisplayed empty checkboxes after validation


0.5 (2009-01-05)
----------------

NOTE: First External Release
      Have a look at `http://ish.io:8891 <http://ish.io:8891>`_ for an example - if this isn't running, please email `support@ish.io <mailto://support@ish.io>`_

""",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Environment :: Web Environment",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Internet :: WWW/HTTP :: WSGI",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: Widget Sets",
      ], 
      keywords='form,forms,widgets,form library, ',
      author='Tim Parkin, Matt Goodall',
      author_email='developers@ish.io',
      url='http://ish.io/projects/show/formish',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'PEAK-Rules',
          'ProxyTypes',
          'schemaish',
          'validatish',
          'convertish',
          'webob',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
