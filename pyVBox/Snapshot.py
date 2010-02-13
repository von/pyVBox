"""Wrapper around ISnapshot object"""

class Snapshot(object):
    def __init__(self, isnapshot):
        assert(isnapshot is not None)
        self._snapshot = isnapshot

    # Pass any requests for unrecognized attributes or methods onto
    # ISnapshot object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._snapshot." + attr)

    def getMachine(self):
        """Return VirtualMachine object associated wit this snapshot"""
        import VirtualMachine
        return VirtualMachine(self.machine)

    def getParent(self):
        """Return parent snapshot (a snapshot this one is based on), or null if the snapshot has no parent (i.e. is the first snapshot). """
        if self.parent is None:
            return None
        return Snapshot(self.parent)

    def getChildren(self):
        """Return child snapshots (all snapshots having this one as a parent)."""
        return [Snapshot(child) for child in self.children]
