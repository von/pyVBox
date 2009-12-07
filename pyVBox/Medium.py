"""Wrapper around IMedium object"""

class Medium:
    def __init__(self, imedium):
        """Return a Medium wrapper around given IMachine instance"""
        self._medium = imedium

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
