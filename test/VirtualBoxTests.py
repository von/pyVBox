#!/usr/bin/env python
"""Unittests for Virtualbox"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualBoxException import VirtualBoxException

class VirtualBoxTests(pyVBoxTest):
    """Test case for VirtualBox"""


    def testOpenMachine(self):
        """Test VirtualBox.openMachine()"""
        machine = self.vbox.openMachine(self.testVMpath)
        self.assertRaises(VirtualBoxException, 
                          self.vbox.openMachine, self.bogusVMpath)

    def testOpenHardDisk(self):
        """Test VirtualBox.openHardDisk()"""
        harddisk = self.vbox.openHardDisk(self.testHDpath)
        harddisk.close()

    def testFindHardDisk(self):
        """Test VirtualBox.findHardDisk()"""
        self.assertRaises(VirtualBoxException, 
                          self.vbox.findHardDisk, "/bogus/path")
        harddisk = self.vbox.openHardDisk("appliances/TestHD.vdi")
        hd = self.vbox.findHardDisk("appliances/TestHD.vdi")
        self.assertEqual(harddisk.getId(), hd.getId())
        harddisk.close()

if __name__ == '__main__':
    main()

