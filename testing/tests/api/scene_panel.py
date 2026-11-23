"""
Scenes panel: rows follow the scene list and the current scene; recall, move,
rename (bad names refused), add, delete; one click or Enter recalls once.
Headless (offscreen QApplication), where scenes have no thumbnail.
"""

import pytest
import os

from pymol import cmd, testing


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_panel(app):
    from pmg_qt.scene_panel import ScenePanel

    cmd.fragment("gly")
    for name in ("a", "b", "c"):
        cmd.turn("x", 30)
        cmd.scene(name, "store")
    panel = ScenePanel(cmd)
    rows = panel.list

    def names():
        panel.refresh()
        return [rows.item(i).text() for i in range(rows.count())]

    assert names() == ["a", "b", "c"]
    assert rows.currentItem().text() == "c"

    panel._recall(rows.item(0))
    assert cmd.get("scene_current_name") == "a"
    names()
    assert rows.currentRow() == 0

    panel._move(1)  # Ctrl+Down
    assert cmd.get_scene_list() == ["b", "a", "c"]
    assert rows.currentItem().text() == "a"
    panel._move(1)
    panel._move(1)  # already last
    panel._move(-1)
    assert cmd.get_scene_list() == ["b", "a", "c"]
    assert names() == ["b", "a", "c"]

    rows.item(0).setText("first")
    app.processEvents()
    assert cmd.get_scene_list() == ["first", "a", "c"]
    # "" would delete the scene, "a" would overwrite scene a
    for bad in ("", "a", "two words"):
        rows.item(0).setText(bad)
        app.processEvents()
        assert cmd.get_scene_list() == ["first", "a", "c"]
        assert names() == ["first", "a", "c"]

    panel._add()
    assert len(names()) == 4
    rows.setCurrentRow(1)
    panel._scene("clear")
    assert names()[:2] == ["first", "c"]

    cmd.scene("*", "clear")  # a command, not the panel
    assert names() == []


def test_one_click_recalls_once(app):
    """35a: a click or Enter recalls a scene once; a double click, a right
    click, F2, a move and a refresh of the list recall nothing more."""
    from unittest import mock

    from PySide6.QtTest import QTest
    from pymol.Qt import QtCore, QtWidgets
    from pmg_qt.scene_panel import ScenePanel

    Qt = QtCore.Qt
    cmd.fragment("gly")
    for name in ("a", "b", "c"):
        cmd.turn("x", 30)
        cmd.scene(name, "store")
    panel = ScenePanel(cmd)
    panel.resize(300, 500)
    panel.show()
    panel.activateWindow()
    panel.refresh()
    rows = panel.list
    port = rows.viewport()
    app.processEvents()

    def at(row):
        return rows.visualItemRect(rows.item(row)).center()

    def recalls(run):
        with mock.patch.object(cmd, "scene", wraps=cmd.scene) as scene:
            run()
            app.processEvents()
        return [
            call.args[0]
            for call in scene.call_args_list
            if call.args[1:] == ("recall",)
        ]

    left, right = Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton
    none = Qt.KeyboardModifier.NoModifier
    assert recalls(lambda: QTest.mouseClick(port, left, none, at(0))) == ["a"]
    assert cmd.get("scene_current_name") == "a"

    def double_click():  # press, release, double click, release
        QTest.mouseClick(port, left, none, at(1))
        QTest.mouseDClick(port, left, none, at(1))
        QTest.mouseRelease(port, left, none, at(1))

    assert recalls(double_click) == ["b"]
    assert not port.findChild(QtWidgets.QLineEdit)  # and no rename started

    # a right click picks the row for Update, Rename and Delete
    assert recalls(lambda: QTest.mouseClick(port, right, none, at(2))) == []
    assert rows.currentRow() == 2 and cmd.get("scene_current_name") == "b"
    # so do the arrow keys; Enter recalls
    rows.setFocus()
    assert recalls(lambda: QTest.keyClick(rows, Qt.Key.Key_Up)) == []
    assert rows.currentRow() == 1
    QTest.keyClick(rows, Qt.Key.Key_Up)
    assert recalls(lambda: QTest.keyClick(rows, Qt.Key.Key_Return)) == ["a"]

    # moving a row and a refresh of the list recall nothing
    assert recalls(lambda: panel._move(1)) == []
    panel.state = None
    assert recalls(panel.refresh) == []
    # F2 renames; Enter in the editor ends the rename, it does not recall
    rows.setCurrentRow(0)
    assert recalls(lambda: QTest.keyClick(rows, Qt.Key.Key_F2)) == []
    editor = port.findChild(QtWidgets.QLineEdit)
    assert editor is not None

    def typed():
        editor.setText("renamed")
        QTest.keyClick(editor, Qt.Key.Key_Return)

    assert recalls(typed) == []
    assert "renamed" in cmd.get_scene_list()
    panel.close()
