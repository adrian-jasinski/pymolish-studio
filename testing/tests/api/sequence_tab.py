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
