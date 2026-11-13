"""
Qt binding for PyMOL scripts and plugins. PySide6 only.

Plugins should import Qt from here, not from PySide6 directly.
"""

import os
import sys

if sys.platform == 'win32':
    # Qt6Core.dll imports the ICU that ships with Windows (icuuc.dll, plain
    # names such as ucnv_open). A conda environment with the "icu" package
    # has its own icuuc.dll (names such as ucnv_open_78) earlier on the
    # search path, and QtCore then fails with "The specified procedure could
    # not be found". A DLL that is already loaded wins over the search.
    import ctypes

    try:
        ctypes.WinDLL(os.path.expandvars(r'%SystemRoot%\System32\icuuc.dll'))
    except OSError:
        pass  # no system ICU: let Qt report it

from PySide6 import QtCore, QtGui, QtOpenGLWidgets, QtWidgets

PYQT_NAME = 'PySide6'
os.environ['QT_API'] = 'pyside6'  # qtpy compatibility

# ponytail: Qt5-style names kept for third-party plugins written against them
QtWidgets.QOpenGLWidget = QtOpenGLWidgets.QOpenGLWidget
QtWidgets.QActionGroup = QtGui.QActionGroup
QtWidgets.QAction = QtGui.QAction
QtWidgets.QShortcut = QtGui.QShortcut
QtCore.pyqtSignal = QtCore.Signal
QtCore.pyqtSlot = QtCore.Slot

del os, sys
