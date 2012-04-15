#!/usr/bin/env python
"""Unittests for Medium"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import Constants
from pyVBox import HardDisk
from pyVBox import Medium
from pyVBox import VirtualBoxException


import os.path

class MediumTests(pyVBoxTest):
    """Test case for Medium"""

    def testMedium(self):
        """Test Medium basics"""
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(os.path.abspath(self.testHDpath), harddisk.location)
        self.assertEqual(os.path.basename(self.testHDpath), harddisk.basename())
        self.assertEqual(os.path.dirname(os.path.abspath(self.testHDpath)),
                         harddisk.dirname())
        self.assertEqual(os.path.basename(self.testHDpath), str(harddisk))
        self.assertNotEqual(None, harddisk.id)
        self.assertNotEqual(None, harddisk.getIMedium())
        self.assertNotEqual(None, harddisk.name)
        harddisk.close()

    def testGetType(self):
        """Test Medium.deviceType"""
        harddisk = HardDisk.open(self.testHDpath)
        self.assertEqual(harddisk.deviceType, HardDisk)

    def testCreate(self):
        """Test Medium.create()"""
        medium = Medium.create(self.cloneHDpath)
        self.assertEqual(Constants.MediumState_NotCreated, medium.state)

    def testCreateWithStorage(self):
        """Test Medium.createWithStorage()"""
        medium = Medium.createWithStorage(self.cloneHDpath, 1)
        self.assertEqual(Constants.MediumState_Created, medium.state)

    def testClone(self):
        """Test Medium.clone()"""
        harddisk = HardDisk.open(self.testHDpath)
        harddisk.clone(self.cloneHDpath)
        clonedisk = HardDisk.find(self.cloneHDpath)
        self.assertEqual(harddisk.format, harddisk.format)
        self.assertEqual(harddisk.logicalSize, harddisk.logicalSize)
        self.assertNotEqual(harddisk.id, clonedisk.id)

if __name__ == '__main__':
    main()
