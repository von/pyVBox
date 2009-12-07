"""Wrapper around IProgress object"""

class Progress:
    WaitIndefinite = -1

    def __init__(self, progress):
        """Return a Progress wrapper around given IProgress instance"""
        self._progress = progress

    def waitForCompletion(self, timeout = None):
        """Waits until the task is done (including all sub-operations).

Timeout is in milliseconds. specify None for an indefinite wait."""
        if timeout is None:
            timeout = self.WaitIndefinite
        self._progress.waitForCompletion(timeout)
        if not self._progress.completed:
            raise VirtualMachineException("Error starting VM: %s (%d)" % 
                                          (self._progress.errorInfo.text,
                                           self._progress.resultCode))

