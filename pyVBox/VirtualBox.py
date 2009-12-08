"""Wrapper around IVirtualBox

This is not used at this time."""

from VirtualBoxException import VirtualBoxException
from VirtualBoxManager import VirtualBoxManager

import os.path

class VirtualBox:
    def __init__(self):
        self._manager = VirtualBoxManager()
        self._vbox = self._manager.getIVirtualBox()


