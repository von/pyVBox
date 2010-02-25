"""Wrapper around IGuestOSType"""

from Wrapper import Wrapper

class GuestOSType(Wrapper):
   # Properties directly inherited from IMachine
    _passthruProperties = [
        "adapterType",
        "description",
        "familyDescription",
        "familyId",
        "id",
        "is64Bit",
        "recommendedHDD",
        "recommendedIOAPIC",
        "recommendedRAM",
        "recommendedVirtEx",
        "recommendedVRAM",
        ]

    def __init__(self, iguestOSType):
        assert(iguestOSType is not None)
        self._wrappedInstance = iguestOSType
