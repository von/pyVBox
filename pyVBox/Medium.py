"""Wrapper around IMedium object"""

from Progress import Progress
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager

import os.path

class Medium:
    _manager = VirtualBoxManager()

    def __init__(self, imedium):
        """Return a Medium wrapper around given IMedium instance"""
        assert(imedium is not None)
        self._medium = imedium

    # Pass any requests for unrecognized attributes or methods onto
    # IMedium object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._medium." + attr)

    #
    # Creation methods
    #
    def clone(self, path, wait=True):
        """Create a clone of this medium at the given location.
        
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
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if os.path.exists(path):
            # Todo: Better exception here
            raise VirtualBoxException.VirtualBoxException(
                "Cannot create %s - file already exists." % path)
        try:
            # Despire the name of this method it returns an IMedium
            # instance
            imedium = cls._getVBox().createHardDisk(format, path)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return cls(imedium)
    
    @classmethod
    def createWithStorage(cls, path, size,
                          format=None, variant=None, wait=True):
        """Create a new hard disk at given location with given size (in MB).

        This is a wrapper around the create() and createBaseStorage() methods."""
        disk = cls.create(path, format)
        disk.createBaseStorage(size, variant, wait)
        return disk

    #
    # Attribute accessors
    # 
    def getId(self):
        """Return UUID of the virtual machine."""
        return self._medium.id

    def getIMedium(self):
        """Return IMedium object."""
        return self._medium

    def getName(self):
        """Return name"""
        return self._medium.name

    def close(self):
        """Closes this medium."""
        self._medium.close()

    def basename(self):
        """Return the basename of the location of the storage unit holding medium data."""
        return os.path.basename(self.location)

    #
    # Methods for testing deviceType
    #
    def isFloppy(self):
        """Is this a Floppy?"""
        return (self._medium.deviceType == Constants.DeviceType_Floppy)

    def isCDorDVD(self):
        """Is this a CD or DVD image?"""
        return (self._medium.deviceType == Constants.DeviceType_DVD)

    def isHardDisk(self):
        """Is this a HardDisk?"""
        return (self._medium.deviceType == Constants.DeviceType_HardDisk)

    def isNetworkDevice(self):
        """Is this a Network device?"""
        return (self._medium.deviceType == Constants.DeviceType_Network)
    
    def isUSB(self):
        """Is this a USB device?"""
        return (self._medium.deviceType == Constants.DeviceType_USB)
    
    def isSharedFolder(self):
        """Is this a shared folder?"""
        return (self._medium.deviceType == Constants.DeviceType_ShardFolder)

    #
    # Internal string representations 
    #
    def __str__(self):
        return self.name

    # IMachine apparently defines this and its method will sometimes
    # be called in preference to our __str__() method.
    def __unicode__(self):
        return self.name

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

    #
    # Internal methods
    #
    @classmethod
    def _canonicalizeMediumPath(cls, path):
        """Given a path to a hard drive (or other medium) do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

    @classmethod
    def _getVBox(cls):
        """Return the VirtualBox object associated with this VirtualMachine."""
        return cls._manager.getIVirtualBox()



