#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for pyfrank."""

from setuptools import setup, find_packages
import sys, os

version = '0.2.5'

# some trove classifiers:

# License :: OSI Approved :: MIT License
# Intended Audience :: Developers
# Operating System :: POSIX

setup(
    name='pyfrank',
    version=version,
    package_dir={'pyfrank': 'src'},
    packages=['pyfrank'],
    description="python binding for iOS automation using frank.",
    long_description=open('README.rst').read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
    ],
    keywords='python frank pyfrank frankly ios qa automation robot testing',
    author='Daniel Ben-Zvi',
    author_email='daniel@doit9.com',
    url='https://github.com/everythingme/pyfrank',
    license='BSD',
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
    install_requires=[
      # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
