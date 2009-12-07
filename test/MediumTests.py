#!/usr/bin/env python
"""Unittests for Medium"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualBoxException import VirtualBoxException

class MediumTests(pyVBoxTest):
    """Test case for Medium"""

    def testMedium(self):
        """Test Medium basics"""
        harddisk = self.vbox.openHardDisk("appliances/TestHD.vdi")
        harddisk.getId()
        harddisk.getIMedium()
        harddisk.getName()
        harddisk.close()
