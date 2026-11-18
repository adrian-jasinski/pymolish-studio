"""
Action toolbar: selection mode menu and label, rock state, zoom, presets
menu, panel and More entries, an icon on every button, the palette menu, the
background menu, the UI scale menu.
Headless (offscreen QApplication).
"""

import os
from collections import defaultdict

from pymol import cmd, testing


class TestActionToolbar(testing.PyMOLTestCase):
    def setUp(self):
        super().setUp()
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from pymol.Qt import QtWidgets

        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_toolbar(self):
        from pmg_qt.action_toolbar import ActionToolbar

        hits = []
        callbacks = defaultdict(list)
        bar = ActionToolbar(
            cmd,
            callbacks,
            panels=[("Builder", lambda: hits.append("builder"))],
            more=[("Get View", lambda: hits.append("view"))],
        )
        texts = {a.text(): a for a in bar.actions()}

        # selection mode: menu sets the setting, the setting sets the label
        self.assertEqual(bar.selecting.text(), "Residues")
        bar.selecting.menu().actions()[2].trigger()
        self.assertEqual(cmd.get_setting_int("mouse_selection_mode"), 2)
        self.assertEqual(bar.selecting.text(), "Chains")
        for callback in callbacks[cmd.setting._get_index("mouse_selection_mode")]:
            callback(0)
        self.assertEqual(bar.selecting.text(), "Atoms")

        # rock follows the setting
        self.assertFalse(bar.rock.isChecked())
        for callback in callbacks[cmd.setting._get_index("rock")]:
            callback(1)
        self.assertTrue(bar.rock.isChecked())

        cmd.fragment("ala")
        view = cmd.get_view()
        cmd.turn("x", 90)
        cmd.move("z", -30)
        bar.zoom.click()
        texts["Orient"].trigger()
        self.assertNotEqual(cmd.get_view(), view)

        bar.presets.menu().aboutToShow.emit()
        rows = [a.text() for a in bar.presets.menu().actions()]
        self.assertIn("technical", rows)
        self.assertNotIn("simple", rows)
        self.assertIn("figure", rows)  # the looks, last group of the list

        texts["Builder"].trigger()
        more = {a.text(): a for a in bar.more.menu().actions()}
        more["Get View"].trigger()
        self.assertEqual(hits, ["builder", "view"])

    def test_icons(self):
        from pymol.Qt import QtCore, QtGui, QtWidgets
        from pmg_qt.action_toolbar import ActionToolbar

        bar = ActionToolbar(
            cmd,
            defaultdict(list),
            panels=[
                ("Builder", lambda: None),
                ("Scenes", lambda: None),
                ("Draw/Ray", QtWidgets.QMenu()),
            ],
        )
        buttons = [
            b
            for b in bar.findChildren(QtWidgets.QToolButton)
            if b.objectName() != "qt_toolbar_ext_button"  # Qt's overflow arrow
        ]
        self.assertEqual(len(buttons), 14)
        self.assertEqual([b.text() for b in buttons if b.icon().isNull()], [])
        IconOnly = QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly
        self.assertEqual(
            sorted(b.toolTip() for b in buttons if b.toolButtonStyle() == IconOnly),
            # the view actions; Palette and Background have their text
            [
                "More view actions",
                "Orient",
                "Redo",
                "Rock",
                "Undo",
                "Zoom on everything",
            ],
        )
        # bolder and larger than the menu icons, and blue while hovered or
        # checked; the text of the selection mode is styled by its name
        self.assertEqual(bar.iconSize().width(), 20)
        icon = bar.colors.icon()
        Mode = QtGui.QIcon.Mode
        normal = icon.pixmap(20, 20, Mode.Normal).toImage()
        active = icon.pixmap(20, 20, Mode.Active).toImage()
        self.assertNotEqual(normal, active)
        self.assertEqual(bar.selecting.objectName(), "selecting")
        from pmg_qt import icons

        self.assertEqual(icons.LABELS["scenes"], "camera")

    def test_background(self):
        from unittest import mock
        from pmg_qt import action_toolbar, theme

        self.addCleanup(cmd.reinitialize)
        saved = []
        with (
            mock.patch.object(theme, "background", return_value=None),
            mock.patch.object(theme, "set_background", saved.append),
        ):
            bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
            menu = bar.background.menu()
            rows = {a.text(): a for a in menu.actions() if a.text()}
            names = [row[0] for row in action_toolbar.BACKGROUNDS if row]
            self.assertEqual(
                list(rows),
                [*names, "Ray trace with this background", "Remember after restart"],
            )

            def color(key):
                return cmd.get_color_tuple(cmd.get(key))

            # every row sets what the table says; a plain row ends a gradient
            for name, top, bottom in filter(None, action_toolbar.BACKGROUNDS):
                rows[name].trigger()
                rgb = tuple(int(top[i : i + 2], 16) / 255 for i in (0, 2, 4))
                self.assertEqual(cmd.get_setting_boolean("bg_gradient"), bool(bottom))
                for a, b in zip(color("bg_rgb_top" if bottom else "bg_rgb"), rgb):
                    self.assertAlmostEqual(a, b, 2, name)
            self.assertEqual(saved, [None] * len(names))  # nothing is kept

            # the row in use is the only one with a frame: its icon differs
            rows["White"].trigger()
            menu.aboutToShow.emit()
            pixel = {
                n: rows[n].icon().pixmap(16, 16).toImage().pixelColor(2, 2).name()
                for n in ("White", "Sky", "Black")
            }
            self.assertNotEqual(pixel["White"], "#ffffff")
            self.assertEqual(pixel["Black"], "#000000")

            # ray tracing with or without the background: one setting,
            # the one Draw/Ray and Display > Background use
            cmd.set("ray_opaque_background", 0)
            rows["Ray trace with this background"].trigger()
            self.assertEqual(cmd.get_setting_int("ray_opaque_background"), -1)
            self.assertEqual(cmd.get_setting_int("opaque_background"), 1)
            menu.aboutToShow.emit()
            self.assertTrue(rows["Ray trace with this background"].isChecked())
            rows["Ray trace with this background"].trigger()
            self.assertEqual(cmd.get_setting_int("opaque_background"), 0)

            # "Remember" keeps the settings now and after each pick
            del saved[:]
            rows["Remember after restart"].setChecked(True)
            rows["Studio"].trigger()
            self.assertEqual(len(saved), 2)
            self.assertEqual(len(saved[1]), len(action_toolbar.BACKGROUND_SETTINGS))
            rows["Remember after restart"].setChecked(False)
            self.assertIsNone(saved[-1])

        # the next start: applied only when a pymolrc may run (not -k)
        with (
            mock.patch.object(theme, "background", return_value=saved[1]),
            mock.patch.object(theme, "object_palette", return_value="default"),
            mock.patch.object(action_toolbar.pymol.invocation.options, "pymolrc", []),
        ):
            cmd.reinitialize()
            bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
        self.assertTrue(bar.remember_background.isChecked())
        self.assertTrue(cmd.get_setting_boolean("bg_gradient"))
        self.assertAlmostEqual(color("bg_rgb_bottom")[0], 0xC8 / 255, 2)

    def test_user_palette(self):
        from unittest import mock
        from pymol import CmdException, palettes
        from pymol.Qt import QtCore
        from pmg_qt import action_toolbar, theme
        from pmg_qt.palette_dialog import PaletteDialog

        role = QtCore.Qt.ItemDataRole.UserRole
        stored = {}
        self.addCleanup(cmd.reinitialize)
        self.addCleanup(
            lambda: [palettes.PALETTES.pop(n, None) for n in ("mine", "other")]
        )
        self.addCleanup(cmd.palette, "default")
        with (
            mock.patch.object(theme, "user_palettes", lambda: dict(stored)),
            mock.patch.object(theme, "set_user_palettes", stored.update),
            mock.patch.object(theme, "set_object_palette"),
        ):
            bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
            view = bar.palettes
            rows = {a.text(): a for a in bar.colors.menu().actions() if a.text()}
            self.assertEqual(
                list(rows), ["New palette...", "Edit palette...", "Delete palette"]
            )
            bar.colors.menu().aboutToShow.emit()
            self.assertFalse(bar.edit_palette.isEnabled())  # a built-in is active

            # what the dialog hands back is stored, listed and applied
            cmd.fragment("ala")
            bar._save_palette("mine", ["ff8800", "0088ff", "33cc66"])
            self.assertEqual(stored, {"mine": ["ff8800", "0088ff", "33cc66"]})
            names = [view.item(i).data(role) for i in range(view.count())]
            self.assertEqual(names[-1], "mine")
            self.assertEqual(view.item(view.count() - 1).text(), "Mine (yours)")
            self.assertEqual(palettes.active, "mine")
            self.assertEqual(cmd.count_atoms("elem C & color mine_01"), 3)
            bar.colors.menu().aboutToShow.emit()
            self.assertTrue(bar.edit_palette.isEnabled())
            self.assertTrue(bar.delete_palette.isEnabled())

            # edited with a new name: the old one is gone
            stored.clear()
            bar._save_palette("other", ["112233", "445566"], old="mine")
            self.assertEqual(list(stored), ["other"])
            self.assertNotIn("mine", palettes.PALETTES)
            self.assertEqual(palettes.active, "other")

            bar._delete_palette()
            self.assertEqual(palettes.active, "default")
            self.assertNotIn("other", palettes.PALETTES)

        # the rules of a palette of the user
        for name, colors in (
            ("vivid", ["ff0000", "00ff00"]),
            ("Bad Name", ["ff0000", "00ff00"]),
            ("mine", ["ff0000"]),
            ("mine", ["ff0000", "nothex"]),
        ):
            self.assertRaises(CmdException, palettes.define, name, colors)
        self.assertRaises(CmdException, palettes.undefine, "vivid")

        # the dialog: OK only with a free name and two colors
        import shiboken6

        dialog = PaletteDialog(None, "", (), taken=palettes.BUILTIN)
        self.addCleanup(shiboken6.delete, dialog)
        ok = dialog.box.button(dialog.box.StandardButton.Ok)
        self.assertFalse(ok.isEnabled())
        dialog.name.setText("vivid")
        dialog._append("ff8800")
        dialog._append("#0088ff")
        self.assertFalse(ok.isEnabled())  # a built-in name
        dialog.name.setText("mine")
        self.assertTrue(ok.isEnabled())
        dialog.list.setCurrentRow(1)
        dialog._move(-1)
        self.assertEqual(dialog.value(), ("mine", ["0088ff", "ff8800"]))
        dialog._remove()
        self.assertFalse(ok.isEnabled())

    def test_palette(self):
        from unittest import mock
        from pymol import palettes
        from pymol.Qt import QtCore
        from pmg_qt import action_toolbar, theme

        Qt = QtCore.Qt

        # -k (how the tests run): the saved palette is not applied
        with mock.patch.object(theme, "object_palette", return_value="deep"):
            bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
        self.assertEqual(palettes.active, "default")
        view = bar.palettes
        role = Qt.ItemDataRole.UserRole
        # 16a: the menu says what it colors, above the list
        caption = bar.colors.menu().actions()[0].defaultWidget()
        self.assertEqual(caption.text(), "Palette: colors of objects and chains")
        self.assertEqual(caption.objectName(), "menu_title")
        names = [view.item(i).data(role) for i in range(view.count())]
        self.assertEqual(names, ["default", *palettes.PALETTES])
        self.assertEqual(view.item(2).text(), "Deep (white background)")
        # wide enough to tell the colors apart: ten of them, 14 px each
        self.assertEqual(view.item(2).icon().availableSizes()[0].width(), 140)
        self.assertGreaterEqual(view.width(), view.sizeHintForColumn(0))
        try:
            # picking recolors what is loaded and is saved
            cmd.fragment("ala")
            with mock.patch.object(theme, "set_object_palette") as save:
                view.setCurrentRow(names.index("deep"))
            save.assert_called_once_with("deep")
            self.assertEqual(palettes.active, "deep")
            self.assertEqual(cmd.count_atoms("elem C & color deep_01"), 3)

            # typed: the list follows when the menu opens, nothing is saved
            cmd.palette("soft")
            with mock.patch.object(theme, "set_object_palette") as save:
                bar.colors.menu().aboutToShow.emit()
            save.assert_not_called()
            self.assertEqual(view.currentItem().data(role), "soft")
            self.assertEqual(cmd.count_atoms("elem C & color deep_01"), 3)

            # without -k the saved palette is back at start
            cmd.palette("default")
            with (
                mock.patch.object(theme, "object_palette", return_value="deep"),
                mock.patch.object(
                    action_toolbar.pymol.invocation.options, "pymolrc", []
                ),
            ):
                action_toolbar.ActionToolbar(cmd, defaultdict(list))
            self.assertEqual(palettes.active, "deep")
        finally:
            cmd.palette("default")

    def test_scale(self):
        from unittest import mock
        from pmg_qt import action_toolbar, theme

        with mock.patch.object(theme, "ui_scale", return_value=1.8):
            bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
        self.assertEqual(bar.scale.text(), "180%")
        actions = bar.scale.menu().actions()
        self.assertEqual(
            [a.text() for a in actions], ["100%", "120%", "150%", "180%", "200%"]
        )
        self.assertEqual([a.text() for a in actions if a.isChecked()], ["180%"])
        with (
            mock.patch.object(theme, "set_ui_scale") as save,
            mock.patch.object(action_toolbar.QtWidgets.QMessageBox, "information"),
        ):
            actions[1].trigger()
        save.assert_called_once_with(1.2)
