#!/usr/bin/env python
"""Unittests for Device"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import Constants

class DeviceTests(pyVBoxTest):
    """Test cases for Device"""

    def testDevice(self):
        """Test Device class"""
        from pyVBox import Device
        self.assertEqual(Device.type, None)

    def testFromType(self):
        """Test Device.from_type()"""
        from pyVBox import Device, DVD, Floppy, \
            HardDisk, NetworkDevice, USBDevice, SharedFolder
        self.assertTrue(
            isinstance(Device.from_type(Constants.DeviceType_Floppy),
                       Floppy))
        self.assertTrue(
            isinstance(Device.from_type(Constants.DeviceType_DVD),
                       DVD))
        self.assertTrue(
            isinstance(Device.from_type(Constants.DeviceType_Network),
                       NetworkDevice))
        self.assertTrue(
            isinstance(Device.from_type(Constants.DeviceType_USB),
                       USBDevice))
        self.assertTrue(
            isinstance(Device.from_type(Constants.DeviceType_SharedFolder),
                       SharedFolder))

    def testClassFromType(self):
        """Test Device.class_from_type()"""
        from pyVBox import Device, DVD, Floppy, \
            HardDisk, NetworkDevice, USBDevice, SharedFolder
        self.assertEqual(
            Device.class_from_type(Constants.DeviceType_Floppy),
            Floppy)
        self.assertEqual(
            Device.class_from_type(Constants.DeviceType_DVD),
            DVD)
        self.assertEqual(
            Device.class_from_type(Constants.DeviceType_Network),
            NetworkDevice)
        self.assertEqual(
            Device.class_from_type(Constants.DeviceType_USB),
            USBDevice)
        self.assertEqual(
            Device.class_from_type(Constants.DeviceType_SharedFolder),
            SharedFolder)

    def testFloppy(self):
        """Test Floppy"""
        from pyVBox import Device, Floppy
        floppy = Device.from_type(Constants.DeviceType_Floppy)
        self.assertTrue(isinstance(floppy, Floppy))
        self.assertEqual(str(floppy), "floppy")

    def testDVD(self):
        """Test DVD"""
        from pyVBox import Device, DVD
        dvd = Device.from_type(Constants.DeviceType_DVD)
        self.assertTrue(isinstance(dvd, DVD))
        self.assertEqual(str(dvd), "DVD")

    def testNetworkDevice(self):
        """Test NetworkDevice"""
        from pyVBox import Device, NetworkDevice
        nd = Device.from_type(Constants.DeviceType_Network)
        self.assertTrue(isinstance(nd, NetworkDevice))
        self.assertEqual(str(nd), "network device")

    def testUSBDevice(self):
        """Test USBDevice"""
        from pyVBox import Device, USBDevice
        usb = Device.from_type(Constants.DeviceType_USB)
        self.assertTrue(isinstance(usb, USBDevice))
        self.assertEqual(str(usb), "USB device")

    def testNetworkDevice(self):
        """Test SharedFolder"""
        from pyVBox import Device, SharedFolder
        folder = Device.from_type(Constants.DeviceType_SharedFolder)
        self.assertTrue(isinstance(folder, SharedFolder))
        self.assertEqual(str(folder), "shared folder")

if __name__ == '__main__':
    main()
