"""Functions for manipulation UUIDs"""

import uuid

def isUUID(s):
    """Is the given string a UUID?"""
    try:
        uuid.UUID(s)
    except ValueError:
        return False
    else:
        return True
