"""Wrapper around IMachine object"""

from HardDisk import HardDisk
from Medium import Medium
from MediumAttachment import MediumAttachment
from Progress import Progress
from Session import Session
from Snapshot import Snapshot
from StorageController import StorageController
from VirtualBox import VirtualBox
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager
from Wrapper import Wrapper

from contextlib import contextmanager
import os
import os.path

class VirtualMachine(Wrapper):
    # Properties directly inherited from IMachine
    _passthruProperties = [
        "accelerate2DVideoEnabled",
        "accelerate3DEnabled",
        "accessible",
        "CPUCount",
        "currentStateModified",
        "description",
        "guestPropertyNotificationPatterns",
        "HardwareVersion",
        "hardwareUUID",
        "id",
        "lastStateChange",
        "lockMachine",
        "logFolder",
        "memorySize",
        "monitorCount",
        "name",
        "OSTypeId",
        "sessionPid",
        "sessionState",
        "sessionType",
        "settingsFilePath",
        "settingsModified",
        "snapshotCount",
        "snapshotFolder",
        "state",
        "stateFilePath",
        "statisticsUpdateInterval",
        "teleporterAddress",
        "teleporterEnabled",
        "teleporterPassword",
        "teleporterPort",
        "unregister",
        "VRAMSize",
        ]

    _manager = VirtualBoxManager()
    _vbox = VirtualBox()

    def __init__(self, machine, session=None):
        """Return a VirtualMachine wrapper around given IMachine instance"""
        self._wrappedInstance = machine

    def __del__(self):
        pass

    def __str__(self):
        return self.name

    #
    # Top-level controls
    #
    def pause(self, wait=False):
        """Pause a running VM.

        If wait is True, then wait until machine is actually paused before returning."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                session.console.pause()
        # XXX Note sure if we need a lock for this or not
        if wait:
            self.waitUntilPaused()

    def resume(self):
        """Resume a paused VM."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                session.console.resume()

    def powerOff(self, wait=False):
        """Power off a running VM.

        If wait is True, then wait for power down and session closureto complete."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                session.console.powerDown()
        # XXX Not sure we need a lock for the following
        if wait:
            self.waitUntilDown()
            self.waitUntilUnlocked()

    def powerOn(self, type="gui", env=""):
        """Spawns a new process that executes a virtual machine.

        This is spawning a "remote session" in VirtualBox terms."""
        # TODO: Add a wait argument
        if not self.isRegistered():
            raise VirtualBoxException.VirtualBoxInvalidVMStateException(
                "VM is not registered")
        with VirtualBoxException.ExceptionHandler():
            iMachine = self.getIMachine()
            session = Session.create()
            iprogress = iMachine.launchVMProcess(session.getISession(),
                                                 type, env)
            progress = Progress(iprogress)
            progress.waitForCompletion()
            session.unlockMachine()

    def eject(self):
        """Do what ever it takes to unregister the VM"""
        if not self.isRegistered():
            # Nothing to do
            return
        if self.isRunning():
            self.powerOff(wait=True)
        self.unregister(cleanup_mode=Constants.CleanupMode_DetachAllReturnNone)

    def delete(self):
        """Delete the VM.

        VM must be locked or unregistered"""
        with VirtualBoxException.ExceptionHandler():
            iMachine = self.getIMachine()
            iprogress = iMachine.delete(None)
            progress = Progress(iprogress)
            progress.waitForCompletion()

    #
    # Creation methods
    #

    @classmethod
    def open(cls, path):
        """Opens a virtual machine from the existing settings file.

        Note that calling open() on a VM that is already registered will
        throw a VirtualBoxFileNotFoundException except.

        Throws VirtualBoxFileNotFoundException if file not found."""
        with VirtualBoxException.ExceptionHandler():
            path = cls._canonicalizeVMPath(path)
            machine = cls._vbox.openMachine(path)
        return VirtualMachine(machine)

    @classmethod
    def find(cls, nameOrId):
        """Attempts to find a virtual machine given its name or UUID."""
        with VirtualBoxException.ExceptionHandler():
            machine = cls._vbox.findMachine(nameOrId)
        return VirtualMachine(machine)

    @classmethod
    def get(cls, id):
        """Attempts to find a virtual machine given its UUID."""
        return cls.find(id)

    @classmethod
    def create(cls, name, osTypeId, settingsFile=None, id=None, register=True,
               forceOverwrite=False):
        """Create a new virtual machine with the given name and osType.
    
        If settingsFile is not None, it should be a path to use instead
        of the default for the settings file.

        If id is not None, it will be used as the UUID of the
        machine. Otherwise one will be automatically generated.

        If register is True, register machine after creation."""
        with VirtualBoxException.ExceptionHandler():
            machine = cls._vbox.createMachine(settingsFile,
                                              name,
                                              osTypeId,
                                              id,
                                              forceOverwrite)
        vm = VirtualMachine(machine)
        vm.saveSettings()
        if register:
            vm.register()
        return vm

    def clone(self, name, settingsFile=None, id=None, register=True,
              description=None):
        """Clone this virtual machine as new VM with given name.

        Clones basic properties of machine plus any storage
        controllers. Does not clone any attached storage.

        If settingsFile is not None, it should be a path to use instead
        of the default for the settingsFile

        If id is not None, it will be used as the UUID of the
        new machine. Otherwise one will be automatically generated.

        If register is True, register new machine after creation.

        If description is None, copy description from source, otherwise use description."""
        vm = VirtualMachine.create(name,
                                   self.OSTypeId,
                                   settingsFile=settingsFile,
                                   id=id,
                                   # Once we register, we cannot make
                                   # changes without opening a
                                   # session, so defer any
                                   # registration.
                                   register=False)
        if description:
            vm.description = description
        else:
            vm.description = self.description
        vm.CPUCount = self.CPUCount
        vm.memorySize = self.memorySize
        vm.VRAMSize = self.VRAMSize
        vm.accelerate3DEnabled = self.accelerate3DEnabled
        vm.accelerate2DVideoEnabled = self.accelerate2DVideoEnabled
        vm.monitorCount = self.monitorCount
        controllers = self.getStorageControllers()
        vm.register()
        for controller in controllers:
            vm.addStorageController(controller.bus,
                                    name = controller.name)
        if not register:
            clone.unregister()
        return vm

    @classmethod
    def getAll(cls):
        """Return an array of all known virtual machines"""
        return [VirtualMachine(vm) for vm in cls._vbox.machines]
            
    #
    # Registration methods
    #

    def register(self):
        """Registers the machine within this VirtualBox installation."""
        with VirtualBoxException.ExceptionHandler():
            self._vbox.registerMachine(self.getIMachine())

    def unregister(self,
                   cleanup_mode=Constants.CleanupMode_DetachAllReturnNone):
        """Unregisters the machine previously registered using register()."""
        with VirtualBoxException.ExceptionHandler():
            machine = self.getIMachine()
            machine.unregister(cleanup_mode)

    def isRegistered(self):
        """Is this virtual machine registered?"""
        from VirtualBoxException import VirtualBoxObjectNotFoundException
        try:
            VirtualMachine.get(self.id)
            registered = True
        except VirtualBoxObjectNotFoundException, e:
            registered = False
        except Exception, e:
            raise
        return registered

    #
    # Snapshot methods
    #
    def getCurrentSnapshot(self):
        """Returns current snapshot of this machine or None if machine currently has no snapshots"""
        imachine = self.getIMachine()
        if imachine.currentSnapshot is None:
            return None
        return Snapshot(imachine.currentSnapshot)

    def takeSnapshot(self, name, description=None, wait=True):
        """Saves the current execution state and all settings of the machine and creates differencing images for all normal (non-independent) media.

        Returns Progress instance. If wait is True, does not return until process completes."""
        assert(name is not None)
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                iprogress = session.console.takeSnapshot(name, description)
                progress = Progress(iprogress)
        # XXX Not sure if we need a lock for this or not
        if wait:
            progress.waitForCompletion()
        return progress

    def deleteSnapshot(self, snapshot, wait=True):
        """Deletes the specified snapshot.

        Returns Progress instance. If wait is True, does not return until process completes."""
        assert(snapshot is not None)
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                iprogress = session.console.deleteSnapshot(snapshot.id)
                progress = Progress(iprogress)
        # XXX Not sure if we need a lock for this or not
        if wait:
            progress.waitForCompletion()
        return progress

    #
    # Attribute getters
    #

    def getIMachine(self):
        """Return wrapped IMachine instance."""
        return self._wrappedInstance

    def getOSType(self):
        """Returns an object describing the specified guest OS type."""
        with VirtualBoxException.ExceptionHandler():
            imachine = self.getIMachine()
            osType = self._vbox.getGuestOSType(imachine.OSTypeId)
        return osType

    #
    # Locking and unlocking
    #

    @contextmanager
    def lock(self, type=Constants.LockType_Shared):
        """Contextmanager yielding a session to a locked machine.

        Machine must be registered."""
        session = Session.create()
        with VirtualBoxException.ExceptionHandler():
            self.getIMachine().lockMachine(session.getISession(), type)
        try:
            session._setMachine(VirtualMachine(session.getIMachine()))
            yield session
        finally:
            session.unlockMachine(wait=True)

    def isLocked(self):
        """Does the machine have an open session?"""
        state = self.sessionState
        return ((state == Constants.SessionState_Locked) or
                (state == Constants.SessionState_Spawning) or
                (state == Constants.SessionState_Unlocking))

    def isUnlocked(self):
        """Does the VM not have an open session."""
        state = self.sessionState
        return ((state == Constants.SessionState_Null) or
                (state == Constants.SessionState_Unlocked))

    def waitUntilUnlocked(self):
        """Wait until VM is unlocked"""
        while not self.isUnlocked():
            self.waitForEvent()

    #
    # Attach methods
    #

    def attachMedium(self, medium):
        """Attachs a medium.."""
        self.attachDevice(medium.deviceType, medium)

    def attachDevice(self, device, medium=None):
        """Attaches a Device and optionally a Medium."""
        imedium = medium.getIMedium() if medium else None
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                # XXX following code needs to be smarter and find appropriate
                # attachment point
                storageControllers = self._getStorageControllers()
                storageController = storageControllers[0]
                controllerPort = 0
                deviceNum = 0
                session.getIMachine().attachDevice(storageController.name,
                                                   controllerPort,
                                                   deviceNum,
                                                   device.type,
                                                   imedium)
                session.saveSettings()

    def detachMedium(self, device):
        """Detach the medium from the machine."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                attachment = self._findMediumAttachment(device)
                session.getIMachine().detachDevice(attachment.controller,
                                                   attachment.port,
                                                   attachment.device)
                session.saveSettings()

    def detachAllMediums(self):
        """Detach all mediums from the machine."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                attachments = self._getMediumAttachments()
                for attachment in attachments:
                    session.getIMachine().detachDevice(attachment.controller,
                                                       attachment.port,
                                                       attachment.device)
                    session.saveSettings()

    def getAttachedMediums(self):
        """Return array of attached Medium instances."""
        with self.lock() as session:
            mediums = []
            with VirtualBoxException.ExceptionHandler():
                attachments = self._getMediumAttachments()
                attachments = filter(lambda a: a.medium is not None,
                                     attachments)
                mediums = [Medium(a.medium) for a in attachments]
            return mediums

    def getHardDrives(self):
        """Return array of Medium instances representing attached HardDrives."""
        return filter(lambda m: m.deviceType == HardDisk,
                      self.getAttachedMediums())

    #
    # MediumAttachment methods
    #
    def getMediumAttachments(self):
        """Return array of MediumAttachments"""
        return [MediumAttachment(ma) for ma in self._getMediumAttachments()]

    def _findMediumAttachment(self, device):
        """Given a device, find the IMediumAttachment object associated with its attachment on this machine."""
        assert(device is not None)
        mediumAttachments = self._getMediumAttachments()
        for attachment in mediumAttachments:
            # medium can be Null for removable devices
            if attachment.medium is not None:
                if attachment.medium.id == device.id:
                    return attachment
        raise VirtualBoxException.VirtualBoxPluggableDeviceManagerError(
            "No attachment for device \"%s\" on VM \"%s\" found" % (device,
                                                                    self))
    def _getMediumAttachments(self):
        """Return the array of medium attachements on this virtual machine."""
        return self._getArray('mediumAttachments')

    #
    # StorageController methods
    #
    
    def getStorageControllers(self):
        """Return array of StorageControllers attached to this VM"""
        return [StorageController(c) for c in self._getStorageControllers()]

    def getStorageControllerByName(self, name):
        """Return the StorageController with the given name"""
        with VirtualBoxException.ExceptionHandler():
            controller = self.getIMachine().getStorageControllerByName(name)
        return StorageController(controller)

    def getStorageControllerByInstance(self, instance):
        """Return the StorageController with the given instance number"""
        with VirtualBoxException.ExceptionHandler():
            controller = self.getIMachine().getStorageControllerByInstance(instance)
        return StorageController(controller)

    def removeStorageController(self, name):
        """Removes a storage controller from the machine."""
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                mutableMachine = session.getMachine()
                mutableMachine.getIMachine().removeStorageController(name)
            session.saveSettings()

    def doesStorageControllerExist(self, name):
        """Return boolean indicating if StorageController with given name exists"""
        exists = False
        try:
            controller = self.getStorageControllerByName(name)
        except VirtualBoxException.VirtualBoxObjectNotFoundException, e:
            exists = False
        except:
            raise
        else:
            exists = True
        return exists

    def addStorageController(self, type, name=None):
        """Add a storage controller to the virtual machine

        type should be the bus type of the new controller. Must be one of Constants.StorageBus_IDE, Constants.StorageBus_SATA, Constants.StorageBus_SCSI, or Constants.StorageBus_Floppy

        name should be the name of the storage controller. If None, a name will be assigned.

        Returns StorageController instance for new controller.
        """
        if name is None:
            name = self._getNewStorageControllerName(type)
        with self.lock() as session:
            with VirtualBoxException.ExceptionHandler():
                mutableMachine = session.getMachine()
                controller = mutableMachine.getIMachine().addStorageController(name, type)
            session.saveSettings()
        return StorageController(controller)
        
    def _getNewStorageControllerName(self, type):
        """Choose a name for a new StorageController of the given type.

        Takes a string describing the controller type and adds an number to it to uniqify it if needed."""
        baseNames = {
            Constants.StorageBus_IDE    : "IDE Controller",
            Constants.StorageBus_SATA   : "SATA Controller",
            Constants.StorageBus_SCSI   : "SCSI Controller",
            Constants.StorageBus_Floppy : "Floppy Controller"
            }
        if not baseNames.has_key(type):
            # Todo: Use correct argument type here
            raise Exception("Invalid type '%d'" % type)
        count = 1
        name = baseNames[type]
        while self.doesStorageControllerExist(name):
            count += 1
            name = "%s %d" % (baseNames[type], count)
        return name

    #
    # Settings functions
    #

    def saveSettings(self):
        """Saves any changes to machine settings made since the session has been opened or a new machine has been created, or since the last call to saveSettings or discardSettings."""
        with VirtualBoxException.ExceptionHandler():
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

    def isDown(self):
        """Is machine down (PoweredOff, Aborted)?"""
        state = self.state
        if ((state == Constants.MachineState_Aborted) or
            (state == Constants.MachineState_PoweredOff)):
            return True
        return False

    def isRunning(self):
        """Is machine Running?"""
        state = self.state
        if (state == Constants.MachineState_Running):
            return True
        return False

    def isPaused(self):
        """Is machine Paused?"""
        state = self.state
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



    #
    # Internal attribute getters
    #

    def _getArray(self, arrayName):
        """Return the array identified by the given name on this virtual machine."""
        return self._getManager().getArray(self.getIMachine(), arrayName)

    def _getManager(self):
        """Return the IVirtualBoxManager object associated with this VirtualMachine."""
        return self._manager

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
