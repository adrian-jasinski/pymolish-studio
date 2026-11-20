"""
Property table: rows and nesting, the In dot, columns from object properties
and SDF data fields, sorting by value, the filter, row numbers, identity
after rename and delete. split_states keeps properties.
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
