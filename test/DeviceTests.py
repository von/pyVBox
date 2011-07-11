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
        self.assertEqual(Device.str(), "undefined device")

    def testFloppy(self):
        """Test Floppy"""
        from pyVBox import Device, Floppy
        self.assertEqual(Device.from_type(Constants.DeviceType_Floppy),
                         Floppy)
        self.assertEqual(Floppy.str(), "floppy")

    def testDVD(self):
        """Test DVD"""
        from pyVBox import Device, DVD
        self.assertEqual(Device.from_type(Constants.DeviceType_DVD),
                         DVD)
        self.assertEqual(DVD.str(), "DVD")

    def testNetworkDevice(self):
        """Test NetworkDevice"""
        from pyVBox import Device, NetworkDevice
        self.assertEqual(Device.from_type(Constants.DeviceType_Network),
                         NetworkDevice)
        self.assertEqual(NetworkDevice.str(), "network device")

    def testUSBDevice(self):
        """Test USBDevice"""
        from pyVBox import Device, USBDevice
        self.assertEqual(Device.from_type(Constants.DeviceType_USB),
                         USBDevice)
        self.assertEqual(USBDevice.str(), "USB device")

    def testNetworkDevice(self):
        """Test SharedFolder"""
        from pyVBox import Device, SharedFolder
        self.assertEqual(Device.from_type(Constants.DeviceType_SharedFolder),
                         SharedFolder)
        self.assertEqual(SharedFolder.str(), "shared folder")

if __name__ == '__main__':
    main()
