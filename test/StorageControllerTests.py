#!/usr/bin/env python
"""Unittests for StorageController"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import StorageController
from pyVBox import VirtualMachine

class StorageControllerTests(pyVBoxTest):
    """Test case for StorageController"""

    def testStorageController(self):
        """Test StorageController attributes"""
        machine = VirtualMachine.open(self.testVMpath)
        controllers = machine.getStorageControllers()
        # Should be an IDE controller and a SATA controller
        self.assertTrue(len(controllers) == 2)
        for controller in controllers:
            self.assertNotEqual(None, controller.name)
            self.assertNotEqual(None, controller.bus)
            self.assertNotEqual(None, controller.controllerType)
            self.assertNotEqual(None, controller.instance)
            self.assertNotEqual(None, controller.maxDevicesPerPortCount)
            self.assertNotEqual(None, controller.maxPortCount)
            self.assertNotEqual(None, controller.minPortCount)
            self.assertNotEqual(None, controller.portCount)

if __name__ == '__main__':
    main()
