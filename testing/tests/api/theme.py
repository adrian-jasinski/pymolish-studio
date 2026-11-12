"""
Dark palette has readable text on all groups and apply() switches back.
The saved UI scale reaches Qt unless the user exported their own.
Headless (offscreen QApplication).
"""

import os

from pymol import testing


class TestTheme(testing.PyMOLTestCase):
    def test_palette(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from pymol.Qt import QtWidgets
        from pmg_qt import theme

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        p = theme.dark_palette()
        for group in (theme.Group.Active, theme.Group.Inactive, theme.Group.Disabled):
            bg = p.color(group, theme.Role.Window).lightness()
            fg = p.color(group, theme.Role.WindowText).lightness()
            self.assertGreater(fg - bg, 60)
        theme.apply(app, True)
        self.assertLess(app.palette().window().color().lightness(), 100)
        menu = QtWidgets.QMenu()
        self.assertLess(menu.palette().window().color().lightness(), 100)
        theme.apply(app, False)
        self.assertGreater(app.palette().window().color().lightness(), 150)
        self.assertEqual(app.style().objectName(), "fusion")

    def test_ui_scale(self):
        from unittest import mock
        from pmg_qt import theme

        with mock.patch.object(theme, "ui_scale", return_value=1.5):
            env = {}
            theme.apply_ui_scale(env)
            self.assertEqual(env, {"QT_SCALE_FACTOR": "1.5"})
            env = {"QT_SCALE_FACTOR": "2"}
            theme.apply_ui_scale(env)
            self.assertEqual(env["QT_SCALE_FACTOR"], "2")
        with mock.patch.object(theme, "ui_scale", return_value=1.0):
            env = {}
            theme.apply_ui_scale(env)
            self.assertEqual(env, {})

    def test_syntax_colors_readable_on_dark(self):
        from pmg_qt.syntax import readable

        for name in ("blue", "darkBlue", "black", "brown", "darkGreen"):
            self.assertGreaterEqual(readable(name, True).lightness(), 170)
            self.assertLess(readable(name, False).lightness(), 170)
