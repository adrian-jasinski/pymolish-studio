"""
Timeline panel: shots are added, edited, moved and deleted, and each edit
rebuilds the movie of the core. Headless (offscreen QApplication).
"""

import os

from pymol import cmd, testing


class TestTimeline(testing.PyMOLTestCase):
    def test_panel(self):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        import shiboken6
        from pymol.Qt import QtWidgets

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        from pmg_qt import timeline

        cmd.set("movie_fps", 30)
        cmd.fab("ACDEFGHIK", "pep")
        cmd.scene("s1", "store")
        cmd.turn("y", 60)
        cmd.scene("s2", "store")
        panel = timeline.TimelinePanel(cmd)
        self.addCleanup(shiboken6.delete, panel)
        table = panel.table
        self.assertEqual(panel.blocks(), [])

        # the Add menu lists the scenes; a tour adds one shot per scene
        panel.add.menu().aboutToShow.emit()
        rows = [a.text() for a in panel.add.menu().actions()]
        self.assertIn("Scene", rows)
        self.assertIn("Hold", rows)
        panel._tour("scenes")
        self.assertEqual(table.rowCount(), 2)
        self.assertEqual(cmd.get_movie_length(), 240)
        self.assertEqual(
            [b[:3] for b in panel.blocks()],
            [(1, 120, "scene s1"), (121, 120, "scene s2")],
        )

        # seconds are typed into the table
        table.item(0, timeline.SECONDS).setText("2")
        self.assertEqual(cmd.get_movie_length(), 180)
        table.item(0, timeline.SECONDS).setText("nonsense")
        self.assertEqual(table.item(0, timeline.SECONDS).text(), "2")
        # start and effect are picked from lists
        table.cellWidget(1, timeline.START).setCurrentText("cut")
        self.assertEqual(panel.shots[1]["start"], "cut")
        table.cellWidget(1, timeline.EFFECT).setCurrentText("fade in cartoon")
        cmd.frame(180)
        self.assertEqual(cmd.get_setting_float("cartoon_transparency"), 0)

        # a shot goes in after the selected one; move, delete
        table.selectRow(0)
        panel.append("turn")
        self.assertEqual([s["kind"] for s in panel.shots], ["scene", "turn", "scene"])
        self.assertEqual(table.currentRow(), 1)
        panel.move_shot(1)
        self.assertEqual([s["kind"] for s in panel.shots], ["scene", "scene", "turn"])
        self.assertEqual(table.currentRow(), 2)
        panel.delete()
        self.assertEqual(len(panel.shots), 2)
        self.assertEqual(cmd.get_movie_length(), 60 + 120)

        # the strip: a click moves the playhead and selects the shot
        panel.seek(150)
        self.assertEqual(cmd.get_frame(), 150)
        self.assertEqual(table.currentRow(), 1)
        self.assertEqual(panel.grab().isNull(), False)

        # record: a view that moved and came to rest becomes a shot
        panel.record.setChecked(True)
        panel._timer.stop()  # ticks by hand
        panel._watch_view()
        self.assertEqual(len(panel.shots), 2)
        cmd.turn("x", 40)
        panel._watch_view()  # moving
        panel._watch_view()  # at rest
        self.assertEqual([s["kind"] for s in panel.shots][-1], "view")
        self.assertEqual(len(panel.shots), 3)
        panel.record.setChecked(False)

        # a movie replaced from outside: the list is dropped, the movie stays
        panel.show()
        cmd.mset("1 x10")
        panel.poll()
        # the panel opens by itself when a movie appears, once
        panel.hide()
        panel.poll()
        self.assertFalse(panel.isVisible())  # closed by the user: stays closed
        cmd.mset()
        panel.poll()
        cmd.mset("1 x10")
        panel.poll()
        self.assertTrue(panel.isVisible())
        self.assertEqual(panel.shots, [])
        self.assertEqual(table.rowCount(), 0)
        self.assertIn("Made with commands", panel.info.text())
        self.assertEqual(len(panel.blocks()), 0)
        panel.hide()

        # a shot would replace that movie: only after a yes
        from unittest import mock

        with mock.patch.object(panel, "_replace_ok", return_value=False):
            panel.append("turn")
        self.assertEqual((panel.shots, cmd.get_movie_length()), ([], 10))
        with mock.patch.object(panel, "_replace_ok", return_value=True):
            panel.append("turn")
        self.assertEqual(cmd.get_movie_length(), 240)

        panel.clear_movie()
        self.assertEqual(cmd.get_movie_length(), 0)
