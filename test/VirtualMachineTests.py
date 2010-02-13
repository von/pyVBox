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
        self.assertEqual(1, len(mediums))
        self.assertEqual(True, isinstance(mediums[0], HardDisk))
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

    def testSnapshot(self):
        """Test taking snapshot of a VM."""
        snapshotName = "Test Snapshot"
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(None, machine.getCurrentSnapshot())
        machine.takeSnapshot(snapshotName)
        snapshot = machine.getCurrentSnapshot()
        self.assertNotEqual(snapshot, None)
        self.assertEqual(snapshotName, snapshot.name)
        machine.deleteSnapshot(snapshot)
        self.assertEqual(None, machine.getCurrentSnapshot())
        
    def testGetAll(self):
        """Test getAll() method"""
        machines = VirtualMachine.getAll()

    def testGetOSType(self):
        """Test getOSType() method"""
        machine = VirtualMachine.open(self.testVMpath)
        osType = machine.getOSType()
        self.assertNotEqual(None, osType)
        self.assertNotEqual(None, osType.familyId)
        self.assertNotEqual(None, osType.familyDescription)
        self.assertNotEqual(None, osType.id)
        self.assertNotEqual(None, osType.description)        
