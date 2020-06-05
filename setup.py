#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tap-stringee-call-logs',
      version='0.1.1',
      description='Singer.io tap for extracting call logs from Stringee API',
      author='Lam Le - lamle@gmx.com',
    #   url='http://github.com/lamlephamngoc/tap-stringee',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_stringee'],
      install_requires=['singer-python==5.3.3',
                        'backoff==1.3.2',
                        'requests==2.21.0'],
      extras_require={
          'dev': [
              'ipdb==0.11'
          ]
      },
      entry_points='''
          [console_scripts]
          tap-stringee-call-logs=tap_stringee:main
      ''',
      packages=['tap_stringee'],
      include_package_data=True
)
