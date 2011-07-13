"""Wrapper around IStorageController"""

from Wrapper import Wrapper

class StorageController(Wrapper):
    # Properties directly inherited from IStorageController
    _passthruProperties = [
        "bus",
        "controllerType",
        "instance",
        "maxDevicesPerPortCount",
        "maxPortCount",
        "minPortCount",
        "name",
        "portCount",
        ]

    def __init__(self, storageController):
        """Return a StorageController around the given IStorageController instance"""
        assert(storageController is not None)
        self._wrappedInstance = storageController

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

