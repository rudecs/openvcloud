#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re
import os

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    dirname = os.path.dirname(__file__)
    init_py = open(os.path.join(dirname, package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

version = get_version('CloudscalerLibcloud')



def list_files(basedir='.', subdir='.'):
    package_data = []
    basedir_length = len(basedir)
    for dirpath, dirs, files in os.walk(os.path.join(basedir,subdir)):
        for file in files:
            package_data.append(os.path.join(dirpath[basedir_length+1:],file))
    return package_data
            
import pdb;pdb.set_trace()

setup(name='CloudScalers-LibCloud',
      version=version,
      description='Extension for Apache LibCloud libvirt to include cloud concepts like sizes,..',
      author='CloudScalers',
      author_email='info@cloudscalers.com',
      url='http://www.cloudscalers.com',
      packages = find_packages(),
      include_package_data = True,
      package_data = {'CloudscalerLibcloud':list_files(basedir='CloudscalerLibcloud',subdir='templates')},

      install_requires=[],
      classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

