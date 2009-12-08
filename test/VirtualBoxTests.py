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

if __name__ == '__main__':
    main()

