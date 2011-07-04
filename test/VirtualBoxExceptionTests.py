#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxException import VirtualBoxException

class VirtualBoxExceptionTests(pyVBoxTest):
    """Test case for VirtualBoxException"""

    def testVirtualBoxException(self):
        """Test raise VirtualBoxException()"""
        # Not assertRaises is not a context manager until Python 2.7
        self.assertRaises(VirtualBoxException, self.raiseVirtualBoxException)

    @staticmethod
    def raiseVirtualBoxException():
        raise VirtualBoxException("Testing")

if __name__ == '__main__':
    main()

