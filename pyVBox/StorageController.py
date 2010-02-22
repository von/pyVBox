"""Wrapper around IStorageController"""

class StorageController:

    def __init__(self, storageController):
        """Return a StorageController around the given IStorageController instance"""
        self._controller = storageController
        
    # Pass any requests for unrecognized attributes or methods onto
    # IStorageController object. Doing this this way since I don't kow
    # how to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._controller." + attr)
