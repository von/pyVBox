# About

This is pyVBOX, a shim layer above the VirtualBox Python API.

Why? Becuase the VirtualBox Python API is somewhat complex and I got
tried of trying to remember all the details of its use. Plus it
changes from release to release and this gives me an abstraction layer
to hide those changes. The software also includes a script,
utils/pyVbox.py, that provides the ability to manipulate VMs (like
VBoxMange).

This code is written to the 3.1 version of VirtualBox (3.1.2
specifically). I have not tried it against any other version.

This software is independently created from VirtualBox and Sun. No
endorsement by Sun or the VirtualBox authors is implied.

Use at your own risk. No support guarenteed, but I'm happy to receive
bug reports or suggestions (open an issue please).

This code is released under the [Apache License, Version
2.0](http://www.apache.org/licenses/LICENSE-2.0.html). I ask you send
me email (von@vwelch.com) if you add any enhancements or just find it
useful (open an issue to report a bug please).

Kudos to [Nikolay Igotti](http://blogs.sun.com/nike/entry/python_api_to_the_virtualbox)
and the vboxshell.py example that comes with the Virtualbox SDK.

The home page for this code is [http://github.com/von/pyVBox](http://github.com/von/pyVBox).

# Goals

 My goal is to provide functionality in the pyVBox library, exposed
through the pyVBox.py script, to do the following:

* Given a VM on a USB drive, register it, boot it and then when it
completes unregister it, all with one command. *DONE:* the 'boot'
command provides this.

* Allow me to backup a running VM. *DONE:* the 'backup' command will
suspend a VM, if needed, and make backup copies of all its attached
hard drives. I'd still like to play around with using snapshops so
that the VM doesn't have to be suspended.

* Allow me to make a copy of a VM with one command. I make what I call
'base VMs' for different OS'es and then when I want a VM for a
specific application I copy the base VM and customize the copy. You
can do this with a combination of VBoxManage and the VirutalBox GUI,
but it's a multi-step process. *In Progress:* I can clone the hard
drives, but need to write the code to clode the VM itself.

One I accomplish the above, I'll probably release 1.0 and then decide
what comes next.

# Installing vboxapi

pyVBox relies on the vboxapi that comes with the VirtualBox SDK from
Sun. You must install it first before trying to use pyVBox.

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

(TODO: Update this to use setup.py)

You will need to include two paths in your PYTHONPATH environent variable:

1. The directory containing the pyVBox module directory. I.e. the
directory in which you found this README.

1. The bindings/xpcom/python/ directory in the VirtualBox SDK distribution. 

For example (assuming your current directory is the one where you
found this README file, and you unpacked the VirtualBox SDK to
/usr/local/virtualbox-sdk):

    setenv PYTHONPATH `pwd`:/usr/local/virtualbox-sdk/bindings/xpcom/python/

# Philosophy

Basically I'm creating wrappers around the VirtualBox Python API that adhere to the OO interface it provides, with a few tweaks:

* Provide reasonable defaults for the VirtualBox methods where it
makes sense. Where 'reasonable' of course means what I consider to be
reasonable.

* Provider for some higher-level functionality. E.g. for a
VirtualMachine I provide a eject() method that does whatever is needed
to unregister the VM.

* In order to make things more intuitive, I move methods to the class
they are associated with. For example, to find a VM you use
VirtualMachine.find() instead of VirtualBox.findMachine(). Again
'intuitive' is what I consider to be intuitive.

For all the classes you should still be able to access any of the
provider VirtualBox methods, attributes, etc. (I.e. I'm subclassing
them, or the equivalent there of).

# Tests

There is a test suite in test/ which you can invoke with:

        python setup.py test

# Other issues

## Python Version on the Mac

On Mac, you need to use python that came with OS or you will get a 'Cannot
find VBoxPython module' error. See [this thread](http://forums.virtualbox.org/viewtopic.php?f=8&t=18969).
