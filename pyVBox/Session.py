"""Wrapper around ISession object"""

from Progress import Progress
from VirtualBox import VirtualBox
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager
from Wrapper import Wrapper

import weakref

STATE_NAME = {
    Constants.SessionState_Null : "Null",
    Constants.SessionState_Locked : "Locked",
    Constants.SessionState_Unlocked : "Unlocked",
    Constants.SessionState_Spawning : "Spawning",
    Constants.SessionState_Unlocking : "Unlocking",
    }

class Session(Wrapper):
    # Properties directly inherited from IMachine
    _passthruProperties = [
        "console",
        "state",
        "type",
        ]

    _manager = VirtualBoxManager()
    _vbox = VirtualBox()

    def __init__(self, isession):
        self._wrappedInstance = isession
        self._machine = None

    @classmethod
    def create(cls):
        """Return a new Session instance"""
        return cls(cls._createSession())

    @classmethod
    def _createSession(cls):
        """Create and return an ISesison object."""
        return cls._manager.mgr.getSessionObject(cls._vbox)

    def __del__(self):
        self.unlockMachine(wait=False)

    def saveSettings(self):
        """Save changes to VM associated with session."""
        with VirtualBoxException.ExceptionHandler():
            self.getIMachine().saveSettings()

    def _setMachine(self, machine):
        """Set the machine associated with this session."""
        self._machine = machine

    def getMachine(self):
        """Return the mutable machine associated with the session."""
        return self._machine

    def unlockMachine(self, wait=True):
        """Close any open session, unlocking the machine."""
        if self.isLocked():
            with VirtualBoxException.ExceptionHandler():
                self._wrappedInstance.unlockMachine()
                if wait:
                    while self.isLocked():
                        self._vbox.waitForEvent()

    def getISession(self):
        """Return ISession instance wrapped by Session"""
        return self._wrappedInstance

    def getIMachine(self):
        """Return mutable IMachine object associated with session."""
        return self._wrappedInstance.machine

    def isDirect(self):
        """Is this a direct session?"""
        return (self.type != Constants.SessionType_Remote)

    def isLocked(self):
        """Is this session locked?"""
        return (self.state == Constants.SessionState_Locked)

    def isUnlocked(self):
        """Is this session unlocked?"""
        return (self.state == Constants.SessionState_Unlocked)

