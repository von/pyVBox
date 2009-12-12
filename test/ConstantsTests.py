#!/usr/bin/env python
"""Unittests for VirtualManager.Constants"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.VirtualBoxManager import Constants
from pyVBox.VirtualBoxException import VirtualBoxException

class ConstantsTests(pyVBoxTest):
    """Test case for Constants"""

    def testConstants(self):
        """Test VirtualBoxManger.Constants"""
        s = Constants.SessionState_Closed
        s = Constants.SessionState_Null
        s = Constants.DeviceType_HardDisk
        s = Constants.MachineState_Aborted
        s = Constants.MachineState_PoweredOff
        s = Constants.MachineState_Running

if __name__ == '__main__':
    main()
