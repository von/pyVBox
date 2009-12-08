#!/usr/bin/env python
"""Unittests for HardDisk"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBoxException import VirtualBoxException

class HardDiskTests(pyVBoxTest):
    """Test case for HardDisk"""

    def testOpen(self):
        """Test HardDisk.open()"""
        harddisk = HardDisk.open(self.testHDpath)
        harddisk.close()

    def testFind(self):
        """Test HardDisk.find()"""
        self.assertRaises(VirtualBoxException, 
                          HardDisk.find, self.bogusHDpath)
        harddisk = HardDisk.open(self.testHDpath)
        hd = HardDisk.find(self.testHDpath)
        self.assertEqual(harddisk.getId(), hd.getId())
        harddisk.close()
