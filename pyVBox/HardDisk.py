"""Presentation of Medium representing HardDisk"""

from Medium import Medium
from Progress import Progress
import VirtualBoxException
from VirtualBoxManager import Constants

class HardDisk(Medium):

    #
    # Creation metods
    #
    def clone(self, path, wait=True):
        """Create a clone of this drive at the given location.
        
        Returns Progress instance. If wait is True, does not return until process completes."""
        try:
            path = self._canonicalizeMediumPath(path)
            target = self.createWithStorage(path, self.logicalSize)
            progress = self.cloneTo(target, wait=wait)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if wait:
            progress.waitForCompletion()
        return progress

    @classmethod
    def create(cls, path, format=None):
        """Create a new hard disk at the given location."""
        try:
            path = cls._canonicalizeMediumPath(path)
            imedium = cls._getVBox().createHardDisk(format, path)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return HardDisk(imedium)

    @classmethod
    def createWithStorage(cls, path, size,
                          format=None, variant=None, wait=True):
        """Create a new hard disk at given location with given size (in MB).

        This is a wrapper around the create() and createBaseStorage() methods."""
        disk = HardDisk.create(path, format)
        disk.createBaseStorage(size, variant, wait)
        return disk

    @classmethod
    def open(cls, path, accessMode = None,
             setImageId=False, imageId="",
             setParentId=False, parentId=""):
        """Opens a hard disk from an existing location, optionally replacing the image UUID and/or parent UUID.

        Throws VirtualBoxFileError if file not found."""
        try:
            if accessMode is None:
                accessMode = Constants.AccessMode_ReadWrite
            # path must be absolute path
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().openHardDisk(path, accessMode,
                                                 setImageId, imageId,
                                                 setParentId, parentId)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return HardDisk(medium)

    @classmethod
    def find(cls, path):
        """Returns a hard disk that uses the given path to store medium data."""
        try:
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().findHardDisk(path)
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

    #
    # Instantiation of other methods
    #
    def cloneTo(self, target, variant=None, parent=None, wait=True):
        """Clone to the target hard drive.
        
        Returns Progress instance. If wait is True, does not return until process completes."""
        if variant is None:
            variant = Constants.MediumVariant_Standard
        try:
            progress = self.getIMedium().cloneTo(target.getIMedium(),
                                                 variant,
                                                 parent)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        progress = Progress(progress)
        if wait:
            progress.waitForCompletion()
        return progress

    def createBaseStorage(self, size, variant=None, wait=True):
        """Create storage for the drive of the given size (in MB).

        Returns Progress instance. If wait is True, does not return until process completes."""
        if variant is None:
            variant = Constants.MediumVariant_Standard
        try:
            progress = self.getIMedium().createBaseStorage(size, variant)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        progress = Progress(progress)
        if wait:
            progress.waitForCompletion()
        return progress
