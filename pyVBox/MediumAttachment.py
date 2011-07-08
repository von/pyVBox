"""Wrapper around IMediumAttachment"""

from Medium import Medium
from Wrapper import Wrapper

class MediumAttachment(Wrapper):
    # Properties directly inherited from IMediumAttachment
    _passthruProperties = [
        "controller",
        "port",
        "device",
        "type",
        "passthrough",
        "bandwidthGroup",  # Wrap some day
        ]

    def __init__(self, mediumAttachment):
        """Return a MediumAttachment around the given IMediumAttachment instance"""
        assert(mediumAttachment is not None)
        self._wrappedInstance = mediumAttachment

    def __getattr__(self, attr):
        if attr == "medium":
            imedium = getattr(self._wrappedInstance, attr)
            if imedium:
                return Medium(imedium)
            else:
                return None
        else:
            return Wrapper.__getattr__(self, attr)
            
        
