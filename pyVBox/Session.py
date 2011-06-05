"""Wrapper around ISession object"""

from Progress import Progress
from VirtualBox import VirtualBox
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager
from Wrapper import Wrapper

import weakref

class Session(Wrapper):
    # Properties directly inherited from IMachine
    _passthruProperties = [
        "console",
        "state",
        "type",
        ]

    _manager = VirtualBoxManager()
    _vbox = VirtualBox()

    def __init__(self, isession, vm):
        self._wrappedInstance = isession
        # Use a weak reference here to prevent circular reference with
        # and and VM that will hold up garbage collection.
        self._vm = weakref.ref(vm)
        # Sanity check
        self._check()
        
    def __del__(self):
        self.close()

    @classmethod
    def open(cls, vm):
        """Opens a session with the given firtual machine.

        Will open existing session if it alrady exists."""
        session = None
        try:
            session = Session.openExisting(vm)
        except VirtualBoxException.VirtualBoxInvalidSessionStateException, ex:
            # No existing session, fall through and open new session.
            pass
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        if not session:
            try:
                session = Session.openNew(vm)
            except Exception, ex:
                VirtualBoxException.handle_exception(ex)
                raise
        return session

    @classmethod
    def openNew(cls, vm):
        """Opens a new direct session with the given virtual machine."""
        try:
            isession = cls._createSession()
            cls._vbox.openSession(isession, vm.id)
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        return Session(isession, vm)

    @classmethod
    def openExisting(cls, vm):
        """Opens a new remote session with the virtual machine for which a direct session is already open."""
        try:
            isession = cls._createSession()
            vm.lockMachine(isession, Constants.LockType_Shared)
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        # TODO: Check session.state == SessionState_Locked as per vboxshell.py
        return Session(isession, vm)

    @classmethod
    def openRemote(cls, vm, type="gui", env=""):
        """Spawns a new process that executes a virtual machine (called a "remote session")."""
        try:
            isession = cls._createSession()
            iprogress = cls._vbox.openRemoteSession(isession,
                                                    vm.id,
                                                    type,
                                                    env)
            progress = Progress(iprogress)
            progress.waitForCompletion()
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        return RemoteSession(isession, vm)

    def close(self):
        """Close any open session, unlocking the machine."""
        if self.isLocked():
            try:
                self._wrappedInstance.unlockMachine()
                while self.isLocked():
                    self._vbox.waitForEvent()
            except Exception, ex:
                VirtualBoxException.handle_exception(ex)
                raise

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

    @classmethod
    def _createSession(cls):
        """Create and return an ISesison object."""
        return cls._manager.mgr.getSessionObject(cls._vbox)

    def _check(self):
        """Check and make sure session appears to be valid.

        Throws exception if otherwise."""
        if not self.isLocked():
            raise VirtualBoxException.VirtualBoxInvalidSessionStateException("Session in invalid state: %s" % self.state)

class RemoteSession(Session):
    """Class representing a remote session."""
    pass

