"""Wrapper around IVirtualBox

This is not used at this time."""

from GuestOSType import GuestOSType
from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import VirtualBoxManager
from Wrapper import Wrapper

import os.path

class VirtualBox(Wrapper):
    # Properties directly inherited from IVirtualMachine
    _passthruProperties = [
        "homeFolder",
        "packageType",
        "revision",
        "settingsFilePath",
        "version",

        # Also allow direct access to these methods. These shouldn't
        # be used directly, buy only by other pyVBox classes.
        "createMachine",
        "findMachine",
        "getMachine",
        "openExistingSession",
        "openMachine",
        "openRemoteSession",
        "openSession",
        "registerMachine",
        ]

    def __init__(self):
        self._manager = VirtualBoxManager()
        self._wrappedInstance = self._manager.getIVirtualBox()

    def getGuestOSType(self, osTypeId):
        """Returns an object describing the specified guest OS type."""
        iosType = self._wrappedInstance.getGuestOSType(osTypeId)
        return GuestOSType(iosType)

    @property
    def guestOSTypes(self):
        """Return an array of all available guest OS Types."""
        return [GuestOSType(t) for t in self._getArray('guestOSTypes')]

    @property
    def machines(self):
        """Return array of machine objects registered within this VirtualBox instance."""
        from VirtualMachine import VirtualMachine
        return [VirtualMachine(vm) for vm in self._getArray('machines')]

    def waitForEvent(self):
        self._manager.waitForEvents()

    def _getArray(self, arrayName):
        """Return the array identified by the given name"""
        return self._manager.getArray(self._wrappedInstance, arrayName)


class VirtualBoxMonitor:
    def __init__(self, vbox):
        self._vbox = vbox
        self._manager = VirtualBoxManager()
        self._isMscom = self._manager.isMSCOM()

    def onMachineStateChange(self, id, state):
        pass

    def onMachineDataChange(self, id):
        pass

    def onExtraDataCanChange(self, id, key, value):
        # Witty COM bridge thinks if someone wishes to return tuple, hresult
        # is one of values we want to return
        if self._isMscom:
            return "", 0, True
        else:
            return True, ""

    def onExtraDataChange(self, id, key, value):
        pass

    def onMediaRegistered(self, id, type, registered):
        pass

    def onMachineRegistered(self, id, registred):
        pass

    def onSessionStateChange(self, id, state):
        pass

    def onSnapshotTaken(self, mach, id):
        pass

    def onSnapshotDiscarded(self, mach, id):
        pass

    def onSnapshotChange(self, mach, id):
        pass

    def onGuestPropertyChange(self, id, name, newValue, flags):
        pass
