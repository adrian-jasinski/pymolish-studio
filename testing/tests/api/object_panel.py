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


def test_row_with_submenu_and_command():
    # a submenu row with a fourth entry: Enter or a click runs it and
    # closes the menu, a row without one only opens its submenu
    from pymol.Qt import QtCore, QtGui, QtWidgets
    from pmg_qt.object_panel import fill_menu

    cmd.fragment("ala")
    cmd.show_as("lines")
    popup = QtWidgets.QMenu()
    only = [[1, "only", 'cmd.show_as("sticks","ala")']]
    fill_menu(
        popup,
        [[1, "sticks", only, 'cmd.show("sticks","ala")'], [1, "more", only]],
        cmd,
    )
    sticks, more = popup.actions()

    def enter(action):
        popup.setActiveAction(action)
        event = QtGui.QKeyEvent(
            QtCore.QEvent.Type.KeyPress,
            QtCore.Qt.Key.Key_Return,
            QtCore.Qt.KeyboardModifier.NoModifier,
        )
        QtWidgets.QApplication.sendEvent(popup, event)

    def click(action):
        from PySide6.QtTest import QTest

        QTest.mouseClick(
            popup,
            QtCore.Qt.MouseButton.LeftButton,
            pos=popup.actionGeometry(action).center(),
        )

    enter(more)
    assert not cmd.count_atoms("rep sticks")
    for run in (enter, click):
        cmd.hide("sticks")
        popup.popup(QtCore.QPoint(0, 0))
        run(sticks)
        assert cmd.count_atoms("rep sticks") == cmd.count_atoms("ala")
        assert cmd.count_atoms("rep lines")  # shown on top, not "as"
        assert not popup.isVisible()
    sticks.menu().aboutToShow.emit()
    sticks.menu().actions()[0].trigger()
    assert not cmd.count_atoms("rep lines")


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
        flat = ["%s %s" % (verb, word) for verb in ("rename", "duplicate", "delete")]
        assert texts(name, kind) == ["Show as", "Color"] + flat + rest
    cmd.pseudoatom("p")
    cmd.distance("d", "p", "m and name CA")
    assert texts("d", "object:measurement") == [
        "Color",
        "rename",
        "delete",
        "Action",
        "Show",
        "Hide",
    ]
    # a flat row runs its command, a submenu is filled when opened
    popup = context_menu(None, cmd, "m", "object:molecule")
    actions = {a.text(): a for a in popup.actions()}
    actions["Show as"].menu().aboutToShow.emit()
    assert "cartoon" in [a.text() for a in actions["Show as"].menu().actions()]
    actions["Show as"].menu().actions()[-1].trigger()  # label: a flat row
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


def test_delete_key(monkeypatch):
    """37b: Delete on the current row. An object or selection goes at once,
    a group asks and goes with everything inside it."""
    from PySide6 import QtTest
    from pymol.Qt import QtCore, QtGui, QtWidgets
    from pmg_qt.object_panel import ObjectPanel

    Button = QtWidgets.QMessageBox.StandardButton
    asked = []
    answer = [Button.Cancel]

    def question(parent, title, text, buttons, default):
        asked.append(text)
        assert default == Button.Cancel
        return answer[0]

    monkeypatch.setattr(QtWidgets.QMessageBox, "question", question)
    for name in ("one", "m1", "m2", "keep"):
        cmd.fragment("gly", name)
    cmd.select("picked", "one and name CA")
    cmd.group("inner", "m2")
    cmd.group("outer", "m1 inner")
    cmd.group("hollow")
    panel = ObjectPanel(cmd)
    panel.refresh()

    def press(name):
        panel.tree.setCurrentItem(panel.items[name])
        panel.delete()

    press("one")  # no question for an object
    assert "one" not in cmd.get_names() and "one" not in panel.items
    assert panel.tree.currentItem() is None
    panel.delete()  # no current row after it: a second press does nothing
    press("picked")
    assert "picked" not in cmd.get_names("all") and not asked
    press("all")
    assert "keep" in cmd.get_names()
    assert "keep" in cmd.get_names("public_objects", enabled_only=1)  # not hidden

    press("outer")  # Cancel: nothing changes
    assert asked == [
        'Delete the group "outer" and the 2 objects and 1 groups inside it?'
        "\n\nm1, inner, m2"
    ]
    assert {"outer", "inner", "m1", "m2"} <= set(cmd.get_names())
    answer[0] = Button.Yes
    press("outer")
    assert cmd.get_names() == ["keep", "hollow"]
    press("hollow")
    assert asked[-1] == 'Delete the empty group "hollow"?'
    assert cmd.get_names() == ["keep"] and list(panel.items) == ["all", "keep"]

    # the key is bound to the list alone: in the filter it edits the text
    shortcuts = panel.findChildren(QtGui.QShortcut)
    bound = [s for s in shortcuts if s.key().toString() == "Del"]
    assert [s.parent() for s in bound] == [panel.tree]
    assert bound[0].context() == QtCore.Qt.ShortcutContext.WidgetShortcut
    assert not bound[0].autoRepeat()
    panel.show()
    panel.filter.setText("ke")
    panel.filter.setFocus()
    panel.filter.setCursorPosition(0)
    QtTest.QTest.keyClick(panel.filter, QtCore.Qt.Key.Key_Delete)
    assert panel.filter.text() == "e" and cmd.get_names() == ["keep"]


@pytest.fixture
def rows():
    """A panel over o1, o2, a group g1 with m1 and m2, and a selection."""
    from pmg_qt.object_panel import ObjectPanel, UserRole

    for name in ("o1", "o2", "m1", "m2"):
        cmd.fragment("gly", name)
    cmd.group("g1", "m1 m2")
    cmd.select("s1", "o1 and name CA")
    panel = ObjectPanel(cmd)
    panel.refresh()

    def tree(parent=None):
        parent = parent or panel.tree.invisibleRootItem()
        found = []
        for i in range(parent.childCount()):
            child = parent.child(i)
            name, inside = child.data(0, UserRole)[0], tree(child)
            found.append({name: inside} if inside else name)
        return found

    panel.shown = tree
    return panel


def test_move_rows(rows, tmp_path):
    """23b: the operation behind the drag and the Alt+arrow keys."""
    panel = rows
    assert panel.shown() == ["all", "o1", "o2", {"g1": ["m1", "m2"]}, "s1"]
    assert panel.move("o2", "o1", "before")
    assert panel.shown() == ["all", "o2", "o1", {"g1": ["m1", "m2"]}, "s1"]
    assert panel.tree.currentItem() is panel.items["o2"]
    assert panel.move("s1", "all", "after")  # a selection, to the top
    assert panel.shown() == ["all", "s1", "o2", "o1", {"g1": ["m1", "m2"]}]
    assert panel.move("o1", "g1", "into")
    assert panel.shown() == ["all", "s1", "o2", {"g1": ["o1", "m1", "m2"]}]
    assert panel.move("o1", "m2", "after")  # the order inside a group
    assert panel.shown() == ["all", "s1", "o2", {"g1": ["m1", "m2", "o1"]}]
    assert panel.move("m1", "o2", "before")  # out of the group
    assert panel.shown() == ["all", "s1", "m1", "o2", {"g1": ["m2", "o1"]}]
    assert panel.move("o2", "m2", "before")  # beside a member: into its group
    assert panel.shown() == ["all", "s1", "m1", {"g1": ["o2", "m2", "o1"]}]

    cmd.group("g2", "g1")
    panel.refresh()
    assert panel.shown() == ["all", "s1", "m1", {"g2": [{"g1": ["o2", "m2", "o1"]}]}]
    # not: "all", onto itself, a group into itself or into what it holds
    for move in (
        ("all", "m1", "after"),
        ("m1", "all", "before"),
        ("m1", "m1", "after"),
        ("m1", "s1", "into"),
        ("g2", "g2", "into"),
        ("g2", "g1", "into"),
        ("g2", "m2", "before"),
        ("m1", "gone", "after"),
    ):
        assert not panel.move(*move), move
    assert panel.shown() == ["all", "s1", "m1", {"g2": [{"g1": ["o2", "m2", "o1"]}]}]
    assert panel.move("g1", "s1", "before")  # a group leaves its group whole
    assert panel.shown() == ["all", {"g1": ["o2", "m2", "o1"]}, "s1", "m1", "g2"]

    # a filtered list moves the same rows; the hidden ones keep their places
    panel.filter.setText("m")
    assert panel.items["s1"].isHidden() and panel.move("m1", "g1", "before")
    panel.filter.setText("")
    assert panel.shown() == ["all", "m1", {"g1": ["o2", "m2", "o1"]}, "s1", "g2"]

    # the core holds order and membership: a session brings them back
    path = str(tmp_path / "moved.pse")
    cmd.save(path)
    cmd.reinitialize()
    cmd.load(path)
    panel.refresh()
    assert panel.shown() == ["all", "m1", {"g1": ["o2", "m2", "o1"]}, "s1", "g2"]


def test_move_with_the_keys(rows):
    panel = rows
    press = lambda name, step: (
        panel.tree.setCurrentItem(panel.items[name]),
        panel.move_current(step),
    )[1]
    assert press("o2", "up") and not press("o2", "up")  # "all" stays first
    assert panel.shown() == ["all", "o2", "o1", {"g1": ["m1", "m2"]}, "s1"]
    assert press("o2", "down")
    assert not press("o2", "in")  # the row above is no group
    assert press("s1", "in")
    assert panel.shown() == ["all", "o1", "o2", {"g1": ["m1", "m2", "s1"]}]
    assert press("m2", "up") and press("m2", "out") and not press("m2", "out")
    assert panel.shown() == ["all", "o1", "o2", {"g1": ["m1", "s1"]}, "m2"]
    assert not press("m2", "down")
    panel.filter.setText("o")  # the row above that is shown
    panel.tree.setCurrentItem(panel.items["o2"])
    assert panel.move_current("up")
    panel.filter.setText("")
    assert panel.shown() == ["all", "o2", "o1", {"g1": ["m1", "s1"]}, "m2"]


def test_drag_with_the_right_button(rows, monkeypatch):
    from PySide6 import QtTest
    from pymol.Qt import QtCore, QtGui, QtWidgets

    panel, Qt, QTest = rows, QtCore.Qt, QtTest.QTest
    panel.resize(300, 400)
    panel.show()
    view = panel.tree.viewport()
    menus = []
    monkeypatch.setattr(panel, "_context_menu", menus.append)

    def row(name, at=0.5):
        rect = panel.tree.visualItemRect(panel.items[name])
        return QtCore.QPoint(30, rect.top() + int(rect.height() * at))

    def send(kind, position, button=Qt.MouseButton.RightButton, held=None):
        held = button if held is None else held
        event = QtGui.QMouseEvent(
            kind,
            QtCore.QPointF(position),
            QtCore.QPointF(view.mapToGlobal(position)),
            button,
            held,
            Qt.KeyboardModifier.NoModifier,
        )
        QtWidgets.QApplication.sendEvent(view, event)

    Type, none = QtCore.QEvent.Type, Qt.MouseButton.NoButton

    def drag(name, to):
        send(Type.MouseButtonPress, row(name))
        send(Type.MouseMove, to, none, Qt.MouseButton.RightButton)
        shown = panel._mark.isVisible(), panel._mark.geometry()
        panel.refresh()  # the poll of the window must not move the rows now
        send(Type.MouseButtonRelease, to, held=none)
        assert not panel._mark.isVisible() and panel._drag is None
        return shown

    # a click without a drag opens the menu of the row, on release
    send(Type.MouseButtonPress, row("o1"))
    assert not menus
    send(Type.MouseButtonRelease, row("o1"), held=none)
    assert menus == [row("o1")] and "o1" in cmd.get_names()
    # the menu the system asks for with the mouse is ours already
    asked = QtGui.QContextMenuEvent(
        QtGui.QContextMenuEvent.Reason.Mouse, row("o1"), view.mapToGlobal(row("o1"))
    )
    QtWidgets.QApplication.sendEvent(view, asked)
    assert len(menus) == 1

    marked, line = drag("o2", row("o1", 0.2))  # above o1: a line there
    assert marked and line.height() == 2
    assert line.top() == panel.tree.visualItemRect(panel.items["o2"]).top() - 1
    assert panel.shown() == ["all", "o2", "o1", {"g1": ["m1", "m2"]}, "s1"]
    group = panel.tree.visualItemRect(panel.items["g1"])
    marked, frame = drag("o2", row("g1"))  # on the group: a frame around it
    assert marked and (frame.top(), frame.height()) == (group.top(), group.height())
    assert panel.shown() == ["all", "o1", {"g1": ["o2", "m1", "m2"]}, "s1"]
    under = QtCore.QPoint(30, panel.tree.visualItemRect(panel.items["s1"]).bottom() + 40)
    drag("m1", under)  # under the last row: out of the group, to the end
    assert panel.shown() == ["all", "o1", {"g1": ["o2", "m2"]}, "s1", "m1"]
    marked, _ = drag("g1", row("m2"))  # a group into itself: no mark, no move
    assert not marked
    drag("all", row("s1", 0.9))  # "all" is not moved
    assert panel.shown() == ["all", "o1", {"g1": ["o2", "m2"]}, "s1", "m1"]
    assert len(menus) == 1  # no menu after a drag
    # the left button is the visibility, as before
    QTest.mouseClick(view, Qt.MouseButton.LeftButton, pos=row("o1"))
    assert "o1" not in cmd.get_names("public_objects", enabled_only=1)


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


def test_rename_in_place():
    from unittest import mock

    from pymol.Qt import QtCore, QtWidgets
    from PySide6.QtTest import QTest
    from pmg_qt.object_panel import ObjectPanel

    Key = QtCore.Qt.Key
    events = QtWidgets.QApplication.processEvents
    cmd.fragment("ala")
    cmd.fragment("gly")
    cmd.select("sele", "name CA")
    panel = ObjectPanel(cmd)
    panel.show()
    panel.refresh()

    def open_editor():
        events()  # the editor opens once the caller has returned
        # a closed editor is only deleted by a running event loop
        return [e for e in panel.tree.findChildren(QtWidgets.QLineEdit) if e.isVisible()][-1]

    def edit(name, text, key=Key.Key_Return):
        assert panel.rename(name)
        editor = open_editor()
        shown = editor.text()
        editor.setText(text)
        QTest.keyClick(editor, key)
        events()
        return shown

    # Enter renames; a space becomes "_"
    assert edit("ala", "my ala") == "ala"
    assert "my_ala" in cmd.get_names() and "ala" not in cmd.get_names()
    assert "my_ala" in panel.items and "ala" not in panel.items
    # Esc, a taken name and an empty name do not
    edit("my_ala", "other", Key.Key_Escape)
    edit("my_ala", "gly")
    edit("my_ala", "  ")
    assert sorted(cmd.get_names()) == ["gly", "my_ala"]
    # a selection is edited without its brackets and gets them back
    assert edit("sele", "site") == "sele"
    assert "site" in cmd.get_names("selections")
    assert panel.items["site"].text(0) == "(site)"
    # "all" and unknown rows cannot be renamed
    assert not panel.rename("all")
    assert not panel.rename("nothing")
    # F2 is the current row
    panel.tree.setCurrentItem(panel.items["gly"])
    assert panel.rename()

    # the poll leaves an open editor alone and catches up afterwards
    editor = open_editor()
    cmd.fragment("ser")
    panel.refresh()
    assert editor.isVisible() and "ser" not in panel.items
    QTest.keyClick(editor, Key.Key_Escape)
    events()
    assert "ser" in panel.items and "gly" in panel.items

    # the "rename" rows of the menus: the panel when a window set the hook,
    # the wizard that types into the viewport without one
    rows = [r for r in menu.mol_action(cmd, "gly") if r[1].startswith("rename")]
    assert [r[2] for r in rows] == ['menu.rename("gly")']
    with mock.patch.object(menu, "rename_hook", panel.rename):
        cmd.do(rows[0][2], echo=0)
        editor = open_editor()
        assert cmd.get_wizard() is None and editor.text() == "gly"
        QTest.keyClick(editor, Key.Key_Escape)
    cmd.do(rows[0][2], echo=0)
    assert type(cmd.get_wizard()).__name__ == "Renaming"
    cmd.set_wizard()


def test_footer_icons():
    """The row under the object list (the window builds it): tinted icons,
    another tint while a switch is on, and the icon of a button with an
    action survives a click."""
    from pymol.Qt import QtGui, QtWidgets
    from pmg_qt import icons
    from pmg_qt.pymol_qt_gui import PyMOLQtGUI

    class Window(QtWidgets.QWidget):
        _set_footer_icons = PyMOLQtGUI._set_footer_icons

    for label in ("mouse mode", "seq", "ai assistant", "wizard", "command line"):
        assert label in icons.LABELS
    window = Window()
    window._set_footer_icons()  # before the row exists: nothing to do
    button, seq = QtWidgets.QToolButton(), QtWidgets.QToolButton()
    action = QtGui.QAction("SEQ", checkable=True)
    seq.setDefaultAction(action)
    window._footer_icons = ((button, "mouse mode"), (action, "seq"))
    window._set_footer_icons()
    assert not button.icon().isNull()
    action.trigger()
    assert seq.isChecked() and not seq.icon().isNull()
    Mode, State = QtGui.QIcon.Mode, QtGui.QIcon.State
    off = seq.icon().pixmap(16, 16, Mode.Normal, State.Off).toImage()
    assert seq.icon().pixmap(16, 16, Mode.Normal, State.On).toImage() != off


def test_footer_rows():
    """32c: the buttons under the object list have an icon of 20 px beside
    a short text and are 32 px high. One row while it fits; in a narrower
    panel the buttons after the second are a second row. Nothing is cut
    off or overlaps, and the panel may be as narrow as the wider row."""
    from pymol.Qt import QtCore, QtWidgets
    from pmg_qt.object_panel import Footer

    # inside a host, as in the panel: a window of its own could not be
    # made narrower than one row. Laid out without a window on the screen.
    host = QtWidgets.QWidget()
    host.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen)
    host.resize(900, 100)
    footer = Footer()
    footer.setParent(host)
    buttons = []
    for text in ("Viewing", "SEQ", "Chat", "Wizard", "Cmd"):
        button = QtWidgets.QToolButton()
        button.setText(text)
        button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        footer.addWidget(button)
        buttons.append(button)
    assert all(b.iconSize() == QtCore.QSize(20, 20) for b in buttons)
    one_row = footer._width(buttons)
    host.show()

    def laid_out(width):
        footer.resize(width, 80)
        for _ in range(3):
            QtWidgets.QApplication.processEvents()
        boxes = [b.geometry() for b in buttons]
        assert all(b.width() >= b.sizeHint().width() for b in buttons)  # not cut
        assert all(box.right() < width and box.height() >= 32 for box in boxes)
        assert not any(a.intersects(b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
        return [sorted({box.y() for box in boxes}).index(box.y()) for box in boxes]

    try:
        assert laid_out(one_row + 40) == [0, 0, 0, 0, 0]
        assert laid_out(one_row) == [0, 0, 0, 0, 0]  # it just fits
        assert laid_out(one_row - 1) == [0, 0, 1, 1, 1]
        two_rows = footer.minimumSizeHint().width()
        assert two_rows == max(footer._width(buttons[:2]), footer._width(buttons[2:]))
        assert two_rows < one_row
        assert laid_out(two_rows) == [0, 0, 1, 1, 1]  # the narrowest panel
        assert laid_out(one_row + 40) == [0, 0, 0, 0, 0]  # and back
        # a longer name of the mouse mode: the row no longer fits
        footer.resize(one_row, 80)
        buttons[0].setText("Lights Manip.")
        assert laid_out(one_row) == [0, 0, 1, 1, 1]
        # the keyboard walks the buttons in their order in both layouts
        chain = [buttons[0]]
        while len(chain) < 5:
            chain.append(chain[-1].nextInFocusChain())
        assert chain == buttons
    finally:
        host.close()


@testing.requires("gui")
def test_footer_in_the_window():
    """32c, in the real window: the five buttons with their short texts,
    their whole names for a screen reader, and their actions."""
    import pymol
    from pymol.Qt import QtCore, QtWidgets

    window = pymol.gui.get_qtwindow()
    footer = window.object_panel.footer
    buttons = [target for target, _ in window._footer_icons]
    assert buttons == footer.buttons
    assert [b.text() for b in buttons][1:] == ["SEQ", "Chat", "Wizard", "Cmd"]
    assert [b.accessibleName() or b.text() for b in buttons][1:] == [
        "Sequence tab", "AI assistant", "Wizard", "Command line and log"]
    assert buttons[0].accessibleName().startswith("Mouse mode: ")
    Style = QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    assert all(b.toolButtonStyle() == Style and not b.icon().isNull() for b in buttons)
    assert all(b.iconSize().width() == 20 and b.height() >= 32 for b in buttons)
    # what a click does is what it did: menus, the tab, the switch
    mouse, seq, chat, wizard, command = buttons
    assert mouse.menu() is window.menudict["Mouse"]
    assert wizard.menu() is window.menudict["Wizard"]
    assert [a.text() for a in chat.menu().actions() if a.text()][0] == "Chat"
    assert "Show in viewport" in [a.text() for a in seq.menu().actions()]
    seq.click()
    assert window.command_tabs.currentWidget() is window.sequence_page
    shown = window.ext_window.isVisible()
    command.click()
    QtWidgets.QApplication.processEvents()
    assert window.ext_window.isVisible() != shown and command.isChecked() != shown
    command.click()
    # two rows in a narrow panel, one in a wide one, never a wider panel
    for width, rows in ((240, 2), (footer._width(buttons) + 30, 1)):
        window.resizeDocks([window.object_panel], [width], QtCore.Qt.Orientation.Horizontal)
        for _ in range(5):
            QtWidgets.QApplication.processEvents()
        assert len({b.y() for b in buttons}) == rows, width
        assert max(b.x() + b.width() for b in buttons) <= footer.width()
        assert abs(window.object_panel.width() - width) <= 2


@testing.requires("gui")
def test_mouse_mode_button_is_as_wide_as_its_content():
    """37e, in the real window: the short name of the mode, the whole one in
    the tooltip, and no growth into the spare width of a wide panel."""
    import time

    import pymol
    from pymol.Qt import QtCore, QtWidgets

    window = pymol.gui.get_qtwindow()
    button = window._footer_icons[0][0]

    def shows(text):  # the window hears of a changed setting a moment later
        deadline = time.monotonic() + 3
        while button.text() != text and time.monotonic() < deadline:
            QtWidgets.QApplication.processEvents()
            time.sleep(0.02)
        return button.text() == text

    cmd.edit_mode(0)
    assert shows("Viewing")
    assert button.toolTip() == "Mouse mode: 3-Button Viewing"
    window.resizeDocks([window.object_panel], [420], QtCore.Qt.Orientation.Horizontal)
    QtWidgets.QApplication.processEvents()
    assert window.object_panel.width() > 400
    assert button.width() == button.sizeHint().width() < 120
    cmd.edit_mode(1)
    assert shows("Editing")
    assert button.toolTip() == "Mouse mode: 3-Button Editing"
    QtWidgets.QApplication.processEvents()  # the row is laid out again
    assert button.width() == button.sizeHint().width()
    cmd.edit_mode(0)
