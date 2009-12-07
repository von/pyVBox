#!/usr/bin/env python
"""Register a VM, boot it, wait for completion and unregister it.

Add a virtual machine to Virtualbox's inventory (attaching a hard
drive in the process), boot the VM, wait for it to power down and then
remove it.

Intended for VMs on removable drives.

Note that the Virtual Box GUI apparently keeps either the xml or hard
drive file open even after they have been unregistered. This may cause
problems unmounting the removable drive until the VBox program is
quit.
"""

from pyVBox.VirtualBox import VirtualBox

import atexit
import optparse
import os.path
import sys

#----------------------------------------------------------------------
#
# Output functions
#

# Default = 1, 0 = quiet, 2 = verbose
verbosityLevel = 1

def errorMsg(msg):
    sys.stderr.write(msg + "\n")

def message(msg):
    if verbosityLevel > 0:
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()

def verboseMsg(msg):
    if verbosityLevel > 1:
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()

#----------------------------------------------------------------------

def main(argv=None):
    global verbosityLevel

    if argv is None:
        argv = sys.argv

    vbox = VirtualBox()

    usage = "usage: %prog [options] <vm settings file>"
    version= "%prog 1.0"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-H", "--hdd", dest="hdd", action="store",
                      help="mount hdd from FILE", metavar="FILE")
    parser.add_option("-q", "--quiet", dest="verbosityLevel",
                      action="store_const", const=0,
                      help="surpress all messages")
    parser.add_option("-v", "--verbose", dest="verbosityLevel",
                      action="store_const", const=2,
                      help="be verbose")
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")

    if options.verbosityLevel != None:
        verbosityLevel = options.verbosityLevel
        verboseMsg("Setting verbosity level to %d" % verbosityLevel)

    settingsFile = args.pop(0)
    if not os.path.exists(settingsFile):
        parser.error("settings file does not exist")

    verboseMsg("Loading VM from \"%s\"" % settingsFile)
    vm = vbox.openMachine(settingsFile)
    if vm.registered():
        verboseMsg("Machine \"%s\" already registered."% vm.getName())
    else:
        verboseMsg("Registering %s (%s)" % (vm.getName(), vm.getId()))
        vm.register()
    # XXX Unregister on exit even if already registered?
    atexit.register(vm.unregister)

    hddPath = options.hdd
    if hddPath:
        vm.openSession()
        atexit.register(vm.closeSession)
        disk = None
        try:
            disk = vbox.findHardDisk(hddPath)
            verboseMsg("Harddisk (%s) already loaded" % disk.getName())
        except:
            pass
        if disk is None:
            verboseMsg("Loading hard drive from %s" % hddPath)
            disk = vbox.openHardDisk(hddPath)
        atexit.register(disk.close)
        vm.attachDevice(disk)
        atexit.register(cleanupVM, vm)
        vm.closeSession()

    verboseMsg("Starting VM")
    vm.openRemoteSession()
    verboseMsg("VM started")

    # XXX We really should wait here until user powers down machine
    # and then clean up. What follows is a hack where we wait 5
    # sections and then just shut it down.
    verboseMsg("Sleeping...")
    from time import sleep
    sleep(5)

    verboseMsg("Powering down...")
    vm.powerOff()
    vm.closeSession()

    # Sleep to let system power off. Again, should actually monitor
    # state.
    sleep(5)

    # atexit functions handle all the clean up
    verboseMsg("Exiting.")
    return 0

def cleanupVM(vm):
    if not vm.hasSession():
        vm.openSession()
    vm.detachAllDevices()
    vm.closeSession()

if __name__ == "__main__":
    sys.exit(main())
