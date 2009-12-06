"""Constants for VirtualBox interface"""

from vboxapi import VirtualBoxManager

class Constants:
    style = None
    params = None
    manager = VirtualBoxManager(style, params)

    class __metaclass__(type):
        def __getattr__(cls, name):
            return eval("cls.manager.constants." + name)

