#!/usr/bin/env python
"""Run the unit tests."""

from pyVBoxTest import pyVBoxTest
import unittest

# Modules to test
modules = [
    "VirtualBoxExceptionTests",
    "VirtualBoxManagerTests",
    "VirtualMachineTests",
    "VirtualBoxTests"
    ]

import os
import sys

def main():
    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromNames(modules)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
