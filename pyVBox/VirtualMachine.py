"""Wrapper around IMachine object"""

from Constants import Constants
from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import VirtualBoxManager

class VirtualMachine:
    def __init__(self, machine, session=None):
        """Return a VirtualMachine wrapper around given IMachine instance"""
        self._machine = machine
        self._manager = VirtualBoxManager()
        self._session = session

    def __del__(self):
        self.closeSession()

    #
    # Registration methods
    #

    def register(self):
        """Registers the machine within this VirtualBox installation."""
        try:
            vbox = self._getVBox()
            vbox.registerMachine(self._machine)
        except Exception, e:
            raise VirtualBoxException(e)

    def unregister(self):
        """Unregisters the machine previously registered using register()."""
        try:
            vbox = self._getVBox()
            vbox.unregisterMachine(self.getId())
        except Exception, e:
            raise VirtualBoxException(e)

    def registered(self):
        """Is this virtual machine registered?"""
        try:
            self._getVBox().getMachine(self.getId())
        except Exception, e:
            # XXX Should verify exception represents specific error
            return False
        return True

    #
    # Attribute getters
    #

    def getId(self):
        """Return the UUID of the virtual machine."""
        return self._machine.id

    def getIMachine(self):
        return self._machine

    #
    # Session methods
    #
    def openSession(self):
        """Opens a new direct session with the given virtual machine, returning a new VirtualMachine object.

        Machine must be registered."""
        if not self.registered():
            raise VirtualBoxException("Cannot open session to unregistered VM")
        try:
            # XXX Check for existing session?
            session = self._getManager().openMachineSession(self.getId())
        except Exception, e:
            raise VirtualBoxException(e)
        return VirtualMachine(session.machine, session=session)

    def closeSession(self):
        """Close any open session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def hasSession(self):
        """Does the machine have an open session?"""
        try:
            self._checkSession()
        except:
            return False
        return True

    #
    # Attach methods
    #

    def attachDevice(self, medium):
        """Attachs a device. Requires an open session."""
        self._checkSession()
        try:
            # XXX following code needs to be smarter and find appropriate
            # attachment point
            storageControllers = self._getStorageControllers()
            storageController = storageControllers[0]
            controllerPort = 0
            device = 0
            deviceType = Constants.DeviceType_HardDisk
            self._machine.attachDevice(storageController.name,
                                       controllerPort,
                                       device,
                                       deviceType,
                                       medium.getId())
            self.saveSettings()
        except Exception, e:
            raise VirtualBoxException(e)

    def detachDevice(self, device):
        """Detach the device from the machine."""
        self._checkSession()
        try:
            attachment = self._findMediumAttachment(device)
            self._machine.detachDevice(attachment.controller,
                                       attachment.port,
                                       attachment.device)
            self.saveSettings()
        except Exception, e:
            raise VirtualBoxException(e)

    def detachAllDevices(self):
        """Detach all devices from the machine."""
        self._checkSession()
        try:
            attachments = self._getMediumAttachments()
            for attachment in attachments:
                self._machine.detachDevice(attachment.controller,
                                           attachment.port,
                                           attachment.device)
            self.saveSettings()
        except Exception, e:
            raise VirtualBoxException(e)

    #
    # Settings functions
    #

    def saveSettings(self):
        """Saves any changes to machine settings made since the session has been opened or a new machine has been created, or since the last call to saveSettings or discardSettings."""
        self._machine.saveSettings()

    #
    # Internal utility functions
    #
     
    def _checkSession(self):
        """Check that we have a session or throw an exception."""
        # XXX Also check sessionState?
        if self._session is None:
            raise VirtualBoxException("No session established")

    def _findMediumAttachment(self, device):
        """Given a device, find the IMediumAttachment object associated with its attachment on this machine."""
        mediumAttachments = self._getMediumAttachments()
        for attachment in mediumAttachments:
            if attachment.medium.id == device.getId():
                return attachment
        raise VirtualBoxException("Device (%s) is not attached to machine" % device)

    #
    # Internal attribute getters
    #

    def _getArray(self, arrayName):
        """Return the array identified by the given name on this virtual machine."""
        return self._getManager().getArray(self._machine, arrayName)

    def _getManager(self):
        """Return the IVirtualBoxManager object associated with this VirtualMachine."""
        return self._manager

    def _getMediumAttachments(self):
        """Return the array of medium attachements on this virtual machine."""
        return self._getArray('mediumAttachments')

    def _getStorageControllers(self):
        """Return the array of storage controllers associated with this virtual machine."""
        return self._getArray('storageControllers')

    def _getVBox(self):
        """Return the IVirtualBox object associated with this VirtualMachine."""
        return self._machine.parent



