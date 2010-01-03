"""Wrapper around ISession object"""

from Progress import Progress
from VirtualBox import VirtualBox
import VirtualBoxException
from VirtualBoxManager import Constants, VirtualBoxManager

class Session(object):
    _manager = VirtualBoxManager()
    _vbox = VirtualBox()

    def __init__(self, isession, vm):
        self._session = isession
        self._vm = vm
        
    def __del__(self):
        self.close()

    # Pass any requests for unrecognized attributes or methods onto
    # ISession object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._session." + attr)

    @classmethod
    def open(cls, vm):
        """Opens a new direct session with the given virtual machine."""
        try:
            isession = cls._createSession()
            cls._vbox.openSession(isession, vm.getId())
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        return Session(isession, vm)

    @classmethod
    def openExisting(cls, vm):
        """Opens a new remote session with the virtual machine for which a direct session is already open."""
        try:
            isession = cls._createSession()
            cls._vbox.openExistingSession(isession, vm.getId())
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        return Session(isession, vm)

    @classmethod
    def openRemote(cls, vm, type="gui", env=""):
        """Spawns a new process that executes a virtual machine (called a "remote session")."""
        try:
            isession = cls._createSession()
            iprogress = cls._vbox.openRemoteSession(isession,
                                                    vm.getId(),
                                                    type,
                                                    env)
            progress = Progress(iprogress)
            progress.waitForCompletion()
        except Exception, ex:
            VirtualBoxException.handle_exception(ex)
            raise
        return RemoteSession(isession, vm)

    def close(self):
        """Close any open session."""
        if not self.isClosed():
            try:
                self._session.close()
            except Exception, ex:
                VirtualBoxException.handle_exception(ex)
                raise

    def getIMachine(self):
        """Return mutable IMachine object associated with session."""
        return self._session.machine

    def getState(self):
        """Return session state."""
        return self._session.state

    def isDirect(self):
        """Is this a direct session?"""
        return (self.type == Constants.SessionType_Direct)

    def isClosed(self):
        """Is this session closed?"""
        return (self.getState() == Constants.SessionState_Closed)

    def isOpen(self):
        """Is this session open?"""
        return (self.getState() == Constants.SessionState_Open)

    @classmethod
    def _createSession(cls):
        """Create and return an ISesison object."""
        return cls._manager.mgr.getSessionObject(cls._vbox)

class RemoteSession(Session):
    """Class representing a remote session."""

    def close(self):
        """Close remote session and wait until VM state reflects this."""
        if not self.isClosed():
            try:
                super(RemoteSession, self).close()
                while not self._vm.isRemoteSessionClosed():
                    self._vbox.waitForEvent()
            except Exception, ex:
                VirtualBoxException.handle_exception(ex)
                raise
