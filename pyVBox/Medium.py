"""Wrapper around IMedium object"""

from VirtualBoxManager import VirtualBoxManager

import os.path

class Medium:
    _manager = VirtualBoxManager()

    def __init__(self, imedium):
        """Return a Medium wrapper around given IMachine instance"""
        self._medium = imedium

    # Pass any requests for unrecognized attributes or methods onto
    # IMedium object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._medium." + attr)

    def getId(self):
        """Return UUID of the virtual machine."""
        return self._medium.id

    def getIMedium(self):
        """Return IMedium object."""
        return self._medium

    def getName(self):
        """Return name"""
        return self._medium.name

    def close(self):
        """Closes this medium."""
        self._medium.close()

    def __str__(self):
        return self._medium.location

    @classmethod
    def _canonicalizeMediumPath(cls, path):
        """Given a path to a hard drive (or other medium) do any needed clean up."""
        # path must be absolute path
        return os.path.abspath(path)

    @classmethod
    def _getVBox(cls):
        """Return the VirtualBox object associated with this VirtualMachine."""
        return cls._manager.getIVirtualBox()



