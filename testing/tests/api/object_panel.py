"""
Objects panel: rows and group nesting, the menu table against pymol.menu,
menu building, visibility toggle, filter, refresh after delete and the
wizard buttons. Headless (offscreen QApplication).
"""

import os

from pymol import cmd, menu, testing


class TestObjectPanel(testing.PyMOLTestCase):
    def setUp(self):
        super().setUp()
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from pymol.Qt import QtWidgets

        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def test_snapshot(self):
        from pmg_qt.object_panel import snapshot

        cmd.fragment("gly", "g1")
        cmd.fragment("ala", "a2")
        cmd.disable("a2")
        cmd.group("grp", "a2")
        cmd.select("sele", "name CA")
        rows = {r[0]: r for r in snapshot(cmd)}
        self.assertEqual(next(iter(rows)), "all")
        self.assertEqual(rows["a2"], ("a2", "object:molecule", False, "grp"))
        self.assertEqual(rows["g1"], ("g1", "object:molecule", True, ""))
        self.assertEqual(rows["grp"][1], "object:group")
        self.assertEqual(rows["sele"][1], "selection")

    def test_menu_table(self):
        from pmg_qt.object_panel import MENUS, menu_entries

        for functions in MENUS.values():
            self.assertEqual(len(functions), 5)
            for function in filter(None, functions):
                self.assertTrue(callable(getattr(menu, function)), function)
        cmd.fragment("ala")
        for button in range(5):
            self.assertTrue(menu_entries(cmd, "ala", "object:molecule", button))
        self.assertIsNone(menu_entries(cmd, "x", "object:map", 3))  # no labels

    def test_fill_menu(self):
        from pymol.Qt import QtWidgets
        from pmg_qt.object_panel import fill_menu

        cmd.fragment("ala")
        popup = QtWidgets.QMenu()
        entries = [
            [2, "Color:", ""],
            [1, "\\900red", 'cmd.color("red","ala")'],
            [0, "", ""],
            [1, "more", lambda: [[1, "hide", 'cmd.disable("ala")']]],
        ]
        fill_menu(popup, entries, cmd)
        red, more = (a for a in popup.actions() if a.text() in ("red", "more"))
        self.assertFalse(red.icon().isNull())  # swatch from the \900 markup
        red.trigger()
        colors = set()
        cmd.iterate("ala", "colors.add(color)", space={"colors": colors})
        self.assertEqual(colors, {cmd.get_color_index("red")})
        self.assertTrue(more.menu().isEmpty())  # filled when first opened
        more.menu().aboutToShow.emit()
        self.assertEqual([a.text() for a in more.menu().actions()], ["hide"])

    def test_panel(self):
        from pmg_qt.object_panel import Checked, ObjectPanel, Unchecked

        cmd.fragment("gly", "g1")
        cmd.fragment("ala", "a2")
        cmd.group("grp", "a2")
        panel = ObjectPanel(cmd)
        panel.refresh()
        self.assertIs(panel.items["a2"].parent(), panel.items["grp"])
        self.assertEqual(
            [panel.items["g1"].text(c) for c in range(1, 6)], list("ASHLC")
        )

        # a click on the name hides the object, the next one shows it again
        panel._clicked(panel.items["g1"], 0)
        self.assertNotIn("g1", cmd.get_names("objects", enabled_only=1))
        self.assertEqual(panel.items["g1"].checkState(0), Unchecked)
        panel._clicked(panel.items["g1"], 0)
        self.assertIn("g1", cmd.get_names("objects", enabled_only=1))
        self.assertEqual(panel.items["g1"].checkState(0), Checked)
        # a double click arrives after a click hid the row: shown again
        panel._clicked(panel.items["g1"], 0)
        panel._double_clicked(panel.items["g1"], 0)
        self.assertIn("g1", cmd.get_names("objects", enabled_only=1))

        panel.filter.setText("a2")
        self.assertTrue(panel.items["g1"].isHidden())
        self.assertFalse(panel.items["grp"].isHidden())  # its member matches

        cmd.delete("g1")
        panel.refresh()
        self.assertNotIn("g1", panel.items)

    def test_status(self):
        from pmg_qt.object_panel import status_text

        cmd.fragment("ala")
        self.assertEqual(status_text(cmd), "State 1/1")

    def test_wizard(self):
        from pmg_qt.object_panel import ObjectPanel

        panel = ObjectPanel(cmd)
        cmd.wizard("measurement")
        panel.wizard.refresh()
        buttons = [
            panel.wizard.buttons.itemAt(i).widget()
            for i in range(panel.wizard.buttons.count())
        ]
        self.assertFalse(panel.wizard.isHidden())
        done = [b for b in buttons if b.text() == "Done"][0]
        self.assertTrue(any(b.menu() for b in buttons))  # mode popups
        done.click()
        self.assertIsNone(cmd.get_wizard())
        panel.wizard.refresh()
        self.assertTrue(panel.wizard.isHidden())
