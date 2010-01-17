#!/usr/bin/env python
"""Unittests for HardDisk"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
import pyVBox.VirtualBoxException

import os.path

class HardDiskTests(pyVBoxTest):
    """Test case for HardDisk"""

    def testOpen(self):
        """Test HardDisk.open()"""
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(os.path.abspath(self.testHDpath), harddisk.location)
        self.assertEqual(os.path.basename(self.testHDpath), harddisk.basename())
        harddisk.close()

    def testOpenNotFound(self):
        """Test HardDisk.open() with not found file"""
        self.assertRaises(
            pyVBox.VirtualBoxException.VirtualBoxFileError,
            HardDisk.open, self.bogusHDpath)

    def testFind(self):
        """Test HardDisk.find()"""
        self.assertRaises(
            pyVBox.VirtualBoxException.VirtualBoxObjectNotFoundException,
            HardDisk.find, self.bogusHDpath)
        self.assertEqual(False, HardDisk.isRegistered(self.testHDpath))
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(True, HardDisk.isRegistered(self.testHDpath))
        hd = HardDisk.find(self.testHDpath)
        self.assertEqual(harddisk.getId(), hd.getId())
        harddisk.close()
        self.assertEqual(False, HardDisk.isRegistered(self.testHDpath))
