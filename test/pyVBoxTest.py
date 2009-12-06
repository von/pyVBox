"""Base class for all pyVBox unittests."""

import unittest

from pyVBox.VirtualBox import VirtualBox

class pyVBoxTest(unittest.TestCase):
    """Base class for all pyVBox unittests."""
    testHDpath = "appliances/TestHD.vdi"
    bogusHDpath = "/bogus/path"
    testVMpath = "appliances/TestVM.xml"
    bogusVMpath = "/bogus/path"

    def setUp(self):
        self.vbox = VirtualBox()
        self._cleanup()

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        # Unregister test HD and VM if they are registered
        # Do machine first to detach any HDs
        machine = self.vbox.openMachine(self.testVMpath)
        if machine.registered():
            vm = machine.openSession()
            vm.detachAllDevices()
            vm.closeSession()
            machine.unregister()
        if self.vbox.isHardDiskOpen(self.testHDpath):
            harddisk = self.vbox.findHardDisk(self.testHDpath)
            harddisk.close()

    
def main():
    """Run tests."""
    unittest.main()
