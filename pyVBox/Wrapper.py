import VirtualBoxException

class Wrapper(object):
    """Base class for wrappers around VirtualBox XPCOM-based objects.

    This class is not usable by itself, it must be inherited by a child
    class and certain properties set:

    _wrappedInstance should be the wrapped instance.

    _passthruProperties is the directly exposed properties (as
    strings) of the wrapped class. These properties can be retrieved or
    set, but not deleted. In general, these should be properties that are
    native Python types, other properties should be wrapped.

    _wrappedProperties is a list of tuples. When the attribute named
    by the first element is accessed, function or class in the second
    element is invoked with the property as an argument and the result is
    returned.

    Utilizing this class since I don't kow how to inherit the XPCOM
    classes directly.
    """
    _wrappedInstance = None
    _passthruProperties = []
    _wrappedProperties = []

    def __getattr__(self, attr):
        if self._wrappedInstance:
            if attr in self._passthruProperties:
                with VirtualBoxException.ExceptionHandler():
                    return getattr(self._wrappedInstance, attr)
            for prop, func in self._wrappedProperties:
                if prop == attr:
                    with VirtualBoxException.ExceptionHandler():
                        value = getattr(self._wrappedInstance, attr)
                    return func(value) if value else None
        raise AttributeError("Unrecognized attribute '%s'" % attr)

    def __setattr__(self, attr, value):
        if self._wrappedInstance and (attr in self._passthruProperties):
            with VirtualBoxException.ExceptionHandler():
                setattr(self._wrappedInstance, attr, value)
        self.__dict__[attr] = value

    def __delattr__(self, attr):
       if self._wrappedInstance and (attr in self._passthruProperties):
           with VirtualBoxException.ExceptionHandler():
               raise AttributeError("Cannot delete attribute '%s'" % attr)
       del self.__dict__[attr]

            
