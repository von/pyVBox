"""Wrapper around IVirtualBox"""

from Constants import Constants
from Medium import Medium
from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import VirtualBoxManager

import os.path

class VirtualBox:
    def __init__(self):
        self._manager = VirtualBoxManager()
        self._vbox = self._manager.getIVirtualBox()

    #
    # HardDisk functions
    #

    def openHardDisk(self, path, accessMode = None,
                     setImageId=False, imageId="",
                     setParentId=False, parentId=""):
        """Opens a medium from an existing location, optionally replacing the image UUID and/or parent UUID."""
        try:
            if accessMode is None:
                accessMode = Constants.AccessMode_ReadWrite
            # path must be absolute path
            path = self._canonicalizeMediumPath(path)
            medium = self._vbox.openHardDisk(path, accessMode,
                                             setImageId, imageId,
                                             setParentId, parentId)
        except Exception, e:
            raise VirtualBoxException(e)
        return Medium(medium)

    def findHardDisk(self, path):
        """Returns a medium that uses the given path to store medium data."""
        try:
            path = self._canonicalizeMediumPath(path)
            medium = self._vbox.findHardDisk(path)
        except Exception, e:
            raise VirtualBoxException(e)
        return Medium(medium)

    def isHardDiskOpen(self, path):
        try:
            self.findHardDisk(path)
        except Exception, e:
            # XXX Should verify exception is what is expected
            return False
        return True

    #
    # Path canonicalization methods
    #

    @classmethod
    def _canonicalizeVMPath(cls, path):
        """Given a path to a VM do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

    @classmethod
    def _canonicalizeMediumPath(cls, path):
        """Given a path to a hard drive (or other medium) do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

