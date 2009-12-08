"""Presentation of Medium representing HardDisk"""

from Constants import Constants
from Medium import Medium
from VirtualBoxException import VirtualBoxException

class HardDisk(Medium):

    #
    # Creation metods
    #
    @classmethod
    def open(cls, path, accessMode = None,
             setImageId=False, imageId="",
             setParentId=False, parentId=""):
        """Opens a hard disk from an existing location, optionally replacing the image UUID and/or parent UUID."""
        try:
            if accessMode is None:
                accessMode = Constants.AccessMode_ReadWrite
            # path must be absolute path
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().openHardDisk(path, accessMode,
                                                 setImageId, imageId,
                                                 setParentId, parentId)
        except Exception, e:
            raise VirtualBoxException(e)
        return Medium(medium)

    @classmethod
    def find(cls, path):
        """Returns a hard disk that uses the given path to store medium data."""
        try:
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().findHardDisk(path)
        except Exception, e:
            raise VirtualBoxException(e)
        return Medium(medium)

    #
    # Utility methods
    #
    @classmethod
    def isOpen(cls, path):
        """Is a hard disk that used the given path already registered?"""
        try:
            cls.find(path)
        except Exception, e:
            # XXX Should verify exception is what is expected
            return False
        return True
