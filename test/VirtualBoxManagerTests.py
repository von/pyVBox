#!/usr/bin/env python
"""Unittests for VirtualboxManager"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxManager import VirtualBoxManager

class VirtualBoxManagerTests(pyVBoxTest):
    """Test case for VirtualBoxManager"""

    def testInit(self):
        """Test VirtualBoxManager()"""
        vboxManager = VirtualBoxManager()
        del vboxManager

    def testGetVirtualBox(self):
        """Test VirtualBoxManager.getVirtualBox()"""
        vboxManager = VirtualBoxManager()
        vbox = vboxManager.getVirtualBox()

if __name__ == '__main__':
    main()

