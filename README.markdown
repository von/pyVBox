# About

This is pyVBOX, a shim layer above the VirtualBox Python API.

Why? Becuase the VirtualBox Python API is somewhat complex and I got
tried of trying to remember all the details of its use. Plus it
changes from release to release and this gives me an abstraction layer
to hide those changes.

This code is written to the 3.1 version of VirtualBox.

This code is far from complete. Use at your own risk.

No support guarenteed, but I'm happy to receive bug reports or
suggestions (open an issue please).

# Installing vboxapi

1. Download and install VirtualBox from  http://www.virtualbox.org/wiki/Downloads

1. Download the VirtualBox SDK from http://www.virtualbox.org/wiki/Downloads

1. Unzip the SDK somewhere

1. cd sdk/installer

1. Set your VBOX_INSTALL_PATH via:

        # VBOXMANAGE_PATH=`which VBoxManage`
        # export VBOX_INSTALL_PATH=`basename $VBOXMANAGE_PATH`

1. Install:

        # python vboxapisetup.py install

# Other issues

## Python Version on the Mac

On Mac, need to use python that came with OS or you will get a "Cannot
find VBoxPython module" error. See:
http://forums.virtualbox.org/viewtopic.php?f=8&t=18969
