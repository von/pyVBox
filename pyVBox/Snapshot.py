"""Wrapper around ISnapshot object"""

from Wrapper import Wrapper

class Snapshot(Wrapper):
    # Properties directly inherited from ISnapshot
    _passthruProperties = [
        "children",
        "description",
        "id",
        "machine",
        "name",
        "online",
        "parent",
        "timeStamp",
        ]

    def __init__(self, isnapshot):
        assert(isnapshot is not None)
        self._wrappedInstance = isnapshot

    @property
    def machine(self):
        """Return VirtualMachine object associated wit this snapshot"""
        import VirtualMachine
        return VirtualMachine(self.machine)

    @property
    def parent(self):
        """Return parent snapshot (a snapshot this one is based on), or null if the snapshot has no parent (i.e. is the first snapshot). """
        if self.parent is None:
            return None
        return Snapshot(self.parent)

    @property
    def children(self):
        """Return child snapshots (all snapshots having this one as a parent)."""
        return [Snapshot(child) for child in self.children]
