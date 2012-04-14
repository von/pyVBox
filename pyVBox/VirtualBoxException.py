"""Basic exceptions for pyVBox."""

import xpcom

from contextlib import contextmanager
import sys

######################################################################
# Constants from IDL file. I can't find a way to programmatically
# get at these through the python API.

# Object corresponding to the supplied arguments does not exist.
VBOX_E_OBJECT_NOT_FOUND = 0x80BB0001

# Current virtual machine state prevents the operation.
VBOX_E_INVALID_VM_STATE = 0x80BB0002

# Virtual machine error occurred attempting the operation.
VBOX_E_VM_ERROR = 0x80BB0003

# File not accessible or erroneous file contents.
VBOX_E_FILE_ERROR = 0x80BB0004

# Runtime subsystem error.
VBOX_E_IPRT_ERROR = 0x80BB0005

# Pluggable Device Manager error.
VBOX_E_PDM_ERROR = 0x80BB0006

# Current object state prohibits operation.
VBOX_E_INVALID_OBJECT_STATE = 0x80BB0007

# Host operating system related error.
VBOX_E_HOST_ERROR = 0x80BB0008

# Requested operation is not supported.
VBOX_E_NOT_SUPPORTED = 0x80BB0009

# Invalid XML found.
VBOX_E_XML_ERROR = 0x80BB000A

# Current session state prohibits operation.
VBOX_E_INVALID_SESSION_STATE = 0x80BB000B

# Object being in use prohibits operation. 
VBOX_E_OBJECT_IN_USE = 0x80BB000C

######################################################################
# Constants I've found experimentally. Names are of my own creation.

# Returned from Progress.waitForCompletion()
VBOX_E_ERROR_ABORT = 0x80004004 

# Returned when VirtualMachine.open() method doesn't find a file
VBOX_E_FILE_NOT_FOUND = 0x80004005

# Thrown if a create VirtualMachine is invalid in some way 
XPCOM_E_OBJECT_NOT_READY = 0x80070005

# Returned if VirtualMachine.memorySize is set out of range
XPCOM_E_INVALID_ARGUMENT = 0x80070057

# "Call to remote object failed"
NS_ERROR_CALL_FAILED = 0x800706be

# Returned when getting machine attribute from closed session
VBOX_E_SESSION_CLOSED = 0x8000ffff

######################################################################

class VirtualBoxException(Exception):
    """Base exception for pyVBox exceptions."""
    pass

class VirtualBoxObjectNotFoundException(VirtualBoxException):
    """Object corresponding to the supplied arguments does not exist."""
    errno = VBOX_E_OBJECT_NOT_FOUND

class VirtualBoxInvalidVMStateException(VirtualBoxException):
    """Current virtual machine state prevents the operation."""
    errno = VBOX_E_INVALID_VM_STATE

class VirtualBoxVMError(VirtualBoxException):
    """Virtual machine error occurred attempting the operation."""
    errno = VBOX_E_VM_ERROR

class VirtualBoxFileError(VirtualBoxException):
    """File not accessible or erroneous file contents."""
    errno = VBOX_E_FILE_ERROR

class VirtualBoxRuntimeSubsystemError(VirtualBoxException):
    """Runtime subsystem error."""
    errno = VBOX_E_IPRT_ERROR

class VirtualBoxPluggableDeviceManagerError(VirtualBoxException):
    """Pluggable Device Manager error."""
    errno = VBOX_E_PDM_ERROR

class VirtualBoxInvalidObjectState(VirtualBoxException):
    """Current object state prohibits operation."""
    errno = VBOX_E_INVALID_OBJECT_STATE

class VirtualBoxHostError(VirtualBoxException):
    """Host operating system related error."""
    errno = VBOX_E_HOST_ERROR

class VirtualBoxNotSupportException(VirtualBoxException):
    """Requested operation is not supported."""
    errno = VBOX_E_NOT_SUPPORTED

class VirtualBoxInvalidXMLError(VirtualBoxException):
    """Invalid XML found."""
    errno = VBOX_E_XML_ERROR

class VirtualBoxInvalidSessionStateException(VirtualBoxException):
    """Current session state prohibits operation."""
    errno = VBOX_E_INVALID_SESSION_STATE

class VirtualBoxObjectInUseException(VirtualBoxException):
    """Object being in use prohibits operation."""
    errno = VBOX_E_OBJECT_IN_USE

class VirtualBoxFileNotFoundException(VirtualBoxException):
    """File not found."""
    errno = VBOX_E_FILE_NOT_FOUND

class VirtualBoxObjectNotReady(VirtualBoxException):
    """Object not read."""
    errno = XPCOM_E_OBJECT_NOT_READY

class VirtualBoxInvalidArgument(VirtualBoxException):
    """Invalid argument."""
    errno = XPCOM_E_INVALID_ARGUMENT

class VirtualBoxOperationAborted(VirtualBoxException):
    """Operation aborted."""
    errno = VBOX_E_ERROR_ABORT

class VirtualBoxCallFailed(VirtualBoxException):
    """Call to remot object failed."""
    errno = NS_ERROR_CALL_FAILED

# Mappings from VirtualBox error numbers to pyVBox classes
EXCEPTION_MAPPINGS = {
    VBOX_E_OBJECT_NOT_FOUND      : VirtualBoxObjectNotFoundException,
    VBOX_E_INVALID_VM_STATE      : VirtualBoxInvalidVMStateException,
    VBOX_E_VM_ERROR              : VirtualBoxVMError,
    VBOX_E_FILE_ERROR            : VirtualBoxFileError,
    VBOX_E_IPRT_ERROR            : VirtualBoxRuntimeSubsystemError,
    VBOX_E_PDM_ERROR             : VirtualBoxPluggableDeviceManagerError,
    VBOX_E_INVALID_OBJECT_STATE  : VirtualBoxInvalidObjectState,
    VBOX_E_HOST_ERROR            : VirtualBoxHostError,
    VBOX_E_NOT_SUPPORTED         : VirtualBoxNotSupportException,
    VBOX_E_XML_ERROR             : VirtualBoxInvalidXMLError,
    VBOX_E_INVALID_SESSION_STATE : VirtualBoxInvalidSessionStateException,
    VBOX_E_OBJECT_IN_USE         : VirtualBoxObjectInUseException,
    VBOX_E_ERROR_ABORT           : VirtualBoxOperationAborted,
    VBOX_E_FILE_NOT_FOUND        : VirtualBoxFileNotFoundException,
    XPCOM_E_OBJECT_NOT_READY     : VirtualBoxObjectNotReady,
    XPCOM_E_INVALID_ARGUMENT     : VirtualBoxInvalidArgument,
    VBOX_E_SESSION_CLOSED        : VirtualBoxInvalidVMStateException,
    NS_ERROR_CALL_FAILED         : VirtualBoxCallFailed,
    }


class ExceptionHandler:
    """Context manager to handle any VirtualBox exceptions.

Since the VirtualBox Python API raises normal exceptions, this
function determines if an exception is related to VirtualBox and, if
so, raises its pyVBox equivalent.

Otherwise, it does nothing.

The function should be used as follows:

    with vbox_exception_handler():
        # Some VirtualBox code here
"""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if issubclass(exc_type, xpcom.Exception):  # Also True if equal
                errno, message = exc_val
                exception_class = None
                if EXCEPTION_MAPPINGS.has_key(errno):
                    exception_class = EXCEPTION_MAPPINGS[errno]
                else:
                    # Convert errno from exception to constant value from
                    # IDL file.  I don't understand why this is needed,
                    # determined experimentally.  ex.errno is a negative
                    # value (e.g. -0x7f44ffff), this effectively takes its
                    # aboslute value and subtracts it from 0x100000000.
                    errno = 0x100000000 + errno
                    if EXCEPTION_MAPPINGS.has_key(errno):
                        exception_class = EXCEPTION_MAPPINGS[errno]
                if exception_class:
                    # Reraise with original stacktrace and instance
                    # information, but with new class.  Note that one
                    # cannot hide the current line from the traceback. See
                    # http://stackoverflow.com/questions/6410764/raising-exceptions-without-raise-in-the-traceback
                    raise exception_class, message
            # Else we don't have or don't recognize the errno, return
            # and allow context manager to re-raise exception.
        return False

