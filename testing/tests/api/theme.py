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

    def test_prefer_x11_on_wsl(self):
        from pmg_qt import theme

        env = {"WSL_DISTRO_NAME": "Ubuntu", "DISPLAY": ":0"}
        theme.prefer_x11_on_wsl(env)
        self.assertEqual(env["QT_QPA_PLATFORM"], "xcb;wayland")
        env = {"WSL_DISTRO_NAME": "Ubuntu", "DISPLAY": ":0", "QT_QPA_PLATFORM": "w"}
        theme.prefer_x11_on_wsl(env)
        self.assertEqual(env["QT_QPA_PLATFORM"], "w")  # the user's choice wins
        for env in ({"DISPLAY": ":0"}, {"WSL_DISTRO_NAME": "Ubuntu"}):
            theme.prefer_x11_on_wsl(env)
            self.assertNotIn("QT_QPA_PLATFORM", env)

    def test_syntax_colors_readable_on_dark(self):
        from pmg_qt.syntax import readable

        for name in ("blue", "darkBlue", "black", "brown", "darkGreen"):
            self.assertGreaterEqual(readable(name, True).lightness(), 170)
            self.assertLess(readable(name, False).lightness(), 170)

    def test_offer_ui_scale(self):
        from unittest import mock
        from pmg_qt import theme

        def offer(width, ratio, saved=False):
            screen = mock.Mock()
            screen.devicePixelRatio.return_value = ratio
            screen.geometry.return_value.width.return_value = width
            app = mock.Mock()
            app.primaryScreen.return_value = screen
            Yes = theme.QtWidgets.QMessageBox.StandardButton.Yes
            with (
                mock.patch.object(theme, "_settings") as settings,
                mock.patch.object(theme, "set_ui_scale") as save,
                mock.patch.object(
                    theme.QtWidgets.QMessageBox, "question", return_value=Yes
                ),
                mock.patch.dict(os.environ),
            ):
                os.environ.pop("QT_SCALE_FACTOR", None)
                settings.return_value.contains.return_value = saved
                theme.offer_ui_scale(app)
                return save.call_args

        self.assertEqual(offer(2560, 1), mock.call(1.5))
        self.assertIsNone(offer(1920, 1))  # ordinary screen
        self.assertIsNone(offer(2560, 2))  # OS already scales
        self.assertIsNone(offer(2560, 1, saved=True))  # asked before
