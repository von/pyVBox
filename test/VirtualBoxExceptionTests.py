#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxException import ExceptionHandler, VirtualBoxException
from pyVBox.VirtualMachine import VirtualMachine

class VirtualBoxExceptionTests(pyVBoxTest):
    """Test case for VirtualBoxException"""

    def testVirtualBoxException(self):
        """Test raise VirtualBoxException()"""
        # Not assertRaises is not a context manager until Python 2.7
        self.assertRaises(VirtualBoxException, self.raiseVirtualBoxException)

    @staticmethod
    def raiseVirtualBoxException():
        raise VirtualBoxException("Testing")

    def testExceptionHandler(self):
        """Test VirtualBoxException.ExceptionHandler"""
        self.assertRaises(VirtualBoxException, self.causeVirtualBoxException)

    @classmethod
    def causeVirtualBoxException(cls):
        """Should translate VirtualBox exception into a VirtualBoxException"""
        with ExceptionHandler():
            VirtualMachine.open(cls.bogusVMpath)

if __name__ == '__main__':
    main()

