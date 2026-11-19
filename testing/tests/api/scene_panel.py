"""
Scenes panel: rows follow the scene list and the current scene; recall, move,
rename (bad names refused), add, delete. Headless (offscreen QApplication),
where scenes have no thumbnail.
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

    rows.itemActivated.emit(rows.item(0))
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
