"""Wrapper around vboxapi.VirtualBoxManager"""

import vboxapi

from VirtualBoxException import VirtualBoxException

class VirtualBoxManager(vboxapi.VirtualBoxManager):

    def __init__(self, style=None, params=None):
        try:
            vboxapi.VirtualBoxManager.__init__(self, style, params)
        except Exception, e:
            raise VirtualBoxException(e)

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
            return eval("cls._manager.constants." + name)
