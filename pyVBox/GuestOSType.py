"""Wrapper around IGuestOSType"""

class GuestOSType:
    def __init__(self, iguestOSType):
        assert(iguestOSType is not None)
        self._guestOSType = iguestOSType

    # Pass any requests for unrecognized attributes or methods onto
    # IGuestOSType object. Doing this this way since I don't kow how
    # to inherit the XPCOM object directly.
    def __getattr__(self, attr):
        return eval("self._guestOSType." + attr)
