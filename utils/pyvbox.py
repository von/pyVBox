#!/usr/bin/env python
"""pyVBox utility to control VirtualBox VMs.
"""

import pyVBox.VirtualBoxException
from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualMachine import VirtualMachine

import atexit
import optparse
import os.path
import sys
import traceback

#----------------------------------------------------------------------
#
# Output functions
#

# Default = 1, 0 = quiet, 2 = verbose
verbosityLevel = 1

def errorMsg(msg):
    sys.stderr.write(msg + "\n")

def handle_exception(e, msg=None):
    sys.stderr.write("Error: ")
    if msg is not None:
        sys.stderr.write(msg + ": ")
    sys.stderr.write(str(e) + "\n")
    if verbosityLevel > 1:
        traceback.print_exc()

def message(msg):
    if verbosityLevel > 0:
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()

def verboseMsg(msg):
    if verbosityLevel > 1:
        sys.stdout.write(msg + "\n")
        sys.stdout.flush()


def show_progress(progress, prefix="Progess: "):
    """Given a Progress instance, display progress to user as percent.
    
    The string prefix will precent the percentage.
    If running in quiet mode, displays nothing."""
    if verbosityLevel > 0:
        try:
            while not progress.completed:
                print "%s%2d%%\r" % (prefix, progress.percent),
                sys.stdout.flush()
                # Wait one second
                progress.waitForCompletion(timeout=1000)
        except KeyboardInterrupt:
            print "Interrupted."
        else:
            # Print one last time with carriage return
            print "%s%2d%%" % (prefix, progress.percent),
    else:
        progress.waitForCompletion()

def print_vm(vm):
    """Given a VM instance, display all the information about it."""
    print "VM: %s" % vm.name
    print "  Id: %s" % vm.id
    osType = vm.getOSType()
    print "  OS: %s" % osType.description
    print "  CPU count: %d" % vm.CPUCount
    print "  RAM: %d MB" % vm.memorySize
    print "  VRAM: %d MB" % vm.VRAMSize
    print "  Monitors: %d" % vm.monitorCount
    devices = vm.getAttachedDevices()
    for device in devices:
        print "    Device: %s" % device.name
        print "      Type: %s" % device.getTypeAsString()
        print "      Id: %s" % device.id
        print "      Location: %s" % device.location
        print "      Format: %s" % device.format
        print "      Size: %s" % device.size
    snapshot = vm.getCurrentSnapshot()
    if snapshot:
        print "  Current Snapshot: %s" % snapshot.name

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
    def harddisk(cls, string):
        """Load a harddisk described by string.

        Will open disk if needed."""
        # TODO: Should also support string being UUID
        if HardDisk.isRegistered(string):
            hd = HardDisk.find(string)
        else:
            hd = HardDisk.open(string)
        return hd

    @classmethod
    def register_command(cls, name, command):
        """Register the binding between name and command class"""
        cls.registered_commands[name] = command

    @classmethod
    def lookup_command_by_name(cls, name):
        """Given a name, return associated registered command class"""
        return cls.registered_commands[name]

    @classmethod
    def string_to_size(cls, string):
        """Given a string representing a size return size as long.

        Size is in MB by default. Supported suffixes: MB, GB, TB, PB"""
        import re

        match = re.match("(\d+)(\w\w)?\Z", string)
        if not match:
            raise Exception("Could not parse size \"%s\"" % string)
        number = long(match.group(1))
        suffix = match.group(2)
        if suffix:
            suffix = suffix.lower()
            suffixes = {
                "mb" : 1,
                "gb" : 1024,
                "tb" : 1048576,
                "pb" : 1073741824,
                }
            if not suffixes.has_key(suffix):
                raise Exception("Unrecognized suffix \"%s\"" % suffix)
            number *= suffixes[suffix]
        return number

class AttachCommand(Command):
    """Attach hard disks to a virtual machine"""
    usage = "attach <VM name> <HD files>"
  
    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) < 1:
            raise Exception("Missing virtual machine argument")
        vm = VirtualMachine.find(args.pop(0))
        if len(args) < 1:
            raise Exception("Missing hard disk filenames")
        for hd in args:
            hd = cls.harddisk(hd)
            verboseMsg("Attaching %s" % hd)
            vm.attachDevice(hd)
        return 0

Command.register_command("attach", AttachCommand)

class BackupCommand(Command):
    """Back up a virtual machine to the given directory."""
    usage = "backup <VM name> <target directory>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) < 1:
            raise Exception("Missing virtual machine argument")
        vm = VirtualMachine.find(args.pop(0))
        if len(args) < 1:
            raise Exception("Missing target directory argument")
        targetDir = args.pop(0)
        verboseMsg("Backing up %s to %s" % (vm, targetDir))
        if vm.isRunning():
            verboseMsg("Pausing VM...")
            # Must wait until paused or will have race condition for lock
            # on disks.
            vm.pause(wait=True)
            atexit.register(vm.resume)
        # Todo: Backup settings file in some way.
        # Todo: Want to back up devices than hard drives?
        disks = vm.getHardDrives()
        for disk in disks:
            targetFilename = os.path.join(targetDir, disk.basename())
            # Todo: Need to resolve file already existing here.
            verboseMsg("Backing up disk %s to %s (%d bytes)" % (disk,
                                                                targetFilename,
                                                                disk.size))
            progress = disk.clone(targetFilename, wait=False)
            show_progress(progress)
            # Remove newly created clone from registry
            clone = HardDisk.find(targetFilename)
            clone.close()
                   
Command.register_command("backup", BackupCommand)

class BootVMCommand(Command):
    """Boot a virtual machine and eject it after power down"""
    usage = "boot <VM settings file> [<HD files>]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        mode = "gui" # or "vrdp"
        if len(args) < 1:
            raise Exception("Missing virtual machine filename argument")
        vm = VirtualMachine.open(args.pop(0))
        atexit.register(vm.eject)
        if not vm.isRegistered():
            vm.register()
        for hd in args:
            hd = HardDisk.find(hd)
            vm.attachDevice(hd)
        verboseMsg("Starting VM in %s mode" % mode)
        vm.powerOn(type=mode)
        # Wait until machine is running or we have a race condition
        # where it still might be down when we call waitUntilDown()
        vm.waitUntilRunning()
        verboseMsg("VM started. Waiting until power down...")
        vm.waitUntilDown()
        verboseMsg("VM powered down.")
        # Let atexit clean up
        return 0

Command.register_command("boot", BootVMCommand)

class CloneCommand(Command):
    """Clone a VM. Cloned VM will be registered."""
    usage = "clone <source VM name> <target VM name>"
    
    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) < 1:
            raise Exception("Missing source VM name argument")
        srcVM = VirtualMachine.find(args.pop(0))
        if len(args) < 1:
            raise Exception("Missing target VM name argument")
        targetName = args.pop(0)
        message("Cloning %s to %s" % (srcVM, targetName))
        cloneVM = srcVM.clone(targetName)
        # Now clone and attach disks
        disks = srcVM.getHardDrives()
        for disk in disks:
            # Generate new HD filename by prefixing new VM name.
            # Not the greatest, but not sure what the best way is.
            targetFilename = os.path.join(disk.dirname(),
                                          "%s-%s" % (targetName, disk.name))
            # Todo: Need to resolve file already existing here.
            message("Cloning disk %s to %s (%d bytes)"
                    % (disk,
                       os.path.basename(targetFilename),
                       disk.size))
            progress = disk.clone(targetFilename, wait=False)
            show_progress(progress)
            cloneHD = HardDisk.find(targetFilename)
            message("Attaching %s to %s" % (cloneHD, cloneVM))
            cloneVM.attachDevice(cloneHD)
        return 0

Command.register_command("clone", CloneCommand)

class CloneHDCommand(Command):
    """Clone a hard disk. Cloned disk will be registered."""
    usage = "clonehd <source path> <target path>"
    
    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) < 1:
            raise Exception("Missing source path argument")
        srcHD = cls.harddisk(args.pop(0))
        if len(args) < 1:
            raise Exception("Missing target path argument")
        targetPath = args.pop(0)
        verboseMsg("Cloning %s to %s" % (srcHD, targetPath))
        progress = srcHD.clone(targetPath, wait=False)
        show_progress(progress)
        return 0

Command.register_command("clonehd", CloneHDCommand)

class CreateHDCommand(Command):
    """Create a hard disk"""
    usage = "createhd <size in MB or given suffix> <path>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) < 1:
            raise Exception("Missing size argument")
        size = cls.string_to_size(args.pop(0))
        if len(args) < 1:
            raise Exception("Missing path argument")
        path = args.pop(0)
        verboseMsg("Creating Hard Disk at %s with size %d" % (path, size))
        HardDisk.createWithStorage(path, size)
        return 0

Command.register_command("createhd", CreateHDCommand)

class DelSnapshotCommand(Command):
    """Delete the current snapshot"""
    usage = "delsnapshot <VM name>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing VM name")
        vm = VirtualMachine.find(args.pop(0))
        snapshot = vm.getCurrentSnapshot()
        progress = vm.deleteSnapshot(snapshot, wait=False)
        show_progress(progress)

Command.register_command("delsnapshot", DelSnapshotCommand)

class EjectCommand(Command):
    """Eject a virtual machine"""
    usage = "boot <VM name>"

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
    usage = "help [<commands>]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) > 0:
            for name in args:
                try:
                    cmd = Command.lookup_command_by_name(name)
                    message("%10s: %s" % (name, cmd.__doc__))
                    message("%10s  usage: %s" % ("", cmd.usage))
                except KeyError, e:
                    message("Unknown command '%s'" % name)
        else:
            message("Available commands:")
            commands = Command.registered_commands.keys()
            commands.sort()
            # What's the length of the longer command name?
            longestNameLen = max(map(len, commands))
            for name in commands:
                cmd = Command.lookup_command_by_name(name)
                message("%*s: %s" % (longestNameLen, name, cmd.__doc__))

Command.register_command("help", HelpCommand)

class OSTypesCommand(Command):
    """Display all the available guest OS types"""
    usage = "guestOSTypes"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        osTypes = VirtualBox().getGuestOSTypes()
        for ostype in osTypes:
            print "%s (%s)" % (ostype.description, ostype.id)
        return 0

Command.register_command("guestOSTypes", OSTypesCommand)

class PauseCommand(Command):
    """Pause a running VM"""
    usage = "pause <VM name>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing virtual machine name argument");
        vm = VirtualMachine.find(args.pop(0))
        vm.pause()
        return 0

Command.register_command("pause", PauseCommand)

class RegisterCommand(Command):
    """Register a VM"""
    usage = "register <VM settings filename> [<VM settings filename>...]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing virtual machine filename argument");
        for filename in args:
            vm = VirtualMachine.open(args.pop(0))
            if vm.isRegistered():
                errorMsg("VM \"%s\" is already registered." % vm)
            else:
                verboseMsg("Registering VM %s" % vm)
                vm.register()
        return 0

Command.register_command("register", RegisterCommand)

class ResumeCommand(Command):
    """Resume a paused VM"""
    usage = "resume <VM name>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing virtual machine name argument");
        vm = VirtualMachine.find(args.pop(0))
        vm.resume()
        return 0

Command.register_command("resume", ResumeCommand)

class SnapshotCommand(Command):
    """Snapshot a VM"""
    usage = "snapshot <VM name> <snapshot name> [<snapshot description>]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing VM name")
        vm = VirtualMachine.find(args.pop(0))
        if len(args) == 0:
            raise Exception("Missing snapshot name")
        name = args.pop(0)
        description = None
        if len(args) > 0:
            description = args.pop(0)
        vm.takeSnapshot(name, description)

Command.register_command("snapshot", SnapshotCommand)

class StartCommand(Command):
    """Start a VM"""
    usage = "start <VM name>"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        mode = "gui"
        if len(args) == 0:
            raise Exception("Missing virtual machine name argument");
        vm = VirtualMachine.find(args.pop(0))
        vm.powerOn(type=mode)

Command.register_command("start", StartCommand)

class UnregisterCommand(Command):
    """Unregister a VM"""
    usage = "unregister <VM name> [<VM name>...]"

    @classmethod
    def invoke(cls, args):
        """Invoke the command. Return exit code for program."""
        if len(args) == 0:
            raise Exception("Missing virtual machine name argument");
        for filename in args:
            vm = VirtualMachine.find(args.pop(0))
            if vm.isRegistered():
                verboseMsg("Unregistering VM %s" % vm)
                vm.unregister()
            else:
                errorMsg("VM \"%s\" is not registered." % vm)
        return 0

Command.register_command("unregister", UnregisterCommand)

class VMCommand(Command):
    """Display information about one or more VMs"""
    usage = "vm [<vm names>]"

    @classmethod
    def invoke(cls, args):
        if len(args) == 0:
            vms = VirtualMachine.getAll()
            verboseMsg("Registered VMs:")
            for vm in vms:
                print "\t%s" % vm
        else:
            for vmName in args:
                vm = VirtualMachine.find(vmName)
                print_vm(vm)

Command.register_command("vm", VMCommand)

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
    commandStr = args.pop(0)

    if options.verbosityLevel != None:
        verbosityLevel = options.verbosityLevel
        verboseMsg("Setting verbosity level to %d" % verbosityLevel)

    try:
        command = Command.lookup_command_by_name(commandStr)
    except Exception, e:
        parser.error("Unrecognized command \"%s\"" % commandStr)
        return 1

    try:
        status = command.invoke(args)
    except Exception, e:
        handle_exception(e)
        return 1
    return status

if __name__ == "__main__":
    sys.exit(main())
