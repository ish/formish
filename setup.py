from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='formish',
      version=version,
      description="Formal like library for mako/pylons",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Tim Parkin, Matt Goodall',
      author_email='developers@jdi-associates.com',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'PEAK-Rules',
          'schemaish',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
