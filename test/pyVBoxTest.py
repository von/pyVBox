"""Base class for all pyVBox unittests."""

import os
import unittest

from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualMachine import VirtualMachine

class pyVBoxTest(unittest.TestCase):
    """Base class for all pyVBox unittests."""
    testHDpath = "test/appliances/TestHD.vdi"
    cloneHDpath = "test/appliances/CloneHD.vdi"
    bogusHDpath = "/bogus/path"
    testVMpath = "test/appliances/TestVM.xml"
    testVMname = "TestVM"
    bogusVMpath = "/bogus/path"

    def setUp(self):
        self._cleanup()

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        """Unregister test HD and VM if they are registered."""
        # Do machine first to detach any HDs
        try:
            machine = VirtualMachine.find(self.testVMname)
            machine.eject()
        except:
            pass
        try:
            harddisk = HardDisk.find(self.testHDpath)
            harddisk.close()
        except:
            pass
        try:
            clonedisk = HardDisk.find(self.cloneHDpath)
            clonedisk.close()
        except:
            pass
        try:
            os.remove(self.cloneHDpath)
        except:
            pass
    
def main():
    """Run tests."""
    unittest.main()
