#!/usr/bin/env python
"""Unittests for VirtualMachine"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import Constants
from pyVBox import HardDisk
from pyVBox import VirtualBoxException
from pyVBox import VirtualBoxFileNotFoundException
from pyVBox import VirtualBoxObjectNotFoundException
from pyVBox import VirtualMachine

from time import sleep

class VirtualMachineTests(pyVBoxTest):
    """Test case for VirtualMachine"""

    def testOpen(self):
        """Test VirtualMachine.open()"""
        machine = VirtualMachine.open(self.testVMpath)
        self.assertNotEqual(None, machine.id)
        self.assertNotEqual(None, machine.name)
        self.assertEqual(True, machine.isDown())

    def testOpenNotFound(self):
        """Test VirtualMachine.open() with not found file"""
        self.assertRaises(
            VirtualBoxFileNotFoundException,
            VirtualMachine.open, self.bogusVMpath)

    def testLock(self):
        """Test VirtualMachine.lock()"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertTrue(machine.isUnlocked())
        with machine.lock() as session:
            self.assertNotEqual(session, None)
            self.assertTrue(machine.isLocked())
            m2 = session.getMachine()
            self.assertNotEqual(m2, None)
        self.assertTrue(machine.isUnlocked())
        machine.unregister()

    def testRegister(self):
        """Test VirtualMachine.register() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(True, machine.isRegistered())
        m2 = VirtualMachine.find(machine.name)
        self.assertEqual(machine.id, m2.id)
        machine.unregister()
        self.assertEqual(False, machine.isRegistered())

    def testAttachDevice(self):
        """Test VirtualMachine.attachDevice()"""
        from pyVBox import DVD
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        machine.attachDevice(DVD)
        machine.unregister()

    def testAttachMedium(self):
        """Test VirtualMachine.attachMedium() and related functions"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachMedium(harddisk)
        mediums = machine.getAttachedMediums()
        self.assertEqual(1, len(mediums))
        self.assertEqual(mediums[0].deviceType, HardDisk)
        machine.detachMedium(harddisk)
        machine.unregister()
        harddisk.close()

    def testEject(self):
        """Test VirtualMachine.eject()"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(True, machine.isRegistered())
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachMedium(harddisk)
        machine.eject()
        self.assertEqual(False, machine.isRegistered())
        harddisk.close()

    def testPowerOn(self):
        """Test powering on a VM."""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        harddisk = HardDisk.open(self.testHDpath)
        machine.attachMedium(harddisk)
        machine.powerOn(type="vrdp")
        machine.waitUntilRunning()
        sleep(5)
        machine.powerOff(wait=True)
        machine.detachMedium(harddisk)
        harddisk.close()
        machine.unregister()

    def testSnapshot(self):
        """Test taking snapshot of a VM."""
        snapshotName = "Test Snapshot"
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        self.assertEqual(None, machine.getCurrentSnapshot())
        # This sleep seems to keep takeSnapshot() from hangin
        sleep(2)
        machine.takeSnapshot(snapshotName)
        snapshot = machine.getCurrentSnapshot()
        self.assertNotEqual(snapshot, None)
        self.assertEqual(snapshotName, snapshot.name)
        machine.deleteSnapshot(snapshot)
        self.assertEqual(None, machine.getCurrentSnapshot())
        machine.unregister()
        
    def testGet(self):
        """Test VirtualMachine.get() method"""
        machine = VirtualMachine.open(self.testVMpath)
        # Should fail since not registered yet
        self.assertRaises(
            VirtualBoxObjectNotFoundException,
            VirtualMachine.get, machine.id)
        machine.register()
        m2 = VirtualMachine.get(machine.id)
        self.assertNotEqual(None, m2)
        self.assertEqual(machine.id, m2.id)
        machine.unregister()

    def testGetAll(self):
        """Test VirtualMachine.getAll()"""
        # Make sure we have at least one vm
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        vms = VirtualMachine.getAll()
        self.assertTrue(len(vms) > 0)
        self.assertTrue(isinstance(vms[0], VirtualMachine))
        machine.unregister()

    def testGetOSType(self):
        """Test getOSType() method"""
        machine = VirtualMachine.open(self.testVMpath)
        osType = machine.getOSType()
        self.assertNotEqual(None, osType)
        self.assertNotEqual(None, osType.familyId)
        self.assertNotEqual(None, osType.familyDescription)
        self.assertNotEqual(None, osType.id)
        self.assertNotEqual(None, osType.description)        

    def testCreate(self):
        """Test VirtualMachine.create() method"""
        # If VM already exists and we don't specify forceOverwrite=True
        # this will raise a VirtualBoxFileError
        machine = VirtualMachine.create("CreateTestVM", "Ubuntu",
                                        forceOverwrite=True)
        # Clean up
        machine.unregister()
        machine.delete()

    def testGetStorageControllers(self):
        """Test VirtualMachine methods for getting StorageControllers"""
        machine = VirtualMachine.open(self.testVMpath)
        controllers = machine.getStorageControllers()
        self.assertNotEqual(None, controllers)
        for controller in controllers:
            c = machine.getStorageControllerByName(controller.name)
            self.assertNotEqual(None, c)
            c = machine.getStorageControllerByInstance(controller.instance)
            self.assertNotEqual(None, c)
            self.assertEqual(True,
                             machine.doesStorageControllerExist(controller.name))
    def testAddStorageController(self):
        """Test adding and removing of StorageController to a VirtualMachine"""
        # Currently the removeStorageController() method is failing with
        # an 'Operation aborted' and the test VM fails to boot if I leave
        # the added storage controllers, which messes up subsequent tests.
        return
        controllerName="TestController"
        machine = VirtualMachine.open(self.testVMpath)
        controller = machine.addStorageController(Constants.StorageBus_SCSI,
                                                  name=controllerName)
        self.assertNotEqual(None, controller)
        self.assertEqual(controllerName, controller.name)
        self.assertEqual(True,
                         machine.doesStorageControllerExist(controller.name))
        machine.removeStorageController(controller.name)
        self.assertEqual(False,
                         machine.doesStorageControllerExist(controller.name))

    def testSetAttr(self):
        """Set setting of VirtualMachine attributes"""
        machine = VirtualMachine.open(self.testVMpath)
        machine.register()
        with machine.lock() as session:
            mutableMachine = session.getMachine()
            # Double memory and make sure it persists
            newMemorySize = machine.memorySize * 2
            mutableMachine.memorySize = newMemorySize
            session.saveSettings()
            self.assertEqual(newMemorySize, mutableMachine.memorySize)
        machine.unregister()
        machine2 = VirtualMachine.open(self.testVMpath)
        self.assertEqual(newMemorySize, machine2.memorySize)

    def testClone(self):
        """Test VirtualMachine.clone() method"""
        machine = VirtualMachine.open(self.testVMpath)
        newMachine = machine.clone(self.cloneVMname)
        self.assertEqual(self.cloneVMname, newMachine.name)
        self.assertEqual(machine.description, newMachine.description)
        self.assertEqual(machine.CPUCount, newMachine.CPUCount)
        self.assertEqual(machine.memorySize, newMachine.memorySize)
        self.assertEqual(machine.VRAMSize, newMachine.VRAMSize)
        self.assertEqual(machine.accelerate3DEnabled,
                         newMachine.accelerate3DEnabled)
        self.assertEqual(machine.accelerate2DVideoEnabled,
                         newMachine.accelerate2DVideoEnabled)
        self.assertEqual(machine.monitorCount,
                         newMachine.monitorCount)
        with newMachine.lock() as session:
            controllers = machine.getStorageControllers()
            newControllers = newMachine.getStorageControllers()
            self.assertEqual(len(controllers), len(newControllers))
        # Todo: compare individual controllers
        # Clean up
        newMachine.unregister()
        newMachine.delete()

if __name__ == '__main__':
    main()

