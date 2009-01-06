from setuptools import setup, find_packages
import sys, os, glob

version = '0.5.4'

setup(name='formish',
      version=version,
      description="Formish is a schema backed, templating language agnostic form generation and handling library.",
      long_description="""\
Formish is a schema backed, templating language agnostic form generation and handling library. It's main features are its granular components and its ability to create quite complex forms (including sequences, groups, sequences of groups, groups of sequences, etc). It has a built in mako templating library but should be straightforward to add other templating systems. It also has strong support for file uploads with a default tempfile storage handler. It uses schemaish for its schema, validatish for validation and convertish for type coercion.
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
          'schemaish',
          'validatish',
          'convertish',
          'webob',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
