#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for pyfrank."""

from setuptools import setup, find_packages
import sys, os

version = '0.1'

# some trove classifiers:

# License :: OSI Approved :: MIT License
# Intended Audience :: Developers
# Operating System :: POSIX

setup(
    name='pyfrank',
    version=version,
    description="a python SDK for the frank iOS automation framework",
    long_description=open('README.md').read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing'
    ],
    keywords='python frank pyfrank frankly ios qa automation robot',
    author='Daniel Ben-Zvi',
    author_email='daniel@doit9.com',
    url='https://github.com/everythingme/pyfrank',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
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
