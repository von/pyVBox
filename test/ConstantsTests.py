#!/usr/bin/env python
"""Unittests for VirtualManager.Constants"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxManager import Constants
from pyVBox.VirtualBoxException import VirtualBoxException

class ConstantsTests(pyVBoxTest):
    """Test case for Constants"""

    def testCleanupModeConstants(self):
        """Test CleanupMode constants"""
        s = Constants.CleanupMode_UnregisterOnly
        s = Constants.CleanupMode_DetachAllReturnNone
        s = Constants.CleanupMode_DetachAllReturnHardDisksOnly
        s = Constants.CleanupMode_Full

    def testDeviceTypeConstants(self):
        """Test DeviceType constants"""
        s = Constants.DeviceType_HardDisk

    def testMachineStateConstants(self):
        """Test MachineState constants"""
        s = Constants.MachineState_Aborted
        s = Constants.MachineState_PoweredOff
        s = Constants.MachineState_Running

    def testSessionStateConstants(self):
        """Test SessionState constants"""
        s = Constants.SessionState_Null
        s = Constants.SessionState_Locked
        s = Constants.SessionState_Unlocked
        s = Constants.SessionState_Spawning
        s = Constants.SessionState_Unlocking

    def testSessionTypeConstants(self):
        """Test SessionType constants"""
        s = Constants.SessionType_Null
        s = Constants.SessionType_WriteLock
        s = Constants.SessionType_Remote
        s = Constants.SessionType_Shared



if __name__ == '__main__':
    main()
