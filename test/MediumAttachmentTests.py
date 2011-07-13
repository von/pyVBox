#!/usr/bin/env python
"""Unittests for MediumAttachment"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox import Constants
from pyVBox import Device
from pyVBox import DVD
from pyVBox import MediumAttachment
from pyVBox import StorageController
from pyVBox import VirtualMachine

class MediumAttachmentTests(pyVBoxTest):
    """Test case for MediumAttachment"""

    def testMediumAttachment(self):
        """Test MediumAttachment attributes"""
        machine = VirtualMachine.open(self.testVMpath)
        attachments = machine.getMediumAttachments()
        # Should be one attached DVD drive
        self.assertTrue(len(attachments) == 1)
        for attachment in attachments:
            self.assertNotEqual(None, attachment.controller)
            # attachment.medium should be None in this case for a
            # empty removable devices
            self.assertEqual(None, attachment.medium)
            self.assertNotEqual(None, attachment.port)
            self.assertNotEqual(None, attachment.device)
            self.assertNotEqual(None, attachment.type)
            self.assertTrue(isinstance(attachment.type, Device))
            self.assertTrue(isinstance(attachment.type, DVD))
            self.assertNotEqual(None, attachment.passthrough)
            # bandwidthGroup can apparently be None too

if __name__ == '__main__':
    main()
