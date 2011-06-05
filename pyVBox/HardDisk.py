"""Presentation of Medium representing HardDisk"""

from Medium import Medium
import VirtualBoxException
from VirtualBoxManager import Constants

class HardDisk(Medium):

    #
    # Creation metods
    #
    @classmethod
    def open(cls, path, accessMode = None):
        """Opens a hard disk from an existing location, optionally replacing the image UUID and/or parent UUID.

        Throws VirtualBoxFileError if file not found."""
        try:
            if accessMode is None:
                accessMode = Constants.AccessMode_ReadWrite
            # path must be absolute path
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().openMedium(path,
                                               Constants.DeviceType_HardDisk,
                                               accessMode)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return HardDisk(medium)

    @classmethod
    def find(cls, path):
        """Returns a hard disk that uses the given path to store medium data."""
        try:
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().findMedium(path,
                                               Constants.DeviceType_HardDisk)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return HardDisk(medium)

    #
    # Utility methods
    #
    @classmethod
    def isRegistered(cls, path):
        """Is a hard disk at the given path already registered?"""
        try:
            cls.find(path)
        except Exception, e:
            # XXX Should verify exception is what is expected
            return False
        return True

