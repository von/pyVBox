"""Wrapper around IVirtualBox

This is not used at this time."""

from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import VirtualBoxManager

import os.path

class VirtualBox:
    def __init__(self):
        self._manager = VirtualBoxManager()
        self._vbox = self._manager.getIVirtualBox()

    # Pass any requests for unrecognized attributes or methods onto
    # IVirtualBox object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._vbox." + attr)

    def waitForEvent(self):
        """Wait for an event"""
        callback = self._manager.createCallback("IVirtualBoxCallback",
                                                VirtualBoxMonitor,
                                                self._vbox)
        self._vbox.registerCallback(callback)
        try:
            self._manager.waitForEvents(-1)
        except:
            pass
        finally:
            self._vbox_unregisterCallback(callback)

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
