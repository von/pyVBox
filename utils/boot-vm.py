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

from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualMachine import VirtualMachine


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

    usage = "usage: %prog [options] <vm settings file>"
    version= "%prog 1.0"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-G", "--gui",
                      dest="type", action="store_const", const="gui",
                      help="Open VM in GUI mode")
    parser.add_option("-H", "--hdd", dest="hdd", action="store",
                      help="mount hdd from FILE", metavar="FILE")
    parser.add_option("-q", "--quiet", dest="verbosityLevel",
                      action="store_const", const=0,
                      help="surpress all messages")
    parser.add_option("-v", "--verbose", dest="verbosityLevel",
                      action="store_const", const=2,
                      help="be verbose")
    parser.add_option("-V", "--vrdp",
                      dest="type", action="store_const", const="vrdp",
                      help="Open VM in VRDP mode")
    parser.set_defaults(type="gui")
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
    vm = VirtualMachine.open(settingsFile)
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
            disk = HardDisk.find(hddPath)
            verboseMsg("Harddisk (%s) already loaded" % disk.getName())
        except:
            pass
        if disk is None:
            verboseMsg("Loading hard drive from %s" % hddPath)
            disk = HardDisk.open(hddPath)
        atexit.register(disk.close)
        vm.attachDevice(disk)
        atexit.register(cleanupVM, vm)
        vm.closeSession()

    verboseMsg("Starting VM in %s mode" % options.type)
    vm.openRemoteSession(type=options.type)
    # Wait until machine is running or we have a race condition
    # where it still might be down when we call waitUntilDown()
    vm.waitUntilRunning()
    
    verboseMsg("VM started. Waiting until power down...")
    vm.waitUntilDown()

    verboseMsg("VM powered down. Cleaning up...")
    vm.closeSession()

    # atexit functions handle all the clean up
    verboseMsg("Exiting.")
    return 0

def cleanupVM(vm):
    verboseMsg("Cleaning up.")
    vm.openSession()
    vm.detachAllDevices()
    vm.closeSession()

if __name__ == "__main__":
    sys.exit(main())
