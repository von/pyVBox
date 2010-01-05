#!/usr/bin/env python
"""pyVBox utility to control VirtualBox VMs.
"""

import pyVBox.VirtualBoxException
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
#
# Argument parsing functions
#
# These functions take some number of arguments from the commandline
# (args) and return the resulting arguments to be appended to the
# argument list to our command function.
#
# On error they should raise an exception.

def parse_vm_filename(args):
    """Parse one virtual machine by settings filename"""
    try:
        settingsFilename = args.pop(0)
    except Exception, e:
        raise Exception("missing virtual machine filename argument")
    if not os.path.exists(settingsFilename):
        raise Exception("settings file \"%s\" does not exist" %
                        settingsFilename)
    return VirtualMachine.open(settingsFilename)

def parse_vm_name(args):
    """Parse one virtual machine by name"""
    try:
        vmName = args.pop(0)
    except Exception, e:
        raise Exception("missing virtual machine argument")
    return VirtualMachine.find(vmName)

def parse_hdd_filenames(args):
    """Parse zero or more remaining arguments as HDD filenames"""
    disks = []
    for filename in args:
        disks.append(HardDisk.find(filename))
    return disks

def parse_help_arg(args):
    """Parse a help argument"""
    try:
        commandString = args.pop(0)
    except Exception, e:
        return None
    commandArray = command_name_to_array(commandString)
    return commandArray[0]

#----------------------------------------------------------------------
#
# Command functions
#
# These functions take parse command line arguments and perform some
# function.
#
# On normal termination, their return value will be the exit code of
# this program. On error they should raise an exception.
#
# Each function's docstring will be provided to the user as help.

def boot_vm(vm, *hdds):
    """Boot the given virtual machine and eject it after power down.

Usage: boot <vm config file> [<hd files>]"""
    mode = "gui" # or "vrdp"
    atexit.register(vm.eject)
    if vm.registered():
        verboseMsg("Machine \"%s\" already registered."% vm.getName())
    else:
        verboseMsg("Registering %s (%s)" % (vm.getName(), vm.getId()))
        vm.register()

    vm.openSession()
    for hdd in hdds:
        verboseMsg("Attaching HD \"%s\"" % hdd)
        vm.attachDevice(hdd)
    vm.closeSession()

    verboseMsg("Starting VM in %s mode" % mode)
    vm.openRemoteSession(type=mode)
    # Wait until machine is running or we have a race condition
    # where it still might be down when we call waitUntilDown()
    vm.waitUntilRunning()
    
    verboseMsg("VM started. Waiting until power down...")
    vm.waitUntilDown()

    verboseMsg("VM powered down. Cleaning up...")
    vm.closeSession()
    
    # Let atexit clean up
    return 0

def eject_vm(vm):
    """Eject the given virtual machine.

Usage: eject <vm name>"""
    message("Ejecting %s" % vm)
    vm.eject()
    return 0

def help(function=None):
    """Print help for the given command (or list command if no command given)

Usage: help [<command>]"""
    if function is None:
        message("Available commands:")
        for key in CommandMappings:
            docString = CommandMappings[key][0].__doc__
            helpString = docString.split("\n")[0]
            message("%10s: %s" % (key, helpString))
    else:
        message(function.__doc__)

# Mapping of command strings to command functions.  Key is the command
# string given on the commandline.  First value of the array is the
# command function to call.  Subsequent values in the array are
# functions to be called in series to parse the commandline arguments.

CommandMappings = {
    "boot" : [ boot_vm, parse_vm_filename, parse_hdd_filenames ],
    "eject" : [ eject_vm, parse_vm_name ],
    "help" : [ help, parse_help_arg ],
}

def command_name_to_array(string):
    """Map a command name to its associated array"""
    if not CommandMappings.has_key(string):
        raise Exception("unknown command \"%s\"" % string)

    return CommandMappings[string]

#----------------------------------------------------------------------

def main(argv=None):
    global verbosityLevel

    if argv is None:
        argv = sys.argv

    usage = "usage: %prog [options] <command> [<arguments>]"
    version= "%prog 1.0"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-q", "--quiet", dest="verbosityLevel",
                      action="store_const", const=0,
                      help="surpress all messages")
    parser.add_option("-v", "--verbose", dest="verbosityLevel",
                      action="store_const", const=2,
                      help="be verbose")
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("missing command")

    if options.verbosityLevel != None:
        verbosityLevel = options.verbosityLevel
        verboseMsg("Setting verbosity level to %d" % verbosityLevel)

    commandString = args.pop(0)
    commandArray = command_name_to_array(commandString)
    commandFunction = commandArray[0]
    commandArgs = []
    for argumentFunction in commandArray[1:]:
        try:
            newArgs = argumentFunction(args)
            if type(newArgs) is list:
                commandArgs.extend(newArgs)
            else:
                commandArgs.append(newArgs)
        except Exception, e:
            parser.error(str(e))
    commandArgs.extend(args)

    try:
        status = commandFunction(*commandArgs)
    except Exception, e:
        handle_exception(e)
        return 1
    return status

if __name__ == "__main__":
    sys.exit(main())
