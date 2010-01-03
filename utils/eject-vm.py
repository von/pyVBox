#!/usr/bin/env python
"""Eject a VM. Doing whatever it takes to unregister it.
"""

from pyVBox import VirtualBoxException
from pyVBox.VirtualMachine import VirtualMachine

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

def handle_exception(e, msg=None):
    if msg is not None:
        sys.stderr.write(msg + ": ")
    sys.stderr.write(str(e) + "\n")
    
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

    usage = "usage: %prog [options] <vm name>"
    version= "%prog 1.0"
    parser = optparse.OptionParser(usage=usage, version=version)
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

    vmName = args.pop(0)

    try:
        vm = VirtualMachine.find(vmName)
    except VirtualBoxException.VirtualBoxObjectNotFoundException, e:
        message("Virtual machine \"%s\" not found" % vmName)
        return 1
    except Exception, e:
        handle_exception(e, "Unexpected error finding VM '%s'" % vmName)
        return 1

    message("Ejecting %s" % vm)
    try:
        vm.eject()
    except Exception, e:
        handle_exception(e, "Unexpected error ejecting VM '%s'" % vmName)
        return 1
    verboseMsg("Exiting.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
