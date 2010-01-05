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
# Commands

class Command:
    """Base class for all commands."""
    usage = "<command> <arguments"

    @classmethod
    def invoke(cls, args):
        """Invoke the command.

        Should return exit code for program.
        Should be overriden by child class."""
        pass

    registered_commands = {}

    @classmethod
    def register_command(cls, name, command):
        """Register the binding between name and command class"""
        cls.registered_commands[name] = command

    @classmethod
    def lookup_command_by_name(cls, name):
        """Given a name, return associated registered command class"""
        return cls.registered_commands[name]

class BootVMCommand(Command):
    """Boot a virtual machine and eject it after power down"""
    usage = "boot <VM settings file> [<HD files>]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        mode = "gui" # or "vrdp"
        if len(args) < 1:
            raise Exception("Missing virtual machine argument")
        vm = VirtualMachine.open(args.pop(0))
        atexit.register(vm.eject)
        if not vm.registered():
            vm.register()
        vm.openSession()
        for hd in args:
            hd = HardDisk.find(hd)
            vm.attachDevice(hd)
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

Command.register_command("boot", BootVMCommand)

class EjectCommand(Command):
    """Eject a virtual machine"""
    
    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing virtual machine name argument");
        for name in args:
            vm = VirtualMachine.find(name)
            verboseMsg("Ejecting %s" % vm)
            vm.eject()
        return 0

Command.register_command("eject", EjectCommand)

class HelpCommand(Command):
    """Provide help"""

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) > 0:
            for name in args:
                cmd = Command.lookup_command_by_name(name)
                message("%10s: %s" % (name, cmd.__doc__))
        else:
            message("Available commands:")
            for name in Command.registered_commands:
                cmd = Command.lookup_command_by_name(name)
                message("%10s: %s" % (name, cmd.__doc__))

Command.register_command("help", HelpCommand)

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

    try:
        command = Command.lookup_command_by_name(args.pop(0))
        status = command.invoke(args)
    except Exception, e:
        handle_exception(e)
        return 1
    return status

if __name__ == "__main__":
    sys.exit(main())
