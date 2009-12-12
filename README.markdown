# About

This is pyVBOX, a shim layer above the VirtualBox Python API.

Why? Becuase the VirtualBox Python API is somewhat complex and I got
tried of trying to remember all the details of its use. Plus it
changes from release to release and this gives me an abstraction layer
to hide those changes.

This code is written to the 3.1 version of VirtualBox.

This software is independently created from VirtualBox and Sun. No
endorsement by Sun or the VirtualBox authors is implied.

This code is far from complete. Use at your own risk. No support
guarenteed, but I'm happy to receive bug reports or suggestions (open
an issue please).

This code is released under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).

For examples of use, see test/ and utils/

Kudos to [Nikolay Igotti](http://blogs.sun.com/nike/entry/python_api_to_the_virtualbox)
and the vboxshell.py example that comes with the Virtualbox SDK.

# Installing vboxapi

1. Download and install VirtualBox from [the VirtualBox downloads page](http://www.virtualbox.org/wiki/Downloads).

1. Download the VirtualBox SDK from [the VirtualBox downloads page](http://www.virtualbox.org/wiki/Downloads).

1. Unzip the SDK somewhere

1. cd sdk/installer

1. Set your VBOX_INSTALL_PATH via:

        # VBOXMANAGE_PATH=`which VBoxManage`
        # export VBOX_INSTALL_PATH=`basename $VBOXMANAGE_PATH`

1. Install:

        # python vboxapisetup.py install

# Setting up your environment

You will need to include two paths in your PYTHONPATH environent variable:

1. The pyVBox directory in pyVBox

1. The bindings/xpcom/python/ directory in the VirtualBox SDK distribution.

For example:

    setenv PYTHONPATH `pwd`/pyVBox/:/usr/local/virtualbox/sdk/bindings/xpcom/python/

# Other issues

## Python Version on the Mac

On Mac, you need to use python that came with OS or you will get a 'Cannot
find VBoxPython module' error. See [this thread](http://forums.virtualbox.org/viewtopic.php?f=8&t=18969).
