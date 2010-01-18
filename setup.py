#!/usr/bin/env python
from setuptools import setup, find_packages

# Todo: Add dependency for virtualboxapi
# Todo: Sync verion here with version in util/pyvbox.py
setup(
    name = "pyVBox",
    version = "0.1preview",
    packages = find_packages(),
    scripts = ['utils/pyvbox.py'],
    test_suite = 'test',

    author = "Von Welch",
    author_email = "von@vwelch.com",
    description = "A shim layer above the VirtualBox Python API",
    license = "Apache2",
    url = "http://github.com/von/pyVBox"
)
