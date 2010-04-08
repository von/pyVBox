"""Base class for all pyVBox unittests."""

import os
import os.path
import shutil
import unittest

from pyVBox.HardDisk import HardDisk
from pyVBox.VirtualBox import VirtualBox
from pyVBox.VirtualMachine import VirtualMachine

class pyVBoxTest(unittest.TestCase):
    """Base class for all pyVBox unittests."""
    # VM and HD for testing
    # These are version controlled, we will make a copy before
    # altering them.
    testHDsrc = "test/appliances/TestHD.vdi"
    testVMsrc = "test/appliances/TestVM.xml"
    testVMname = "TestVM"

    # Our testing grounds
    testPath = "test/tmp/"
    
    # setUp() will create these copies of the sources above
    testHDpath = "test/tmp/TestHD.vdi"
    testVMpath = "test/tmp/TestVM.xml"

    # HD clone we will create during testing
    cloneHDpath = "test/tmp/CloneHD.vdi"

    # Paths for testing failure
    bogusHDpath = "/bogus/path"
    bogusVMpath = "/bogus/path"

    def setUp(self):
        if not os.path.exists(self.testPath):
            os.mkdir(self.testPath)
        shutil.copy(self.testVMsrc, self.testVMpath)
        shutil.copy(self.testHDsrc, self.testHDpath)
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
