"""Presentation of Medium representing HardDisk"""

from Medium import Device
from VirtualBoxException import VirtualBoxObjectNotFoundException
from VirtualBoxManager import Constants

class HardDisk(Device):
    type = Constants.DeviceType_HardDisk

    #
    # Utility methods
    #
    @classmethod
    def isRegistered(cls, path):
        """Is a hard disk at the given path already registered?"""
        try:
            cls.find(path)
        except VirtualBoxObjectNotFoundException, e:
            return False
        return True

