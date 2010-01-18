#!/usr/bin/env python
"""Unittests for Medium"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBoxException import VirtualBoxException

import os.path

class MediumTests(pyVBoxTest):
    """Test case for Medium"""

    def testMedium(self):
        """Test Medium basics"""
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(os.path.abspath(self.testHDpath), harddisk.location)
        self.assertEqual(os.path.basename(self.testHDpath), harddisk.basename())
        self.assertEqual(os.path.basename(self.testHDpath), str(harddisk))
        harddisk.getId()
        harddisk.getIMedium()
        harddisk.getName()
        self.assertEqual(True, harddisk.isHardDisk())
        harddisk.close()
