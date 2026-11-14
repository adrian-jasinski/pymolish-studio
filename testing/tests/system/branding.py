"""
Own icon and logo (plan step 9): both images load and the icon is square,
the splash keeps the upstream copyright line, the About text has the allowed
slogan and the trademark footnote.
"""

import os
import subprocess
import sys

from pymol import testing


class TestBranding(testing.PyMOLTestCase):
    def test_images(self):
        from pymol.Qt import QtGui

        icons = os.path.expandvars("$PYMOL_DATA/pymol/icons/")
        icon = QtGui.QImage(icons + "pymolish.png")
        self.assertFalse(icon.isNull())
        self.assertEqual(icon.width(), icon.height())
        self.assertFalse(QtGui.QImage(icons + "logo.png").isNull())

    def test_splash(self):
        out = subprocess.run(
            [sys.executable, "-m", "pymol", "-ck"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertIn("pymolish-studio, an independent fork.", out)
        self.assertIn("Copyright (c) Schrodinger, LLC.", out)

    def test_about(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from pmg_qt.pymol_qt_gui import ABOUT_TEXT

        self.assertIn("pymolish-studio %s\nBased on PyMOL(TM) technology.", ABOUT_TEXT)
        self.assertIn("Copyright (C) Schr\xf6dinger, LLC.", ABOUT_TEXT)
        self.assertTrue(
            ABOUT_TEXT.endswith("PyMOL is a trademark of Schrodinger, LLC.")
        )
        self.assertNotIn("sales@", ABOUT_TEXT)
