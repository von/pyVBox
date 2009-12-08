#!/usr/bin/env python
"""Unittests for VirtualMachine"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxException import VirtualBoxException
from pyVBox.VirtualMachine import VirtualMachine

class VirtualMachineTests(pyVBoxTest):
    """Test case for VirtualMachine"""

    def testOpen(self):
        """Test VirtualMachine.open()"""
        machine = VirtualMachine.open(self.testVMpath)
        id = machine.getId()

    def testRegister(self):
        """Test VirtualMachine.register() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(True, machine.registered())
        m2 = VirtualMachine.find(machine.getName())
        self.assertEqual(machine.getId(), m2.getId())
        machine.unregister()
        self.assertEqual(False, machine.registered())

    def testSession(self):
        """Test VirtualMachine.openSession() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
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
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = self.vbox.openHardDisk(self.testHDpath)
        machine.openSession()
        machine.attachDevice(harddisk)
        machine.detachDevice(harddisk)
        machine.closeSession()
        machine.unregister()
        harddisk.close()
