"""Glue functionals for binding pyVBox to vboxapi"""

from HardDisk import HardDisk
from Medium import Medium
from VirtualBoxManager import Constants

# Mappings from DeviceType to pyVBox classes
# For non-implemented classes, map to Medium
DEVICE_TYPE_MAPPINGS = {
    Constants.DeviceType_Null : Medium,
    Constants.DeviceType_Floppy : Medium,
    Constants.DeviceType_DVD : Medium,
    Constants.DeviceType_HardDisk : HardDisk,
    Constants.DeviceType_Network : Medium,
    Constants.DeviceType_USB : Medium,
    Constants.DeviceType_SharedFolder : Medium,
}

def IMediumToMedium(imedium):
    """Given an IMedium instance, return a instance wrapper in the most appropriate class."""
    assert(imedium is not None)
    deviceType = imedium.deviceType
    if DEVICE_TYPE_MAPPINGS.has_key(deviceType):
        cls = DEVICE_TYPE_MAPPINGS[deviceType]
    else:
        # Punt
        cls = Medium
    return cls(imedium)
