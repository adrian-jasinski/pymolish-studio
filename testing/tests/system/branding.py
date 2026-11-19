"""
Own icon and logo (plan step 9): both images load and the icon is square,
the splash keeps the upstream copyright line, the About text has the allowed
slogan and the trademark footnote.
"""

import os
import subprocess
import sys

from pymol import testing


def test_images():
    from pymol.Qt import QtGui

    icons = os.path.expandvars("$PYMOL_DATA/pymol/icons/")
    icon = QtGui.QImage(icons + "pymolish.png")
    assert not icon.isNull()
    assert icon.width() == icon.height()
    assert not QtGui.QImage(icons + "logo.png").isNull()


def test_splash():
    out = subprocess.run(
        [sys.executable, "-m", "pymol", "-ck"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "pymolish-studio, an independent fork." in out
    assert "Copyright (c) Schrodinger, LLC." in out


def test_about():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pmg_qt.pymol_qt_gui import ABOUT_TEXT

    assert "pymolish-studio %s\nBased on PyMOL(TM) technology." in ABOUT_TEXT
    assert "Copyright (C) Schr\xf6dinger, LLC." in ABOUT_TEXT
    assert ABOUT_TEXT.endswith("PyMOL is a trademark of Schrodinger, LLC.")
    assert "sales@" not in ABOUT_TEXT
