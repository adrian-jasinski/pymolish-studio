"""
Objects panel: rows and group nesting, the menu table against pymol.menu,
menu building, visibility toggle, filter, refresh after delete, the states
panel and the wizard buttons. Headless (offscreen QApplication).
"""

import pytest
import os
import re

from pymol import cmd, menu, testing


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_snapshot():
    from pmg_qt.object_panel import snapshot

    cmd.fragment("gly", "g1")
    cmd.fragment("ala", "a2")
    cmd.disable("a2")
    cmd.group("grp", "a2")
    cmd.select("sele", "name CA")
    rows = {r[0]: r for r in snapshot(cmd)}
    assert next(iter(rows)) == "all"
    assert rows["a2"] == ("a2", "object:molecule", False, "grp")
    assert rows["g1"] == ("g1", "object:molecule", True, "")
    assert rows["grp"][1] == "object:group"
    assert rows["sele"][1] == "selection"


def test_menu_table():
    from pmg_qt.object_panel import MENUS, menu_entries

    for functions in MENUS.values():
        assert len(functions) == 5
        for function in filter(None, functions):
            assert callable(getattr(menu, function)), function
    cmd.fragment("ala")
    for button in range(5):
        assert menu_entries(cmd, "ala", "object:molecule", button)
    assert menu_entries(cmd, "x", "object:map", 3) is None  # no labels


def test_fill_menu():
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
    entries.append([1, r"\933delete", 'cmd.delete("none")'])
    fill_menu(popup, entries, cmd)
    title = popup.actions()[0]  # a caption, skipped by the keyboard
    assert title.defaultWidget().text() == "Color:"
    assert not title.isEnabled()
    delete = popup.actions()[-1]  # a known command gets its line icon
    assert not delete.icon().isNull()
    red, more = (a for a in popup.actions() if a.text() in ("red", "more"))
    assert not red.icon().isNull()  # swatch from the \900 markup
    red.trigger()
    colors = set()
    cmd.iterate("ala", "colors.add(color)", space={"colors": colors})
    assert colors == {cmd.get_color_index("red")}
    assert more.menu().isEmpty()  # filled when first opened
    more.menu().aboutToShow.emit()
    assert [a.text() for a in more.menu().actions()] == ["hide"]


def test_context_menu():
    from pmg_qt.object_panel import context_menu

    def texts(name, kind):
        popup = context_menu(None, cmd, name, kind)
        return [a.text() for a in popup.actions() if not a.isSeparator()]

    cmd.fragment("ala", "m")
    cmd.select("s", "m and name CA")
    cmd.group("g", "m")
    rest = ["Action", "Show", "Hide", "Label"]
    for name, kind, word in (
        ("m", "object:molecule", "object"),
        ("g", "object:group", "group"),
        ("s", "selection", "selection"),
    ):
        flat = [
            "%s %s" % (verb, word) for verb in ("rename", "duplicate", "delete")
        ]
        assert texts(name, kind) == ["Show as", "Color"] + flat + rest
    cmd.pseudoatom("p")
    cmd.distance("d", "p", "m and name CA")
    assert texts("d", "object:measurement") == ["Color", "rename", "delete", "Action", "Show", "Hide"]
    # a flat row runs its command, a submenu is filled when opened
    popup = context_menu(None, cmd, "m", "object:molecule")
    actions = {a.text(): a for a in popup.actions()}
    actions["Show as"].menu().aboutToShow.emit()
    assert "cartoon" in [a.text() for a in actions["Show as"].menu().actions()]
    actions["duplicate object"].trigger()
    assert cmd.count_atoms("m_cpy") == cmd.count_atoms("m")
    actions["delete object"].trigger()
    assert "m" not in cmd.get_names()


def test_icons():
    from pymol.Qt import QtGui
    from pmg_qt import icons

    white = QtGui.QColor("white")
    for label in icons.LABELS:
        image = icons.menu_icon(label, white).pixmap(16, 16).toImage()
        # drawn in the color asked for, on a clear background
        drawn = [
            image.pixelColor(x, y)
            for x in range(image.width())
            for y in range(image.height())
            if image.pixelColor(x, y).alpha() > 100
        ]
        assert drawn, label
        assert all(c.lightness() > 240 for c in drawn), label
    assert icons.menu_icon("no such command", white) is None
    # destructive rows get the trash icon, not a red square
    source = open(menu.__file__).read()
    risky = re.findall(r"(?:del|rem)_col \+ '([^']+)'", source)
    assert len(risky) > 20
    for label in risky:
        assert icons.menu_icon(label, white) is not None, label
    # every top-level command of the viewport's menu has an icon
    for entry in menu.main_menu(cmd, (0, 0, 0), (0, 0)):
        if entry[0] == 1:
            assert entry[1].replace(r"\933", "") in icons.LABELS


def test_panel():
    from pmg_qt.object_panel import Checked, ObjectPanel, Unchecked

    cmd.fragment("gly", "g1")
    cmd.fragment("ala", "a2")
    cmd.group("grp", "a2")
    panel = ObjectPanel(cmd)
    panel.refresh()
    assert panel.items["a2"].parent() is panel.items["grp"]
    assert [panel.items["g1"].text(c) for c in range(1, 6)] == list("ASHLC")

    # a click on the name hides the object, the next one shows it again
    panel._clicked(panel.items["g1"], 0)
    assert "g1" not in cmd.get_names("objects", enabled_only=1)
    assert panel.items["g1"].checkState(0) == Unchecked
    panel._clicked(panel.items["g1"], 0)
    assert "g1" in cmd.get_names("objects", enabled_only=1)
    assert panel.items["g1"].checkState(0) == Checked
    # a double click arrives after a click hid the row: shown again
    panel._clicked(panel.items["g1"], 0)
    panel._double_clicked(panel.items["g1"], 0)
    assert "g1" in cmd.get_names("objects", enabled_only=1)

    panel.filter.setText("a2")
    assert panel.items["g1"].isHidden()
    assert not panel.items["grp"].isHidden()  # its member matches

    cmd.delete("g1")
    panel.refresh()
    assert "g1" not in panel.items


def test_states():
    from pmg_qt.object_panel import StatesPanel

    panel = StatesPanel(cmd)
    cmd.fragment("ala")
    panel.refresh()
    assert panel.isHidden()  # nothing to step through

    for state in (2, 3, 4):
        cmd.create("ala", "ala", 1, state)
    panel.refresh()
    assert not panel.isHidden()
    assert panel.title.text() == "States"
    assert panel.counter.text() == "1/4"
    assert panel.counter.maximum() == 4

    for button, frame in (("last", 4), ("first", 1), ("forward", 2)):
        panel.buttons[button].click()
        assert cmd.get_frame() == frame
        assert panel.counter.value() == frame
    panel.buttons["previous"].click()
    assert cmd.get_frame() == 1
    panel.counter.setValue(3)  # typed or stepped by the user
    assert cmd.get_state() == 3
    cmd.frame(2)  # changed by command: the next poll shows it
    panel.refresh()
    assert panel.counter.text() == "2/4"

    play = panel.buttons["play"]
    play.click()
    assert cmd.get_movie_playing()
    assert play.toolTip() == "Stop"
    play.click()
    assert not cmd.get_movie_playing()
    assert play.toolTip() == "Play"

    speeds = {a.text(): a for a in panel.speed.menu().actions()}
    speeds["5 fps"].trigger()
    assert cmd.get_setting_float("movie_fps") == 5
    assert panel.speed.text() == "5 fps"
    cmd.set("movie_fps", 0.3)
    panel.refresh()
    assert panel.speed.text() == "0.3 fps"

    cmd.mset("1 x8")  # a movie: frames, not states
    panel.refresh()
    assert panel.title.text() == "Frames"
    assert panel.counter.maximum() == 8

    cmd.delete("ala")
    cmd.mclear()
    cmd.mset()
    panel.refresh()
    assert panel.isHidden()


def test_wizard():
    from pmg_qt.object_panel import ObjectPanel

    panel = ObjectPanel(cmd)
    cmd.wizard("measurement")
    panel.wizard.refresh()
    buttons = [
        panel.wizard.buttons.itemAt(i).widget()
        for i in range(panel.wizard.buttons.count())
    ]
    assert not panel.wizard.isHidden()
    done = [b for b in buttons if b.text() == "Done"][0]
    assert any(b.menu() for b in buttons)  # mode popups
    done.click()
    assert cmd.get_wizard() is None
    panel.wizard.refresh()
    assert panel.wizard.isHidden()
