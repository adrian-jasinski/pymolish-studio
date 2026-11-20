"""
Property table: rows and nesting, the In dot, columns from object properties
and SDF data fields, sorting by value, the filter, row numbers, identity
after rename and delete; editing cells and names, columns added, renamed and
deleted, copy and paste of a block. split_states keeps properties.
Headless (offscreen QApplication).
"""

import os

import pytest

from pymol import cmd


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _table():
    from pymol.Qt import QtWidgets
    from pmg_qt.property_table import PropertyTable

    window = QtWidgets.QMainWindow()
    viewport = QtWidgets.QWidget()
    window.setCentralWidget(viewport)
    panel = QtWidgets.QDockWidget(window)
    table = PropertyTable(cmd, window, viewport, panel)
    table._window = window  # keep it alive
    table.refresh()
    return table


def _shown(table, column=2):
    """Texts of one column over the rows shown, in the order shown."""
    from pymol.Qt import QtWidgets

    walk = QtWidgets.QTreeWidgetItemIterator(
        table.tree, QtWidgets.QTreeWidgetItemIterator.IteratorFlag.NotHidden
    )
    texts = []
    while walk.value():
        texts.append(walk.value().text(column))
        walk += 1
    return texts


def _scene():
    cmd.fragment("ala", "lig_a")
    cmd.fragment("gly", "lig_b")
    cmd.fragment("ser", "lig_c")
    cmd.fragment("trp", "protein")
    cmd.group("poses", "lig_a lig_b lig_c")
    cmd.select("sele", "name CA")
    for name, score in (("lig_a", -6.5), ("lig_b", -10.25), ("lig_c", -8)):
        cmd.set_property("score", score, name)
    cmd.set_property("note", "best", "lig_b")


def test_rows_and_columns():
    from pymol.Qt import QtCore

    _scene()
    table = _table()
    tree = table.tree
    labels = [tree.headerItem().text(c) for c in range(tree.columnCount())]
    assert labels == ["Row", "In", "Name", "score", "note"]
    # no row for "all" or a selection; members nest under their group
    assert _shown(table) == ["protein", "poses", "lig_a", "lig_b", "lig_c"]
    assert table.items["lig_a"].parent() is table.items["poses"]
    assert tree.treePosition() == 2
    # numbers over the object rows, none for the group
    assert _shown(table, 0) == ["1", "", "2", "3", "4"]
    assert table.items["lig_b"].text(3) == "-10.25"
    assert table.items["lig_c"].text(3) == "-8" and table.items["lig_a"].text(4) == ""
    right = QtCore.Qt.AlignmentFlag.AlignRight
    assert table.items["lig_b"].textAlignment(3) & right
    assert not table.items["lig_b"].textAlignment(4) & right


def test_in_dot():
    from pymol.Qt import QtCore

    Checked = QtCore.Qt.CheckState.Checked
    _scene()
    table = _table()
    item = table.items["lig_a"]
    assert item.checkState(1) == Checked
    table._clicked(item, 1)
    assert "lig_a" not in cmd.get_names(enabled_only=1)
    assert item.checkState(1) != Checked
    table._clicked(item, 1)
    assert "lig_a" in cmd.get_names(enabled_only=1)
    # a click elsewhere on the row changes nothing
    table._clicked(item, 2)
    assert "lig_a" in cmd.get_names(enabled_only=1)
    # only this one
    table._toggle(table.items["protein"], only=True)
    assert cmd.get_names(enabled_only=1) == ["protein"]
    # the command line is followed at the next poll
    cmd.enable("lig_b")
    table.refresh()
    assert table.items["lig_b"].checkState(1) == Checked


def test_sort_filter_identity():
    from pymol.Qt import QtCore

    Order = QtCore.Qt.SortOrder
    _scene()
    cmd.ungroup("poses")
    cmd.delete("poses")
    table = _table()
    tree = table.tree
    # by value, not by text: -10.25 is below -8; the empty cell is last
    tree.sortByColumn(3, Order.AscendingOrder)
    assert _shown(table) == ["lig_b", "lig_c", "lig_a", "protein"]
    assert _shown(table, 0) == ["1", "2", "3", "4"]  # numbers follow the sort
    tree.sortByColumn(0, Order.AscendingOrder)  # the order of the Objects panel
    assert _shown(table) == ["lig_a", "lig_b", "lig_c", "protein"]

    table.filter.setText("best")  # a value
    assert _shown(table) == ["lig_b"] and _shown(table, 0) == ["1"]
    table.filter.setText("LIG_")  # a name, any case
    assert _shown(table) == ["lig_a", "lig_b", "lig_c"]
    table.filter.setText("")

    # a row is its object, whatever its number: rename and delete under a sort
    tree.sortByColumn(3, Order.AscendingOrder)
    cmd.set_name("lig_b", "winner")
    cmd.delete("lig_c")
    table.refresh()
    assert _shown(table) == ["winner", "lig_a", "protein"]
    assert table.items["winner"].text(4) == "best"
    # a property that no object has any more loses its column
    cmd.delete("winner")
    table.refresh()
    labels = [tree.headerItem().text(c) for c in range(tree.columnCount())]
    assert labels == ["Row", "In", "Name", "score"]


def test_sdf_fields_and_split_states(tmp_path):
    cmd.fragment("ala", "m1")
    cmd.fragment("gly", "m2")
    records = []
    for name, score in (("m1", "-6.4"), ("m2", "-5.1")):
        mol = cmd.get_str("mol", name).rstrip("\n")
        records.append(mol + "\n> <docking_score>\n" + score + "\n\n$$$$\n")
    path = str(tmp_path / "two.sdf")
    with open(path, "w") as handle:
        handle.write("".join(records))
    cmd.delete("*")
    cmd.load(path, "hits")
    cmd.split_states("hits", prefix="pose")
    assert cmd.get_property("docking_score", "pose0001") == -6.4
    assert cmd.get_property("docking_score", "pose0002") == -5.1
    cmd.delete("hits")
    table = _table()
    assert [table.items[n].text(3) for n in ("pose0001", "pose0002")] == ["-6.4", "-5.1"]


def test_many_rows():
    """1,000 objects with 20 properties: one poll stays cheap."""
    import time

    cmd.fragment("gly", "m0")
    for i in range(1, 1000):
        cmd.create("m%d" % i, "m0", zoom=0)
        for j in range(20):
            cmd.set_property("p%d" % j, i * 0.5 + j, "m%d" % i)
    table = _table()
    assert table.tree.columnCount() == 23
    start = time.time()
    for _ in range(5):
        table.refresh()  # nothing changed: read and compare
    assert (time.time() - start) / 5 < 0.1


def _edit(item, column, text):
    """What a closed editor does; the table applies it from the event loop."""
    from pymol.Qt import QtWidgets

    item.setText(column, text)
    QtWidgets.QApplication.processEvents()


def test_edit_cells():
    _scene()
    table = _table()
    a, b, c = (table.items[n] for n in ("lig_a", "lig_b", "lig_c"))
    # the text of a cell becomes a whole number, a number or text
    for text, value in (("-7.25", -7.25), ("12", 12), ("see note", "see note"), (" 3e2 ", 300.0)):
        _edit(a, 3, text)  # what a closed editor does
        assert cmd.get_property("score", "lig_a") == value
        assert type(cmd.get_property("score", "lig_a")) is type(value)
    # an emptied cell deletes the property
    _edit(a, 3, "")
    assert "score" not in (cmd.get_property_list("lig_a") or ())
    assert a.text(3) == ""
    # with several cells of the column selected, the edit goes to all
    b.setSelected(False)
    for item in (b, c):
        table.tree.setCurrentItem(item, 3, table.tree.selectionModel().SelectionFlag.Select)
    _edit(c, 3, "1.5")
    assert [cmd.get_property("score", n) for n in ("lig_b", "lig_c")] == [1.5, 1.5]
    # a new property for an object that had none
    _edit(table.items["protein"], 4, "target")
    assert cmd.get_property("note", "protein") == "target"
    # Row and In have no editor
    assert table.tree.itemDelegateForColumn(0).createEditor(None, None, None) is None


def test_edit_name():
    _scene()
    table = _table()
    _edit(table.items["lig_a"], 2, "pose one")
    assert "pose_one" in cmd.get_names() and "lig_a" not in cmd.get_names()
    assert table.items["pose_one"].text(3) == "-6.5"  # its values came along
    _edit(table.items["pose_one"], 2, "lig_b")  # taken: refused, text back
    _edit(table.items["pose_one"], 2, " ")
    assert "pose_one" in cmd.get_names()
    assert table.items["pose_one"].text(2) == "pose_one"


def test_columns():
    _scene()
    table = _table()
    tree = table.tree

    def labels():
        return [tree.headerItem().text(c) for c in range(3, tree.columnCount())]

    assert table.add_column(" stars ")
    assert not table.add_column("stars") and not table.add_column("Name")
    assert not table.add_column("")
    assert labels() == ["score", "note", "stars"]
    table.refresh()  # an empty column of the user outlives a poll
    assert labels() == ["score", "note", "stars"]
    _edit(table.items["lig_a"], 5, "3")
    assert cmd.get_property("stars", "lig_a") == 3

    assert table.rename_column("score", "docking score")
    assert not table.rename_column("note", "stars")
    assert labels() == ["docking score", "note", "stars"]  # it keeps its place
    assert cmd.get_property("docking score", "lig_b") == -10.25
    assert "score" not in cmd.get_property_list("lig_b")

    table.delete_column("docking score")
    assert labels() == ["note", "stars"]
    assert all("docking score" not in (cmd.get_property_list(n) or ()) for n in ("lig_a", "lig_b", "lig_c"))


def test_copy_paste():
    from pymol.Qt import QtWidgets

    Select = QtWidgets.QAbstractItemView.SelectionMode  # noqa: F841
    _scene()
    cmd.ungroup("poses")
    cmd.delete("poses")
    table = _table()
    tree = table.tree
    flag = tree.selectionModel().SelectionFlag
    clipboard = QtWidgets.QApplication.clipboard()

    tree.clearSelection()
    for name in ("lig_a", "lig_b"):
        for column in (2, 3, 4):
            tree.setCurrentItem(table.items[name], column, flag.Select)
    table.copy()
    assert clipboard.text() == "lig_a\t-6.5\t\nlig_b\t-10.25\tbest"

    # a block from a spreadsheet, pasted at lig_b / score: to the right and down
    clipboard.setText("1\tone\n2\ttwo\n3\tthree\n")
    tree.clearSelection()
    tree.setCurrentItem(table.items["lig_b"], 3, flag.Select)
    table.paste()
    assert [cmd.get_property("score", n) for n in ("lig_a", "lig_b", "lig_c", "protein")] == [-6.5, 1, 2, 3]
    assert [cmd.get_property("note", n) for n in ("lig_b", "lig_c", "protein")] == ["one", "two", "three"]

    # a paste never renames and never touches Row or In
    clipboard.setText("x\ty\tz\t9")
    tree.clearSelection()
    tree.setCurrentItem(table.items["lig_a"], 0, flag.Select)
    table.paste()
    assert "lig_a" in cmd.get_names() and cmd.get_property("score", "lig_a") == 9

    # Delete empties the selected cells
    tree.clearSelection()
    for name in ("lig_a", "lig_b"):
        tree.setCurrentItem(table.items[name], 3, flag.Select)
    table._write(table._selected_cells(), None)
    assert all("score" not in (cmd.get_property_list(n) or ()) for n in ("lig_a", "lig_b"))
    assert cmd.get_property("score", "lig_c") == 2


def test_export(tmp_path):
    from pymol import tables
    from pymol.Qt import QtCore

    _scene()
    table = _table()
    table.tree.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)
    table.filter.setText("lig_")
    table.tree.header().hideSection(4)  # note
    path = str(tmp_path / "shown.csv")
    table.export(path)
    # the rows shown in the order shown, the columns shown; no group row
    assert tables.read_table(path) == [
        ["name", "score"],
        ["lig_b", "-10.25"],
        ["lig_c", "-8"],
        ["lig_a", "-6.5"],
    ]
