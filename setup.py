#!/usr/bin/env python

from distutils.core import setup

setup(name='OpenCloudRender',
      version='0.1',
      description='cloud-render interface for popular render-engines',
      author='Oliver Markowski',
      author_email='oliver@fullblownimages.com',
      url='somewhere on github',
      package_dir = {'cgru_python': 'cgru/lib/cgru_python', 'af_python': 'cgru/afanasy/af_python'},
      packages=['opencloudrender' ],
      py_modules = ['af_python.af', 'cgru_python.cgruconfig', 'cgru_python.cgruutils', 'cgru_python.cgrupathmap' ],      scripts=['bin/ocrSubmitUI.py','bin/ocrSubmitUI.sh']
     )
