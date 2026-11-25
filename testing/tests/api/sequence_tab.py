"""
The Sequence tab of the command panel (pmg_qt/sequence_tab.py) and the two
calls it reads the sequence viewer of the core with: seq_rows and seq_mouse.
The rows exist without seq_view, which only puts them into the viewport.
Headless (offscreen QApplication).
"""

import os

import pymol
import pytest
from pymol import cmd


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def selected():
    residues = set()
    cmd.iterate("?sele", "residues.add(int(resi))", space={"residues": residues})
    return sorted(residues)


def click(char, mod=0, row=1):
    for kind in (0, 2):  # press, release
        pymol._cmd.seq_mouse(cmd._COb, kind, 0, row, char, mod)


def test_rows_and_mouse():
    serial, rows, marks, colors, fill = pymol._cmd.seq_rows(cmd._COb, -1)
    assert rows == [] and marks == [] and len(colors) == 3 and fill == "-"
    click(3)  # no rows, no handler yet: nothing happens

    cmd.fab("ACDEFGHIKL", "m")
    assert not cmd.get_setting_boolean("seq_view")
    serial, rows, marks, _, _ = pymol._cmd.seq_rows(cmd._COb, serial)
    (labels, label_flags, _, _), (text, flags, columns, _) = rows
    assert label_flags == 1 and labels.startswith("/m") and flags == 0
    offsets, starts, stops = columns[0::4], columns[1::4], columns[2::4]
    letters = {text[s:e]: o for o, s, e in zip(offsets, starts, stops)}
    assert "".join(k for k in letters if k.strip()) == "ACDEFGHIKL"
    assert pymol._cmd.seq_rows(cmd._COb, serial)[1] is None  # nothing new
    assert not any(marks[1])

    click(letters["C"])
    assert selected() == [2]
    click(letters["E"])  # the next one is added
    assert selected() == [2, 4]
    click(letters["H"], mod=1)  # Shift: the range from the last click
    assert selected() == [2, 4, 5, 6, 7]
    click(letters["F"])  # a selected one is taken out
    assert selected() == [2, 4, 6, 7]
    # a drag from K to L
    pymol._cmd.seq_mouse(cmd._COb, 0, 0, 1, letters["K"], 0)
    pymol._cmd.seq_mouse(cmd._COb, 1, -1, 0, letters["L"], 0)  # the row stays
    pymol._cmd.seq_mouse(cmd._COb, 2, 0, 1, letters["L"], 0)
    assert selected() == [2, 4, 6, 7, 9, 10]
    marks = pymol._cmd.seq_rows(cmd._COb, serial)[2][1]
    marked = [o for o, mark in zip(offsets, marks) if mark]
    assert marked == [letters[k] for k in "CEGHKL"]

    # an object that switches seq_view off for itself is not listed
    cmd.fab("GG", "other")
    assert len(pymol._cmd.seq_rows(cmd._COb, -1)[1]) == 4
    cmd.set("seq_view", 0, "other")
    assert len(pymol._cmd.seq_rows(cmd._COb, -1)[1]) == 2
    cmd.set("seq_view", 1)  # in the viewport: the rows the setting gives
    assert len(pymol._cmd.seq_rows(cmd._COb, -1)[1]) == 2


def test_tab():
    from pmg_qt.sequence_tab import MARGIN, SequenceTab
    from pymol.Qt import QtCore
    from PySide6.QtTest import QTest

    Qt = QtCore.Qt
    tab = SequenceTab(cmd)
    tab.resize(300, 80)
    tab.grab()  # nothing to draw yet
    cmd.fab("ACDEFGHIKL" * 10, "m")
    tab.refresh()
    assert [row[1] for row in tab.rows] == [1, 0] and tab.title == 2
    offsets = tab.rows[1][2]
    assert offsets == sorted(offsets) and tab.rows[0][2] == sorted(tab.rows[0][2])
    assert tab.horizontalScrollBar().maximum() > 0
    assert not tab.verticalScrollBar().maximum()
    width, height = tab.cell()

    def at(column):
        x = MARGIN + (offsets[column] - tab.horizontalScrollBar().value() + 0.5) * width
        return QtCore.QPoint(int(x), int(1.5 * height))

    view, left = tab.viewport(), Qt.MouseButton.LeftButton
    first = offsets.index(5)  # the columns before it are blank
    QTest.mouseClick(view, left, Qt.KeyboardModifier.NoModifier, at(first + 2))
    assert selected() == [3] and tab.state[0][1][first + 2]
    tab.horizontalScrollBar().setValue(40)
    QTest.mouseClick(view, left, Qt.KeyboardModifier.NoModifier, at(first + 50))
    assert selected() == [3, 51]
    QTest.mouseDClick(view, left, Qt.KeyboardModifier.NoModifier, at(first + 50))
    assert selected() == [3]  # the second press of a double click
    assert not tab.grab().isNull()
    cmd.delete("m")
    tab.refresh()
    assert tab.rows == []


def test_options_row():
    """37f: the lists over the sequence are the settings of Display >
    Sequence Mode, and a button opens the alignment window."""
    from collections import defaultdict

    from pmg_qt.sequence_tab import Options, SequenceTab
    from pymol._gui import SEQUENCE_OPTIONS, PyMOLDesktopGUI
    from pymol.Qt import QtWidgets

    callbacks, opened = defaultdict(list), []
    cmd.fab("ACDEFGHIKL", "m")
    row = Options(cmd, callbacks, lambda: opened.append(1))
    tab = SequenceTab(cmd)
    tab.refresh()
    codes = tab.rows[1][0]

    for setting, title, choices in SEQUENCE_OPTIONS:
        box = row.lists[setting]
        assert [box.itemText(i) for i in range(box.count())] == [c[0] for c in choices]
        assert box.currentData() == cmd.get_setting_int(setting)  # as it is now
        assert box.accessibleName() and box.toolTip()
        for index, (label, value) in enumerate(choices):  # picked in the list
            box.setCurrentIndex(index)
            box.activated.emit(index)
            assert cmd.get_setting_int(setting) == value
        for label, value in choices:  # set by a command or the Display menu
            cmd.set(setting, value)
            for callback in callbacks[cmd.setting._get_index(setting)]:
                callback(cmd.get_setting_tuple(setting)[1][0])
            assert box.currentText() == label
        cmd.set(setting, choices[0][1])

    # the names of the residues: other rows, and a click still finds them
    box = row.lists["seq_view_format"]
    box.setCurrentIndex(box.findText("Residue Names"))
    box.activated.emit(box.currentIndex())
    tab.refresh()
    text, _, offsets, starts, stops = tab.rows[1][:5]
    assert text != codes and "CYS" in text
    names = {text[s:e].strip(): o for o, s, e in zip(offsets, starts, stops)}
    click(names["ASP"])
    assert selected() == [3]
    cmd.set("seq_view_format", 0)

    row.align.click()
    assert opened == [1] and isinstance(row.align, QtWidgets.QPushButton)

    # the Display menu is built from the same lists
    from unittest import mock

    data = PyMOLDesktopGUI.get_menudata(mock.MagicMock(), cmd)  # any window
    menus = {label: rows for _, label, rows in data}
    display = {row[1]: row for row in menus["Display"] if len(row) > 2}
    mode = display["Sequence Mode"][2]
    rows = [(r[1], r[2], r[3]) if r[0] == "radio" else None for r in mode]
    expected = []
    for setting, _, choices in SEQUENCE_OPTIONS:
        expected += [None] + [(label, setting, value) for label, value in choices]
    assert rows == expected[1:] and len(rows) == 14


def test_tab_font_buttons(monkeypatch, tmp_path):
    """37g: A-, A+ and Reset beside the tabs size the text of the tab that
    is shown, each tab for itself, and the sizes come back at the next start."""
    from pmg_qt.pymol_qt_gui import TabFontButtons
    from pmg_qt.sequence_tab import MARGIN, SequenceTab
    from pymol.Qt import QtCore, QtWidgets
    from PySide6.QtTest import QTest

    ini = str(tmp_path / "settings.ini")
    Settings = QtCore.QSettings
    monkeypatch.setattr(
        QtCore, "QSettings", lambda *a: Settings(ini, Settings.Format.IniFormat)
    )
    cmd.fab("ACDEFGHIKL" * 10, "m")

    def window():
        tabs = QtWidgets.QTabWidget()
        log, entry = (
            QtWidgets.QPlainTextEdit("a long line " * 40),
            QtWidgets.QLineEdit(),
        )
        font = log.font()
        font.setPointSizeF(9)
        log.setFont(font)
        sequence = SequenceTab(cmd)
        history, prompt = QtWidgets.QPlainTextEdit(), QtWidgets.QLineEdit()
        for title, widgets in (
            ("Command", (log, entry)),
            ("Sequence", (sequence,)),
            ("Chat", (history, prompt)),
        ):
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            for widget in widgets:
                layout.addWidget(widget)
            tabs.addTab(page, title)
        targets = {
            "Command": (log, entry),
            "Sequence": (sequence,),
            "Chat": (history, prompt),
        }
        buttons = TabFontButtons(tabs, targets)
        tabs.setCornerWidget(buttons)
        tabs.resize(600, 160)
        tabs.show()
        sequence.refresh()
        return tabs, buttons, targets

    def sizes(targets):
        return {t: [w.font().pointSizeF() for w in ws] for t, ws in targets.items()}

    tabs, buttons, targets = window()
    start = sizes(targets)
    smaller, larger, reset = buttons.findChildren(QtWidgets.QToolButton)
    assert [b.text() for b in (smaller, larger, reset)] == ["A−", "A+", "Reset"]
    for button in (smaller, larger, reset):  # reached with Tab, and explained
        assert (
            button.toolTip() and button.focusPolicy() & QtCore.Qt.FocusPolicy.TabFocus
        )
    assert start["Command"][0] == 9

    larger.click()
    larger.click()  # the Command tab is shown: its log and its entry
    assert sizes(targets)["Command"] == [s + 2 for s in start["Command"]]
    assert sizes(targets)["Chat"] == start["Chat"]
    assert sizes(targets)["Sequence"] == start["Sequence"]
    assert (
        targets["Command"][0].font().family()
        == tabs.widget(0).findChild(QtWidgets.QPlainTextEdit).font().family()
    )

    # the Sequence tab: other cells, other scroll range, and a click still
    # finds the residue under it
    sequence = targets["Sequence"][0]
    tabs.setCurrentIndex(1)
    QtWidgets.QApplication.processEvents()
    width, _ = sequence.cell()
    reach = sequence.horizontalScrollBar().maximum()
    for _ in range(4):
        larger.click()
    assert sizes(targets)["Sequence"] == [start["Sequence"][0] + 4]
    wide, height = sequence.cell()
    assert wide > width and sequence.horizontalScrollBar().maximum() > reach
    offsets = sequence.rows[1][2]
    first = offsets.index(5)
    x = MARGIN + (offsets[first + 3] + 0.5) * wide
    QTest.mouseClick(
        sequence.viewport(),
        QtCore.Qt.MouseButton.LeftButton,
        QtCore.Qt.KeyboardModifier.NoModifier,
        QtCore.QPoint(int(x), int(1.5 * height)),
    )
    assert selected() == [4]
    assert sequence.font().family() == SequenceTab(cmd).font().family()

    tabs.setCurrentIndex(2)
    smaller.click()
    assert sizes(targets)["Chat"] == [s - 1 for s in start["Chat"]]
    for _ in range(60):  # never unreadable
        smaller.click()
    assert min(sizes(targets)["Chat"]) == TabFontButtons.SMALLEST

    # the next start: each tab has its size again
    again, buttons2, targets2 = window()
    assert sizes(targets2)["Command"] == [s + 2 for s in start["Command"]]
    assert sizes(targets2)["Sequence"] == [start["Sequence"][0] + 4]
    assert min(sizes(targets2)["Chat"]) == TabFontButtons.SMALLEST
    again.setCurrentIndex(2)
    buttons2.change(0)  # Reset: this tab only
    assert sizes(targets2)["Chat"] == start["Chat"]
    assert sizes(targets2)["Command"] == [s + 2 for s in start["Command"]]
    third, _, targets3 = window()
    assert sizes(targets3)["Chat"] == start["Chat"]
    for _ in range(60):
        buttons2.change(1)
    assert max(sizes(targets2)["Chat"]) == TabFontButtons.LARGEST
