#!/usr/bin/env python
"""Unittests for Session class"""

from pyVBoxTest import pyVBoxTest, main
from pyVBox.Session import Session
from pyVBox.VirtualMachine import VirtualMachine

class SessionTests(pyVBoxTest):
    """Tests for Session class"""

    def testCreate(self):
        """Test Session.create() method"""
        s = Session.create()
        self.assertNotEqual(s, None)
