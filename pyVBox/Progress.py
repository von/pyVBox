"""Wrapper around IProgress object"""

import VirtualBoxException

class Progress:
    WaitIndefinite = -1

    def __init__(self, progress):
        """Return a Progress wrapper around given IProgress instance"""
        self._progress = progress

    # Pass any requests for unrecognized attributes or methods onto
    # IProgress object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._progress." + attr)

    def waitForCompletion(self, timeout = None):
        """Waits until the task is done (including all sub-operations).

Timeout is in milliseconds. specify None for an indefinite wait."""
        if timeout is None:
            timeout = self.WaitIndefinite
        try:
            self._progress.waitForCompletion(timeout)
        except Exception, e:
            VirtualBoxException.handle_exception(e)
            raise
        if not self._progress.completed:
            # TODO: This is obly an error if we were waiting indefinitely?
            # TODO: This is not the right exception to return.
            raise VirtualBoxException.VirtualBoxException(
                "Error starting VM: %s (%d)" % 
                (self._progress.errorInfo.text,
                 self._progress.resultCode))

