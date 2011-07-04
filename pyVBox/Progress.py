"""Wrapper around IProgress object"""

import VirtualBoxException
from Wrapper import Wrapper

class Progress(Wrapper):
    # Properties directly inherited from IProgress
    _passthruProperties = [
        "cancelable",
        "canceled",
        "completed",
        "description",
        "errorInfo",
        "id",
        "initiator",
        "operation",
        "operationCount",
        "operationDescription",
        "operationPercent",
        "percent",
        "resultCode",
        "timeout",
        "timeRemaining",
        ]

    WaitIndefinite = -1

    def __init__(self, progress):
        """Return a Progress wrapper around given IProgress instance"""
        self._wrappedInstance = progress

    def waitForCompletion(self, timeout = None):
        """Waits until the task is done (including all sub-operations).

        Timeout is in milliseconds, specify None for an indefinite wait."""
        if timeout is None:
            timeout = self.WaitIndefinite
        with VirtualBoxException.ExceptionHandler():
            self._wrappedInstance.waitForCompletion(timeout)
        if (((not self.completed) and (timeout == self.WaitIndefinite)) or
            (self.completed and (self.resultCode != 0))):
            # TODO: This is not the right exception to return.
            raise VirtualBoxException.VirtualBoxException(
                "Task %s did not complete: %s (%d)" % 
                (self.description,
                 self.errorInfo.text,
                 self.resultCode))

