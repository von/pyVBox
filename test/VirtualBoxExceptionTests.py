#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxException import VirtualBoxException

class VirtualBoxExceptionTests(pyVBoxTest):
    """Test case for VirtualBoxException"""

    def testRaises(self):
        """Test raise VirtualBoxException()"""
        self.assertRaises(VirtualBoxException, self.raiseVirtualBoxException)

    @staticmethod
    def raiseVirtualBoxException():
        raise VirtualBoxException("Testing")

if __name__ == '__main__':
    main()

