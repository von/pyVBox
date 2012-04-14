"""Presentation of Medium representing HardDisk"""

from Medium import Device
import VirtualBoxException
from VirtualBoxManager import Constants

class HardDisk(Device):
    type = Constants.DeviceType_HardDisk
    _type_str = "hard disk"

    #
    # Utility methods
    #
    @classmethod
    def isRegistered(cls, path):
        """Is a hard disk at the given path already registered?"""
        try:
            with VirtualBoxException.ExceptionHandler():
                cls.find(path)
        except VirtualBoxException.VirtualBoxObjectNotFoundException:
            return False
        return True

