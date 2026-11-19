"""
Dialogs built from pmg_qt/forms/*.ui: the form is set up on the dialog
itself, so the dialog has the form's layout and title and opens at least as
large as its content needs.
Headless (offscreen QApplication).
"""

import glob
import os

from pymol import testing


def test_load_form(request):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtCore, QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    import pmg_qt
    from pmg_qt.pymol_qt_gui import PyMOLQtGUI

    class Window(QtWidgets.QWidget):
        load_form = PyMOLQtGUI.load_form

    window = Window()
    # delete it now: a widget alive when Python exits crashes the
    # headless run, and deleteLater needs an event loop
    import shiboken6

    request.addfinalizer(lambda: shiboken6.delete(window))
    forms = os.path.join(os.path.dirname(pmg_qt.__file__), "forms", "*.ui")
    names = sorted(os.path.basename(f)[:-3] for f in glob.glob(forms))
    assert len(names) > 20
    # drawn with fixed positions, no layout; shortcut_menu is not loaded
    fixed = {"change_confirm", "shortcut_menu"}
    for name in names:
        form = window.load_form(name)
        dialog = form._dialog
        assert form is dialog, name  # not a child of the dialog
        assert isinstance(dialog, QtWidgets.QDialog), name
        if name in fixed:
            continue
        assert dialog.layout() is not None, name
        if name != "save_object":  # its caller sets the title
            assert dialog.windowTitle() not in ("", "PyMOL"), name
        # Not shown: a dialog that was on screen crashes the headless
        # run at exit. A form without a size of its own is fitted to
        # its content by Qt when it is shown.
        if dialog.testAttribute(QtCore.Qt.WidgetAttribute.WA_Resized):
            hint = dialog.sizeHint()
            assert dialog.width() >= hint.width(), name
            assert dialog.height() >= hint.height(), name

    # named children are attributes, layouts too
    form = window.load_form("pluginmanager")
    assert isinstance(form.f_installed_layout, QtWidgets.QLayout)
    assert isinstance(form.e_filter, QtWidgets.QLineEdit)
