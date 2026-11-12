"""
Action toolbar: selection mode menu and label, rock state, zoom, presets
menu, panel and More entries, movie buttons only when asked for.
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
        self.assertIn("simple", [a.text() for a in bar.presets.menu().actions()])

        texts["Builder"].trigger()
        more = {a.text(): a for a in bar.more.menu().actions()}
        more["Get View"].trigger()
        self.assertEqual(hits, ["builder", "view"])

        self.assertFalse(texts["Play"].isVisible())
        bar.set_movie_visible(True)
        self.assertTrue(texts["Play"].isVisible())
