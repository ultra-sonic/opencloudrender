#!/usr/bin/env python

from distutils.core import setup

setup(name='OpenCloudRender',
      version='0.1',
      description='cloud-render interface for popular render-engines',
      author='Oliver Markowski',
      author_email='oliver@fullblownimages.com',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['opencloudrender'],
      scripts=['bin/ocrSubmitUI.py','bin/ocrSubmitUI.sh']
     )