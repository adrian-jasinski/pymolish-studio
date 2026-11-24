"""
Timeline panel: shots are added, edited, moved and deleted, and each edit
rebuilds the movie of the core. Headless (offscreen QApplication).
"""

import os

from pymol import cmd, testing


def test_panel(request):
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
    request.addfinalizer(lambda: shiboken6.delete(panel))
    table = panel.table
    assert panel.blocks() == []

    # the Add menu lists the scenes; a tour adds one shot per scene
    panel.add.menu().aboutToShow.emit()
    rows = [a.text() for a in panel.add.menu().actions()]
    assert "Scene" in rows
    assert "Hold" in rows
    panel._tour("scenes")
    assert table.rowCount() == 2
    assert cmd.get_movie_length() == 240
    assert [b[:3] for b in panel.blocks()] == [
        (1, 120, "scene s1"),
        (121, 120, "scene s2"),
    ]

    # seconds are typed into the table
    table.item(0, timeline.SECONDS).setText("2")
    assert cmd.get_movie_length() == 180
    table.item(0, timeline.SECONDS).setText("nonsense")
    assert table.item(0, timeline.SECONDS).text() == "2"
    # start and effect are picked from lists
    table.cellWidget(1, timeline.START).setCurrentText("cut")
    assert panel.shots[1]["start"] == "cut"
    table.cellWidget(1, timeline.EFFECT).setCurrentText("fade in cartoon")
    cmd.frame(180)
    assert cmd.get_setting_float("cartoon_transparency") == 0

    # a shot goes in after the selected one; move, delete
    table.selectRow(0)
    panel.append("turn")
    assert [s["kind"] for s in panel.shots] == ["scene", "turn", "scene"]
    assert table.currentRow() == 1
    panel.move_shot(1)
    assert [s["kind"] for s in panel.shots] == ["scene", "scene", "turn"]
    assert table.currentRow() == 2
    panel.delete()
    assert len(panel.shots) == 2
    assert cmd.get_movie_length() == 60 + 120

    # the strip: a click moves the playhead and selects the shot
    panel.seek(150)
    assert cmd.get_frame() == 150
    assert table.currentRow() == 1
    assert panel.grab().isNull() == False

    # record: a view that moved and came to rest becomes a shot
    panel.record.setChecked(True)
    panel._timer.stop()  # ticks by hand
    panel._watch_view()
    assert len(panel.shots) == 2
    cmd.turn("x", 40)
    panel._watch_view()  # moving
    panel._watch_view()  # at rest
    assert [s["kind"] for s in panel.shots][-1] == "view"
    assert len(panel.shots) == 3
    panel.record.setChecked(False)

    # a movie replaced from outside: the list is dropped, the movie stays
    panel.show()
    cmd.mset("1 x10")
    panel.poll()
    # the panel opens by itself when a movie appears, once
    panel.hide()
    panel.poll()
    assert not panel.isVisible()  # closed by the user: stays closed
    cmd.mset()
    panel.poll()
    cmd.mset("1 x10")
    panel.poll()
    assert panel.isVisible()
    assert panel.shots == []
    assert table.rowCount() == 0
    assert "Made with commands" in panel.info.text()
    assert len(panel.blocks()) == 0
    panel.hide()

    # a shot would replace that movie: only after a yes
    from unittest import mock

    with mock.patch.object(panel, "_replace_ok", return_value=False):
        panel.append("turn")
    assert (panel.shots, cmd.get_movie_length()) == ([], 10)
    with mock.patch.object(panel, "_replace_ok", return_value=True):
        panel.append("turn")
    assert cmd.get_movie_length() == 240

    panel.clear_movie()
    assert cmd.get_movie_length() == 0


def test_drag_and_session(request, tmp_path):
    """19: the strip moves and stretches shots with the mouse, and the list
    comes back with the session it was saved in."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import shiboken6
    from PySide6.QtTest import QTest
    from pymol import session_extra
    from pymol.Qt import QtCore, QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from pmg_qt import timeline

    cmd.set("movie_fps", 30)
    cmd.fab("ACDEFGHIK", "pep")
    panel = timeline.TimelinePanel(cmd)
    request.addfinalizer(lambda: shiboken6.delete(panel))
    request.addfinalizer(session_extra.entries.clear)
    strip = panel.strip
    strip.resize(600, 70)
    for kind in ("turn", "rock", "hold"):
        panel.append(kind, seconds=2)
    assert cmd.get_movie_length() == 180  # 200 px a shot
    Left = QtCore.Qt.MouseButton.LeftButton
    none = QtCore.Qt.KeyboardModifier.NoModifier

    def drag(x0, x1, y=40):
        QTest.mousePress(strip, Left, none, QtCore.QPoint(x0, y))
        QTest.mouseMove(strip, QtCore.QPoint((x0 + x1) // 2, y))
        QTest.mouseMove(strip, QtCore.QPoint(x1, y))
        QTest.mouseRelease(strip, Left, none, QtCore.QPoint(x1, y))

    assert strip.hit(100, 5) == ("seek", -1)  # the ruler
    assert strip.hit(100, 40) == ("move", 0)
    assert strip.hit(198, 40) == ("stretch", 0)
    # a block dragged onto the third one takes its place
    drag(100, 500)
    assert [s["kind"] for s in panel.shots] == ["rock", "hold", "turn"]
    assert panel.table.currentRow() == 2
    # the right end of the first block dragged from 2 s to 3 s
    drag(198, 300)
    assert panel.shots[0]["seconds"] == 3
    assert cmd.get_movie_length() == 210
    # a click on a block, and a drag on the ruler, move the playhead
    QTest.mouseClick(strip, Left, none, QtCore.QPoint(450, 40))
    assert cmd.get_frame() == 1 + int(450 * 210 / 600)
    assert [s["kind"] for s in panel.shots] == ["rock", "hold", "turn"]
    drag(100, 300, y=5)
    assert cmd.get_frame() == 1 + int(300 * 210 / 600)
    assert not strip.grab().isNull()

    # the session keeps the list with the movie it built
    kinds = ["rock", "hold", "turn"]
    filename = str(tmp_path / "movie.pse")
    cmd.save(filename)
    cmd.reinitialize()
    panel.poll()
    assert panel.shots == [] and "timeline" not in session_extra.entries
    cmd.load(filename)
    panel.poll()
    assert [s["kind"] for s in panel.shots] == kinds
    assert panel.table.rowCount() == 3 and panel.shots[0]["seconds"] == 3
    assert [b[1] for b in panel.blocks()] == [90, 60, 60]
    panel.delete()  # and it is edited like the one that was made here
    assert cmd.get_movie_length() == 120
    # a movie that is no longer the one of the list: no list
    cmd.load(filename)
    cmd.mset("1 x10")
    panel.poll()
    assert panel.shots == []
    # a damaged entry is passed over
    session_extra.entries["timeline"] = {"shots": [{"kind": "nonsense"}]}
    panel.poll()
    assert panel.shots == []
