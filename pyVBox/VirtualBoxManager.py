"""Wrapper around vboxapi.VirtualBoxManager"""

import vboxapi
import VirtualBoxException

class VirtualBoxManager(vboxapi.VirtualBoxManager):

    def __init__(self, style=None, params=None):
        self.__call_deinit = False
        with VirtualBoxException.ExceptionHandler():
            vboxapi.VirtualBoxManager.__init__(self, style, params)
            self.__call_deinit = True

    def __del__(self):
        if self.__call_deinit:
            # Not sure what this does. Copying use from vboxshell.py.
            vboxapi.VirtualBoxManager.deinit(self)

    def waitForEvents(self, timeout=None):
        """Wait for an event.

        Timeout is in miliseconds (I think)."""
        if timeout is None:
            # No timeout
            timeout = 0
        with VirtualBoxException.ExceptionHandler():
            vboxapi.VirtualBoxManager.waitForEvents(self, timeout)


    def getIVirtualBox(self):
        return self.vbox

    def isMSCOM(self):
        """This this a MSCOM manager?"""
        return (self.type == 'MSCOM')

class Constants:
    _manager = VirtualBoxManager()
    
    # Pass any request for unrecognized method or attribute on to
    # XPCOM object. We do this since I don't know how to inherit the
    # XPCOM class directly.
    class __metaclass__(type):
        def __getattr__(cls, name):
            try:
                return getattr(cls._manager.constants, name)
            except AttributeError as e:
                raise AttributeError("%s.%s not found" % (cls.__name__,
                                                          name))
