"""Wrapper around IMachine object"""

from Glue import IMediumToMedium
from Medium import Medium
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
        # Our cached open session
        self._session = None

    def __del__(self):
        self.closeSession()

    def __str__(self):
        return self.getIMachine().name

    #
    # Top-level controls
    #
    def pause(self, wait=False):
        """Pause a running VM.

        If wait is True, then wait until machine is actually paused before returning."""
        session = self.getSession()
        try:
            session.console.pause()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if wait:
            self.waitUntilPaused()

    def resume(self):
        """Resume a paused VM."""
        session = self.getSession()
        try:
            session.console.resume()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def powerOff(self, wait=False):
        """Power off a running VM.

        If wait is True, then wait for power down and session closureto complete."""
        session = self.getSession()
        try:
            session.console.powerDown()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if wait:
            self.waitUntilDown()
            self.waitForSessionClose()

    def powerOn(self, type="gui", env=""):
        """Spawns a new process that executes a virtual machine.

        This is spawning a "remote session" in VirtualBox terms."""
        # TODO: Add a wait argument
        if not self.isRegistered():
            raise VirtualBoxException.VirtualBoxInvalidVMStateException(
                "VM is not registered")
        try:
            # Remote session must replace any existing session
            self.closeSession()
            self._session = Session.openRemote(self, type=type, env=env)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def eject(self):
        """Do what ever it takes to unregister the VM"""
        if not self.isRegistered():
            # Nothing to do
            return
        if self.isRunning():
            self.powerOff(wait=True)
        self.detachAllDevices()
        self.unregister()

    #
    # Creation methods
    #

    @classmethod
    def open(cls, path):
        """Opens a virtual machine from the existing settings file.

        Throws VirtualBoxFileNotFoundException if file not found."""
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
            # Must close any open session to unregister
            self.closeSession()
            self._vbox.unregisterMachine(self.getId())
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def isRegistered(self):
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

    def getId(self):
        """Return the UUID of the virtual machine."""
        return self.getIMachine().id

    def getIMachine(self):
        """Return wrapped IMachine instance."""
        return self._machine

    def getName(self):
        return self.getIMachine().name

    #
    # Session management
    #

    def getSession(self):
        """Return a session to the VM."""
        if (not self._session) or (self._session.isClosed()):
            self._session = Session.open(self)
        return self._session

    def closeSession(self):
        """Close any open session to the VM."""
        if not self._session:
            return
        isDirect = self._session.isDirect()
        self._session.close()
        self._session = None
        if isDirect:
            # For Direct sessions, wait for Machine to show session in
            # closed state or we risk race condition with subsequent
            # command if it requires no session to be open.  For
            # Remote sessions, session won't close since it will
            # remain open, so don't wait.
            self.waitForSessionClose()

    def hasSession(self):
        """Does the machine have an open session?"""
        state = self.getSessionState()
        return ((state == Constants.SessionState_Open) or
                (state == Constants.SessionState_Spawning) or
                (state == Constants.SessionState_Closing))

    def isSessionClosed(self):
        """Does the VM not have an open session."""
        state = self.getSessionState()
        return ((state == Constants.SessionState_Null) or
                (state == Constants.SessionState_Closed))

    def waitForSessionClose(self):
        """Wait for session to close."""
        while not self.isSessionClosed():
            self.waitForEvent()

    def getSessionState(self):
        """Return the session state of the VM."""
        return self.getIMachine().sessionState

    #
    # Attach methods
    #

    def attachDevice(self, medium):
        """Attachs a device. Requires an open session."""
        session = self.getSession()
        try:
            # XXX following code needs to be smarter and find appropriate
            # attachment point
            storageControllers = self._getStorageControllers()
            storageController = storageControllers[0]
            controllerPort = 0
            device = 0
            deviceType = Constants.DeviceType_HardDisk
            session.getIMachine().attachDevice(storageController.name,
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
        session = self.getSession()
        try:
            attachment = self._findMediumAttachment(device)
            session.getIMachine().detachDevice(attachment.controller,
                                               attachment.port,
                                               attachment.device)
            self.saveSettings()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def detachAllDevices(self):
        """Detach all devices from the machine."""
        session = self.getSession()
        try:
            attachments = self._getMediumAttachments()
            for attachment in attachments:
                session.getIMachine().detachDevice(attachment.controller,
                                                   attachment.port,
                                                   attachment.device)
            self.saveSettings()
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise

    def getAttachedDevices(self):
        """Return array of attached Medium instances."""
        session = self.getSession()
        mediums = []
        try:
            attachments = self._getMediumAttachments()
            attachments = filter(lambda a: a.medium is not None, attachments)
            mediums = [IMediumToMedium(a.medium) for a in attachments]
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        return mediums

    def getHardDrives(self):
        """Return array of attached HardDrive instances."""
        return filter(lambda d: d.isHardDisk(), self.getAttachedDevices())

    #
    # Settings functions
    #

    def saveSettings(self):
        """Saves any changes to machine settings made since the session has been opened or a new machine has been created, or since the last call to saveSettings or discardSettings."""
        # Use mutable machine associated with session.
        session = self.getSession()
        session.getIMachine().saveSettings()

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

    def isPaused(self):
        """Is machine Paused?"""
        state = self.getState()
        if (state == Constants.MachineState_Paused):
            return True
        return Fals

    def waitUntilPaused(self):
        """Wait until machine is paused."""
        while not self.isPaused():
            self.waitForEvent()

    #
    # Internal utility functions
    #
     
    @classmethod
    def _canonicalizeVMPath(cls, path):
        """Given a path to a VM do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

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
