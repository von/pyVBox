#!/usr/bin/env python
"""Unittests for HardDisk"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import HardDisk 
from pyVBox import VirtualBoxException
from pyVBox import VirtualBoxFileError
from pyVBox import VirtualBoxObjectNotFoundException

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
            VirtualBoxFileError,
            HardDisk.open, self.bogusHDpath)

    def testFind(self):
        """Test HardDisk.find()"""
        self.assertEqual(False, HardDisk.isRegistered(self.testHDpath))
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(True, HardDisk.isRegistered(self.testHDpath))
        hd = HardDisk.find(self.testHDpath)
        self.assertEqual(harddisk.id, hd.id)
        harddisk.close()
        self.assertEqual(False, HardDisk.isRegistered(self.testHDpath))

    def testFindNotFound(self):
        """Test HardDisk.find() with not found file"""
        self.assertRaises(
            VirtualBoxObjectNotFoundException,
            HardDisk.find, self.bogusHDpath)

if __name__ == '__main__':
    main()
