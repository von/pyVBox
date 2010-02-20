#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualBoxException import VirtualBoxException

class VirtualBoxTests(pyVBoxTest):
    """Test case for VirtualBox"""

    def testInit(self):
        """Test VirtualBox()"""
        vbox = VirtualBox()

    def testGetGuestOSTypes(self):
        """Test VirtualBox.getGustOSTypes()"""
        vbox = VirtualBox()
        osTypes = vbox.getGuestOSTypes()

if __name__ == '__main__':
    main()

