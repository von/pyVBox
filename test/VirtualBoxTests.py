#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import VirtualBox
from pyVBox import VirtualBoxException

class VirtualBoxTests(pyVBoxTest):
    """Test case for VirtualBox"""

    def testInit(self):
        """Test VirtualBox()"""
        vbox = VirtualBox()

    def testGuestOSTypes(self):
        """Test VirtualBox.getGustOSTypes()"""
        vbox = VirtualBox()
        self.assertNotEqual(None, vbox.guestOSTypes)

if __name__ == '__main__':
    main()

