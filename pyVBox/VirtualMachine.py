"""Wrapper around IMachine object"""

from Session import Session
from VirtualBox import VirtualBox
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager

import os.path

class VirtualMachine:
    _manager = VirtualBoxManager()
    _vbox = VirtualBox()

    def __init__(self, machine, session=None):
        """Return a VirtualMachine wrapper around given IMachine instance"""
        self._machine = machine
        self._session = session

    def __del__(self):
        self.closeSession()

    def __str__(self):
        return self.getIMachine().name

    #
    # Top-level controls
    #
    def powerOff(self, wait=False):
        """Power off a running VM.

        If wait is True, then wait for power down to complete."""
        self._checkSession()
        try:
            console = self._session.console
            console.powerDown()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if wait:
            self.waitUntilDown()

    def eject(self):
        """Do what ever it takes to unregister the VM"""
        if not self.registered():
            # Nothing to do
            return
        if not self.hasSession():
            self.openSession()
        if self.isRunning():
            self.powerOff(wait=True)
        self.detachAllDevices()
        self.closeSession()
        self.waitForRemoteSessionClose()
        self.unregister()

    #
    # Creation methods
    #

    @classmethod
    def open(cls, path):
        """Opens a virtual machine from the existing settings file."""
        try:
            path = cls._canonicalizeVMPath(path)
            machine = cls._vbox.openMachine(path)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return VirtualMachine(machine)

    @classmethod
    def find(cls, vmName):
        """Attempts to find a virtual machine given its name."""
        try:
            machine = cls._vbox.findMachine(vmName)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return VirtualMachine(machine)
        
    #
    # Registration methods
    #

    def register(self):
        """Registers the machine within this VirtualBox installation."""
        try:
            self._vbox.registerMachine(self.getIMachine())
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def unregister(self):
        """Unregisters the machine previously registered using register()."""
        try:
            self._vbox.unregisterMachine(self.getId())
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def registered(self):
        """Is this virtual machine registered?"""
        try:
            self._vbox.getMachine(self.getId())
        except Exception, e:
            # XXX Should verify exception represents specific error
            return False
        return True

    #
    # Attribute getters
    #

    def getConsole(self):
        """Return the console associated with session."""
        self._checkSession()
        return self._session.console

    def getId(self):
        """Return the UUID of the virtual machine."""
        return self.getIMachine().id

    def getIMachine(self):
        """Return wrapped IMachine instance.

        If we have a mutable IMachine associated with a session, return that."""
        if self.hasSession():
            return self._getSessionMachine()
        else:
            return self._machine

    def getSession(self):
        self._checkSession()
        return self._session

    def getName(self):
        return self.getIMachine().name



    #
    # Session methods
    #

    def openSession(self):
        """Opens a new direct session with the given virtual machine.

        Machine must be registered."""
        if not self.registered():
            raise VirtualBoxException.VirtualBoxInvalidVMStateException(
                "VM is not registered")
        if self._session is not None:
            raise VirtualBoxException.VirtualBoxInvalidSessionStateException(
                "VM has no open session")
        try:
            if self.hasRemoteSession():
                self._session = Session.openExisting(self)
            else:
                self._session = Session.open(self)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def openRemoteSession(self, type="gui", env=""):
        """Spawns a new process that executes a virtual machine (called a "remote session")."""
        if not self.registered():
            raise VirtualBoxException.VirtualBoxInvalidVMStateException(
                "VM is not registered")
        try:
            self._session = Session.openRemote(self, type=type, env=env)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def closeSession(self):
        """Close any open session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def hasSession(self):
        """Does the machine have an open session?"""
        return ((self._session is not None) and
                (self._session.isOpen()))

    def hasDirectSession(self):
        """Does the machine have an open direct session?"""
        return ((self._session is not None) and
                (self._session.isDirect()))

    def hasRemoteSession(self):
        """Does the machine have an running remote session?"""
        state = self.getRemoteSessionState()
        return ((state == Constants.SessionState_Open) or
                (state == Constants.SessionState_Spawning) or
                (state == Constants.SessionState_Closing))

    def isRemoteSessionClosed(self):
        """Is the remote session closed?"""
        state = self.getRemoteSessionState()
        return (state == Constants.SessionState_Closed)

    def waitForRemoteSessionClose(self):
        """Wait for remote session to close."""
        while not self.isRemoteSessionClosed():
            self.waitForEvent()

    def getRemoteSessionState(self):
        """Return the session state of the VM."""
        # Seems like .sessionState is really remote session state.
        # Going with that.
        #
        # If the VM is transitioning we can get the following error:
        # Exception: 0x80070005 (The object is not ready)
        # In this case, punt and return SessionState_Null
        try:
            state = self.getIMachine().sessionState
        except:
            state = Constants.SessionState_Null
        return state

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
            self.getIMachine().attachDevice(storageController.name,
                                            controllerPort,
                                            device,
                                            deviceType,
                                            medium.getId())
            self.saveSettings()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def detachDevice(self, device):
        """Detach the device from the machine."""
        self._checkSession()
        try:
            attachment = self._findMediumAttachment(device)
            self.getIMachine().detachDevice(attachment.controller,
                                            attachment.port,
                                            attachment.device)
            self.saveSettings()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def detachAllDevices(self):
        """Detach all devices from the machine."""
        self._checkSession()
        try:
            attachments = self._getMediumAttachments()
            for attachment in attachments:
                self.getIMachine().detachDevice(attachment.controller,
                                                attachment.port,
                                                attachment.device)
            self.saveSettings()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    #
    # Settings functions
    #

    def saveSettings(self):
        """Saves any changes to machine settings made since the session has been opened or a new machine has been created, or since the last call to saveSettings or discardSettings."""
        self.getIMachine().saveSettings()

    #
    # Monitoring methods
    #

    def waitForEvent(self):
        self._getManager().waitForEvents()

    def waitUntilRunning(self):
        """Wait until machine is running."""
        while not self.isRunning():
            self.waitForEvent()

    def waitUntilDown(self):
        """Wait until machine is down (cleanly or not)."""
        while not self.isDown():
            self.waitForEvent()

    def getState(self):
        """Return state of machine."""
        return self.getIMachine().state

    def isDown(self):
        """Is machine down (PoweredOff, Aborted)?"""
        state = self.getState()
        if ((state == Constants.MachineState_Aborted) or
            (state == Constants.MachineState_PoweredOff)):
            return True
        return False

    def isRunning(self):
        """Is machine Running?"""
        state = self.getState()
        if (state == Constants.MachineState_Running):
            return True
        return False

    #
    # Internal utility functions
    #
     
    @classmethod
    def _canonicalizeVMPath(cls, path):
        """Given a path to a VM do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

    def _checkSession(self):
        """Check that we have a session or throw an exception."""
        # XXX Also check sessionState?
        if self._session is None:
            raise VirtualBoxException.VirtualBoxInvalidVMStateException(
                "VM has no open session")

    def _findMediumAttachment(self, device):
        """Given a device, find the IMediumAttachment object associated with its attachment on this machine."""
        mediumAttachments = self._getMediumAttachments()
        for attachment in mediumAttachments:
            if attachment.medium.id == device.getId():
                return attachment
        raise VirtualBoxException.VirtualBoxPluggableDeviceManagerError(
            "No attachment for device \"%s\" on VM \"%s\" found" % (device,
                                                                    self))

    #
    # Internal attribute getters
    #

    def _getArray(self, arrayName):
        """Return the array identified by the given name on this virtual machine."""
        return self._getManager().getArray(self.getIMachine(), arrayName)

    def _getManager(self):
        """Return the IVirtualBoxManager object associated with this VirtualMachine."""
        return self._manager

    def _getMediumAttachments(self):
        """Return the array of medium attachements on this virtual machine."""
        return self._getArray('mediumAttachments')

    def _getSessionMachine(self):
        """Return the machine associated with our session."""
        return self._session.getIMachine()

    def _getStorageControllers(self):
        """Return the array of storage controllers associated with this virtual machine."""
        return self._getArray('storageControllers')

# Simple implementation of IConsoleCallback
class VirtualMachineMonitor:
    def __init__(self, vm):
        self.vm = vm

    def onMousePointerShapeChange(self, visible, alpha, xHot, yHot,
                                  width, height, shape):
        pass

    def onMouseCapabilityChange(self, supportsAbsolute, needsHostCursor):
        pass

    def onKeyboardLedsChange(self, numLock, capsLock, scrollLock):
        pass

    def onStateChange(self, state):
        pass

    def onAdditionsStateChange(self):
        pass

    def onNetworkAdapterChange(self, adapter):
        pass

    def onSerialPortChange(self, port):
        pass

    def onParallelPortChange(self, port):
        pass

    def onStorageControllerChange(self):
        pass

    def onMediumChange(self, attachment):
        pass

    def onVRDPServerChange(self):
        pass

    def onRemoteDisplayInfoChange(self):
        pass

    def onUSBControllerChange(self):
        pass

    def onUSBDeviceStateChange(self, device, attached, error):
        pass

    def onSharedFolderChange(self, scope):
        pass

    def onRuntimeError(self, fatal, id, message):
        pass

    def onCanShowWindow(self):
        return True

    def onShowWindow(self, winId):
        pass
