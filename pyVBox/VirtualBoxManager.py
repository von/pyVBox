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
