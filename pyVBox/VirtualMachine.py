"""Wrapper around IMachine object"""

from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager
from Progress import Progress

import os.path

class VirtualMachine:
    _manager = VirtualBoxManager()

    def __init__(self, machine, session=None):
        """Return a VirtualMachine wrapper around given IMachine instance"""
        self._machine = machine
        self._session = session
        self._unmutableMachine = None

    def __del__(self):
        self.closeSession()

    #
    # Top-level controls
    #
    def powerOff(self):
        """Power off a running VM"""
        self._checkSession()
        try:
            console = self._session.console
            console.powerDown()
        except Exception, e:
            raise VirtualBoxException(e)

    #
    # Creation methods
    #

    @classmethod
    def open(cls, path):
        """Opens a virtual machine from the existing settings file."""
        try:
            path = cls._canonicalizeVMPath(path)
            machine = cls._getVBox().openMachine(path)
        except Exception, e:
            raise VirtualBoxException(e)
        return VirtualMachine(machine)

    @classmethod
    def find(cls, vmName):
        """Attempts to find a virtual machine given its name."""
        try:
            machine = cls._getVBox().findMachine(vmName)
        except Exception, e:
            raise VirtualBoxException(e)
        return VirtualMachine(machine)
        
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

    def getConsole(self):
        """Return the console associated with session."""
        self._checkSession()
        return self._session.console

    def getId(self):
        """Return the UUID of the virtual machine."""
        return self._machine.id

    def getIMachine(self):
        return self._machine

    def getSession(self):
        self._checkSession()
        return self._session

    def getName(self):
        return self._machine.name

    #
    # Session methods
    #

    def openSession(self):
        """Opens a new direct session with the given virtual machine.

        Machine must be registered."""
        if not self.registered():
            raise VirtualBoxException("Cannot open session to unregistered VM")
        if self._session is not None:
            raise VirtualBoxException("Attempt to open session when one already open")
        try:
            # XXX Check for existing session?
            self._session = self._getManager().openMachineSession(self.getId())
        except Exception, e:
            raise VirtualBoxException(e)
        # Replace machine with mutable version, saving unmutable version
        self._unmutableMachine = self._machine
        self._machine = self._session.machine

    def openRemoteSession(self, type="gui", env=""):
        """Spawns a new process that executes a virtual machine (called a "remote session")."""
        if not self.registered():
            raise VirtualBoxException("Cannot open session to unregistered VM")
        try:
            self._session = self._getManager().mgr.getSessionObject(self._getVBox())
            iprogress = self._getVBox().openRemoteSession(self._session,
                                                          self.getId(),
                                                          type,
                                                          env)
            progress = Progress(iprogress)
            progress.waitForCompletion()
        except Exception, e:
            raise e
            #raise VirtualBoxException(e)
        # Replace machine with mutable version, saving unmutable version
        self._unmutableMachine = self._machine
        self._machine = self._session.machine

    def closeSession(self):
        """Close any open session."""
        if self._session is not None:
            self._session.close()
            # Wait for session to fully close
            while self._session.state != Constants.SessionState_Closed:
                self._getVBox().waitForEvent()
            self._session = None
            # Restore unmutable machine from before session open
            if self._unmutableMachine is None:
                raise VirtualBoxException("State error: No umutable machine saved")
            self._machine = self._unmutableMachine
            self._unmutableMachine = None

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
    # Monitoring methods
    #

    def waitForEvent(self):
        """Wait for some form of event to occurr and return."""
        callback = self._getManager().createCallback("IConsoleCallback",
                                                     VirtualMachineMonitor,
                                                     self._machine)
        console = self.getConsole()
        console.registerCallback(callback)
        try:
            self._getManager().waitForEvents(-1)
        except:
            pass # Ignore
        finally:
            console.unregisterCallback(callback)

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
        return self._machine.state

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

    @classmethod
    def _getVBox(cls):
        """Return the VirtualBox object associated with this VirtualMachine."""
        return cls._manager.getIVirtualBox()

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
