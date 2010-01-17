#!/usr/bin/env python
"""Unittests for VirtualMachine"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.HardDisk import HardDisk
import pyVBox.VirtualBoxException
from pyVBox.VirtualMachine import VirtualMachine

from time import sleep

class VirtualMachineTests(pyVBoxTest):
    """Test case for VirtualMachine"""

    def testOpen(self):
        """Test VirtualMachine.open()"""
        machine = VirtualMachine.open(self.testVMpath)
        id = machine.getId()
        self.assertEqual(True, machine.isDown())

    def testOpenNotFound(self):
        """Test VirtualMachine.open() with not found file"""
        self.assertRaises(
            pyVBox.VirtualBoxException.VirtualBoxFileNotFoundException,
            VirtualMachine.open, self.bogusVMpath)

    def testRegister(self):
        """Test VirtualMachine.register() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(True, machine.isRegistered())
        m2 = VirtualMachine.find(machine.getName())
        self.assertEqual(machine.getId(), m2.getId())
        machine.unregister()
        self.assertEqual(False, machine.isRegistered())

    def testAttachDevice(self):
        """Test VirtualMachine.attachDevice() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachDevice(harddisk)
        mediums = machine.getAttachedDevices()
        self.assertEqual(str(harddisk), str(mediums[0]))
        machine.detachDevice(harddisk)
        machine.unregister()
        harddisk.close()

    def testEject(self):
        """Test VirtualMachine.eject()"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachDevice(harddisk)
        self.assertEqual(True, machine.isRegistered())
        machine.eject()
        self.assertEqual(False, machine.isRegistered())
        harddisk.close()

    def testPowerOn(self):
        """Test powering on a VM."""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachDevice(harddisk)
        machine.powerOn(type="vrdp")
        machine.waitUntilRunning()
        sleep(5)
        machine.powerOff(wait=True)
        machine.detachDevice(harddisk)
        harddisk.close()
        machine.unregister()
