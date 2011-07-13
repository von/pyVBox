"""Wrapper around IMediumAttachment"""

from Medium import Medium, Device
from Wrapper import Wrapper

class MediumAttachment(Wrapper):
    # Properties directly inherited from IMediumAttachment
    _passthruProperties = [
        "controller",
        "port",
        "device",
        "passthrough",
        "bandwidthGroup",  # Wrap some day
        ]

    _wrappedProperties = [
        ( "medium", Medium ),
        ( "type", Device.from_type ),
        ]

    def __init__(self, mediumAttachment):
        """Return a MediumAttachment around the given IMediumAttachment instance"""
        assert(mediumAttachment is not None)
        self._wrappedInstance = mediumAttachment
        
