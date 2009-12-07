#!/usr/bin/env python
"""Unittests for VirtualMachine"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualBoxException import VirtualBoxException

class VirtualMachineTests(pyVBoxTest):
    """Test case for VirtualMachine"""

    def testRegister(self):
        """Test VirtualMachine.register() and related functions"""
        machine = self.vbox.openMachine(self.testVMpath)
        machine.register()
        self.assertEqual(True, machine.registered())
        machine.unregister()
        self.assertEqual(False, machine.registered())

    def testSession(self):
        """Test VirtualMachine.openSession() and related functions"""
        machine = self.vbox.openMachine(self.testVMpath)
        self.assertEqual(False, machine.hasSession())
        self.assertRaises(VirtualBoxException,
                          machine.openSession)
        machine.register()
        machine.openSession()
        self.assertEqual(True, machine.hasSession())
        machine.closeSession()
        self.assertEqual(False, machine.hasSession())
        machine.unregister()

    def testAttachDevice(self):
        """Test VirtualMachine.attachDevice() and related functions"""
        machine = self.vbox.openMachine(self.testVMpath)
        machine.register()
        harddisk = self.vbox.openHardDisk(self.testHDpath)
        machine.openSession()
        machine.attachDevice(harddisk)
        machine.detachDevice(harddisk)
        machine.closeSession()
        machine.unregister()
        harddisk.close()
