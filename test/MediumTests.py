#!/usr/bin/env python
"""Unittests for Medium"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
from pyVBox.Medium import Medium
from pyVBox.VirtualBoxException import VirtualBoxException
from pyVBox.VirtualBoxManager import Constants

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
        self.assertEqual(True, harddisk.isHardDisk())
        harddisk.close()

    def testGetType(self):
        """Test Medium.getTypeAsString()"""
        harddisk = HardDisk.open(self.testHDpath)
        self.assertNotEqual(None, harddisk.type)
        self.assertEqual("hard drive", harddisk.getTypeAsString())

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

