#!/usr/bin/env python
"""Unittests for Medium"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBoxException import VirtualBoxException

class MediumTests(pyVBoxTest):
    """Test case for Medium"""

    def testMedium(self):
        """Test Medium basics"""
        harddisk = HardDisk.open(self.testHDpath)
        harddisk.getId()
        harddisk.getIMedium()
        harddisk.getName()
        harddisk.close()
