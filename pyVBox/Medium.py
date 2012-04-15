"""Wrapper around IMedium object"""

from Progress import Progress
import UUID
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager
from Wrapper import Wrapper

import os.path

class Device(object):
    """Abstract class wrapping DeviceType

    Provides convienence functions for associcated Mediums.

    type is DeviceType constant (e.g. Constants.DeviceType_DVD).
    """
    type = None
    _type_str = "undefined device"

    @classmethod
    def class_from_type(cls, type):
        """Given a type, return appropriate class"""
        for cls in cls.__subclasses__():
            if type == cls.type:
                return cls
        raise ValueError("Unknown Device type \"%d\"" % type)

    @classmethod
    def from_type(cls, type):
        """Given a type, return appropriate instance"""
        cls = cls.class_from_type(type)
        return cls()

    #
    # Medium creation methods
    #
    @classmethod
    def open(cls, path, accessMode = None):
        """Open an instance of medium for the given device."""
        return Medium.open(path, cls.type, accessMode)

    @classmethod
    def find(cls, path):
        """Find a medium for type using given path or UUID."""
        return Medium.find(path, cls.type)

    def __str__(self):
        return self._type_str

    def __unicode__(self):
        return self._type_str

class Floppy(Device):
    type = Constants.DeviceType_Floppy
    _type_str = "floppy"

class DVD(Device):
    type = Constants.DeviceType_DVD
    _type_str = "DVD"

class NetworkDevice(Device):
    type = Constants.DeviceType_Network
    _type_str = "network device"

class USBDevice(Device):
    type = Constants.DeviceType_USB
    _type_str = "USB device"

class SharedFolder(Device):
    type = Constants.DeviceType_SharedFolder
    _type_str = "shared folder"
    

class Medium(Wrapper):
    # Properties directly inherited from IMedium
    _passthruProperties = [
        "autoResize",
        "description",
        "format",
        "hostDrive",
        "id",
        "lastAccessError",
        "location",
        "logicalSize",
        "name",
        "readOnly",
        "size",
        "state",
        "type"
        ]

    # These properties are converted by given function before being returned.
    _wrappedProperties = [
        ("deviceType", Device.class_from_type),
        ]

    _manager = VirtualBoxManager()

    def __init__(self, imedium):
        """Return a Medium wrapper around given IMedium instance"""
        assert(imedium is not None)
        self._wrappedInstance = imedium

    #
    # Creation methods
    #
    @classmethod
    def open(cls, path, deviceType, accessMode = None, forceNewUuid=False):
        """Opens a medium from an existing location.

        Throws VirtualBoxFileError if file not found."""
        with VirtualBoxException.ExceptionHandler():
            if accessMode is None:
                accessMode = Constants.AccessMode_ReadWrite
            # path must be absolute path
            path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().openMedium(path,
                                               deviceType,
                                               accessMode,
                                               forceNewUuid)
        return Medium(medium)

    @classmethod
    def find(cls, path, deviceType):
        """Returns a medium that uses the given path or UUID to store medium data."""
        with VirtualBoxException.ExceptionHandler():
            if not UUID.isUUID(path):
                path = cls._canonicalizeMediumPath(path)
            medium = cls._getVBox().findMedium(path, deviceType)
        return Medium(medium)

    def clone(self, path, newUUID=True, wait=True):
        """Create a clone of this medium at the given location.

        If wait is True, does not return until process completes.
        if newUUID is true, clone will have new UUID and will be registered, otherwise will have same UUID as source medium.
        Returns Progress instance."""
        with VirtualBoxException.ExceptionHandler():
            path = self._canonicalizeMediumPath(path)
            if newUUID:
                # If target doesn't have storage, new UUID is created.
                target= self.create(path)
            else:
                # If target does have storage, UUID is copied.
                target = self.createWithStorage(path, self.logicalSize)
            progress = self.cloneTo(target, wait=wait)
        if wait:
            progress.waitForCompletion()
        return progress

    @classmethod
    def create(cls, path, format=None):
        """Create a new hard disk at the given location."""
        with VirtualBoxException.ExceptionHandler():
            path = cls._canonicalizeMediumPath(path)
        if os.path.exists(path):
            # Todo: Better exception here
            raise VirtualBoxException.VirtualBoxException(
                "Cannot create %s - file already exists." % path)
        with VirtualBoxException.ExceptionHandler():
            # Despire the name of this method it returns an IMedium
            # instance
            imedium = cls._getVBox().createHardDisk(format, path)
        return cls(imedium)
    
    @classmethod
    def createWithStorage(cls, path, size,
                          format=None, variant=None, wait=True):
        """Create a new hard disk at given location with given size (in MB).

        This is a wrapper around the create() and createBaseStorage() methods."""
        disk = cls.create(path, format)
        disk.createBaseStorage(size, variant, wait)
        return disk

    def getIMedium(self):
        """Return IMedium object."""
        return self._wrappedInstance

    def close(self):
        """Closes this medium."""
        self._wrappedInstance.close()

    def basename(self):
        """Return the basename of the location of the storage unit holding medium data."""
        return os.path.basename(self.location)

    def dirname(self):
        """Return the dirname of the location of the storage unit holding medium data."""
        return os.path.dirname(self.location)

    #
    # Internal string representations 
    #
    def __str__(self):
        return self.name

    # IMedium apparently defines this and its method will sometimes
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
        with VirtualBoxException.ExceptionHandler():
            progress = self.getIMedium().cloneTo(target.getIMedium(),
                                                 variant,
                                                 parent)
        progress = Progress(progress)
        if wait:
            progress.waitForCompletion()
        return progress

    def createBaseStorage(self, size, variant=None, wait=True):
        """Create storage for the drive of the given size (in MB).

        Returns Progress instance. If wait is True, does not return until process completes."""
        if variant is None:
            variant = Constants.MediumVariant_Standard
        with VirtualBoxException.ExceptionHandler():
            progress = self.getIMedium().createBaseStorage(size, variant)
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



