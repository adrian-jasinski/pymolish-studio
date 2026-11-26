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
    assert labels == ["Row", "In", "Name", "stars", "score", "note"]
    # no row for "all" or a selection; members nest under their group
    assert _shown(table) == ["protein", "poses", "lig_a", "lig_b", "lig_c"]
    assert table.items["lig_a"].parent() is table.items["poses"]
    assert tree.treePosition() == 2
    # numbers over the object rows, none for the group
    assert _shown(table, 0) == ["1", "", "2", "3", "4"]
    assert table.items["lig_b"].text(4) == "-10.25"
    assert table.items["lig_c"].text(4) == "-8" and table.items["lig_a"].text(5) == ""
    # 30b: every value starts at the left of its cell, numbers too; the
    # row number stays at the right
    right = QtCore.Qt.AlignmentFlag.AlignRight
    assert not table.items["lig_b"].textAlignment(4) & right
    assert not table.items["lig_b"].textAlignment(5) & right
    assert table.items["lig_b"].textAlignment(0) & right


def test_only_molecules_are_asked(capfd):
    # 30b: a group, a measurement and a map have no properties. Asked for
    # them the core prints "ExecutiveGetProperty: objname=... not found",
    # twice a second while the table is open; writing to one raises.
    _scene()
    cmd.distance("far", "lig_a and name N", "lig_a and name C")
    capfd.readouterr()
    table = _table()
    table.refresh(force=True)
    assert "far" in table.items and "poses" in table.items
    table._write([(table.items["poses"], 4), (table.items["far"], 4)], "5")
    QtWidgets = __import__("pymol.Qt", fromlist=["QtWidgets"]).QtWidgets
    table.tree.setCurrentItem(table.items["poses"], 4)
    QtWidgets.QApplication.clipboard().setText("7")
    table.paste()
    printed = capfd.readouterr()
    assert "not found" not in printed.out + printed.err
    assert cmd.get_property("score", "lig_b") == -10.25  # the members keep theirs
    cmd.get_property_list("poses")  # what the table no longer does
    assert "not found" in capfd.readouterr().out


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
    tree.sortByColumn(4, Order.AscendingOrder)
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
    tree.sortByColumn(4, Order.AscendingOrder)
    cmd.set_name("lig_b", "winner")
    cmd.delete("lig_c")
    table.refresh()
    assert _shown(table) == ["winner", "lig_a", "protein"]
    assert table.items["winner"].text(5) == "best"
    # a property that no object has any more loses its column
    cmd.delete("winner")
    table.refresh()
    labels = [tree.headerItem().text(c) for c in range(tree.columnCount())]
    assert labels == ["Row", "In", "Name", "stars", "score"]


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
    assert [table.items[n].text(4) for n in ("pose0001", "pose0002")] == [
        "-6.4",
        "-5.1",
    ]


def test_many_rows():
    """1,000 objects with 20 properties: one poll stays cheap."""
    import time

    cmd.fragment("gly", "m0")
    for i in range(1, 1000):
        cmd.create("m%d" % i, "m0", zoom=0)
        for j in range(20):
            cmd.set_property("p%d" % j, i * 0.5 + j, "m%d" % i)
    table = _table()
    assert table.tree.columnCount() == 24
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
    for text, value in (
        ("-7.25", -7.25),
        ("12", 12),
        ("see note", "see note"),
        (" 3e2 ", 300.0),
    ):
        _edit(a, 4, text)  # what a closed editor does
        assert cmd.get_property("score", "lig_a") == value
        assert type(cmd.get_property("score", "lig_a")) is type(value)
    # an emptied cell deletes the property
    _edit(a, 4, "")
    assert "score" not in (cmd.get_property_list("lig_a") or ())
    assert a.text(4) == ""
    # with several cells of the column selected, the edit goes to all
    b.setSelected(False)
    for item in (b, c):
        table.tree.setCurrentItem(
            item, 4, table.tree.selectionModel().SelectionFlag.Select
        )
    _edit(c, 4, "1.5")
    assert [cmd.get_property("score", n) for n in ("lig_b", "lig_c")] == [1.5, 1.5]
    # a new property for an object that had none
    _edit(table.items["protein"], 5, "target")
    assert cmd.get_property("note", "protein") == "target"
    # Row and In have no editor
    assert table.tree.itemDelegateForColumn(0).createEditor(None, None, None) is None


def test_edit_name():
    _scene()
    table = _table()
    _edit(table.items["lig_a"], 2, "pose one")
    assert "pose_one" in cmd.get_names() and "lig_a" not in cmd.get_names()
    assert table.items["pose_one"].text(4) == "-6.5"  # its values came along
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

    assert table.add_column(" comment ")
    assert (
        not table.add_column("comment")
        and not table.add_column("stars")
        and not table.add_column("Name")
    )
    assert not table.add_column("")
    assert labels() == ["stars", "score", "note", "comment"]
    table.refresh()  # an empty column of the user outlives a poll
    assert labels() == ["stars", "score", "note", "comment"]
    _edit(table.items["lig_a"], 6, "3")
    assert cmd.get_property("comment", "lig_a") == 3

    assert table.rename_column("score", "docking score")
    assert not table.rename_column("note", "comment")
    assert labels() == [
        "stars",
        "docking score",
        "note",
        "comment",
    ]  # it keeps its place
    assert cmd.get_property("docking score", "lig_b") == -10.25
    assert "score" not in cmd.get_property_list("lig_b")

    table.delete_column("docking score")
    assert labels() == ["stars", "note", "comment"]
    assert all(
        "docking score" not in (cmd.get_property_list(n) or ())
        for n in ("lig_a", "lig_b", "lig_c")
    )


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
        for column in (2, 4, 5):
            tree.setCurrentItem(table.items[name], column, flag.Select)
    table.copy()
    assert clipboard.text() == "lig_a\t-6.5\t\nlig_b\t-10.25\tbest"

    # a block from a spreadsheet, pasted at lig_b / score: to the right and down
    clipboard.setText("1\tone\n2\ttwo\n3\tthree\n")
    tree.clearSelection()
    tree.setCurrentItem(table.items["lig_b"], 4, flag.Select)
    table.paste()
    assert [
        cmd.get_property("score", n) for n in ("lig_a", "lig_b", "lig_c", "protein")
    ] == [-6.5, 1, 2, 3]
    assert [cmd.get_property("note", n) for n in ("lig_b", "lig_c", "protein")] == [
        "one",
        "two",
        "three",
    ]

    # a paste never renames and never touches Row or In
    clipboard.setText("x\ty\tz\t\t9")
    tree.clearSelection()
    tree.setCurrentItem(table.items["lig_a"], 0, flag.Select)
    table.paste()
    assert "lig_a" in cmd.get_names() and cmd.get_property("score", "lig_a") == 9

    # Delete empties the selected cells
    tree.clearSelection()
    for name in ("lig_a", "lig_b"):
        tree.setCurrentItem(table.items[name], 4, flag.Select)
    table._write(table._selected_cells(), None)
    assert all(
        "score" not in (cmd.get_property_list(n) or ()) for n in ("lig_a", "lig_b")
    )
    assert cmd.get_property("score", "lig_c") == 2


def test_export(tmp_path):
    from pymol import tables
    from pymol.Qt import QtCore

    _scene()
    table = _table()
    table.tree.sortByColumn(4, QtCore.Qt.SortOrder.AscendingOrder)
    table.filter.setText("lig_")
    table.tree.header().hideSection(5)  # note
    path = str(tmp_path / "shown.csv")
    table.export(path)
    # the rows shown in the order shown, the columns shown; no group row
    assert tables.read_table(path) == [
        ["name", "stars", "score"],
        ["lig_b", "", "-10.25"],
        ["lig_c", "", "-8"],
        ["lig_a", "", "-6.5"],
    ]


def _labels(table):
    """The property columns shown, in the order shown."""
    tree, header = table.tree, table.tree.header()
    columns = sorted(range(3, tree.columnCount()), key=header.visualIndex)
    return [tree.headerItem().text(c) for c in columns if not tree.isColumnHidden(c)]


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_columns_in_the_session(tmp_path, ext):
    """22d: the order of the columns, the hidden and the empty ones come
    back with a session, in a table that is open and in a new one."""
    from pymol import session_extra

    _scene()
    table = _table()
    table.add_column("comment")  # empty: no object has it
    assert _labels(table) == ["stars", "score", "note", "comment"]
    table.tree.header().moveSection(6, 4)  # comment before score
    table.set_hidden("note", True)
    assert _labels(table) == ["stars", "comment", "score"]
    assert session_extra.entries["table"] == {
        "columns": ["stars", "comment", "score", "note"],
        "hidden": ["note"],
        "empty": ["comment"],
    }
    path = str(tmp_path / ("layout." + ext))
    cmd.save(path)

    # a new session: nothing of the old columns is left
    cmd.reinitialize()
    table.refresh()
    assert (
        _labels(table) == ["stars"] and table.hidden == set() and table.extra == set()
    )
    cmd.fragment("ala", "other")
    cmd.set_property("note", "x", "other")
    table.refresh()
    assert _labels(table) == ["stars", "note"]

    cmd.load(path)
    table.refresh()  # the open table follows the session
    assert _labels(table) == ["stars", "comment", "score"]
    assert table.hidden == {"note"} and table.extra == {"comment"}
    fresh = _table()  # and so does a table opened later
    assert _labels(fresh) == ["stars", "comment", "score"]
    table.set_hidden("note", False)
    assert _labels(table) == ["stars", "comment", "score", "note"]

    # what is not a list of names is ignored
    session_extra.entries["table"] = {
        "columns": "score",
        "hidden": [3, "note"],
        "empty": None,
    }
    table.refresh()
    assert _labels(table) == ["stars", "score"]


def test_columns_menu_and_counted():
    """22d: the Columns button hides and shows columns and adds columns
    the core counts, as ordinary properties."""
    from pymol import util
    from pmg_qt import property_table

    _scene()
    cmd.alter("lig_a and name N", "formal_charge = 1")
    cmd.create("lig_b", "lig_b", 1, 2)  # a second state
    table = _table()
    table._fill_columns_menu()
    menu = table.columns_button.menu()
    rows = {a.text(): a for a in menu.actions() if a.text()}
    assert list(rows) == ["Add counted", "Refresh counted", "stars", "score", "note"]
    counted = [a.text() for a in rows["Add counted"].menu().actions() if a.text()]
    assert counted == [*property_table.COMPUTED, "all of them"]
    assert rows["score"].isChecked()
    rows["score"].trigger()  # unchecked: hidden
    assert table.hidden == {"score"} and _labels(table) == ["stars", "note"]
    table._fill_columns_menu()
    score = [a for a in menu.actions() if a.text() == "score"][0]
    assert not score.isChecked()
    score.trigger()
    assert _labels(table) == ["stars", "score", "note"]

    table.add_computed()
    assert _labels(table) == ["stars", "score", "note", *property_table.COMPUTED]
    for name in ("lig_a", "lig_b", "protein"):
        assert cmd.get_property("atoms", name) == cmd.count_atoms("%" + name)
        assert cmd.get_property("residues", name) == 1
        assert cmd.get_property("chains", name) == len(cmd.get_chains("%" + name))
        assert cmd.get_property("weight", name) == pytest.approx(
            util.compute_mass("%" + name), abs=0.01
        )
    assert [cmd.get_property("states", n) for n in ("lig_a", "lig_b")] == [1, 2]
    assert [cmd.get_property("charge", n) for n in ("lig_a", "lig_b")] == [1, 0]
    assert "atoms" not in (cmd.get_property_list("poses") or ())  # groups have none

    # counted when asked: a change shows after "Refresh counted"
    cmd.remove("lig_a and hydro")
    table.refresh()
    assert cmd.get_property("atoms", "lig_a") != cmd.count_atoms("%lig_a")
    table._fill_columns_menu()
    [a for a in menu.actions() if a.text() == "Refresh counted"][0].trigger()
    assert cmd.get_property("atoms", "lig_a") == cmd.count_atoms("%lig_a")


def test_follow():
    """22d: with Follow checked only the object of the current row is
    shown, with the groups it is in."""
    _scene()
    table = _table()
    tree = table.tree

    def enabled():
        return set(cmd.get_names("objects", enabled_only=1))

    everything = enabled()
    tree.setCurrentItem(table.items["lig_a"], 2)
    assert enabled() == everything  # not checked: rows are just rows
    table.follow.setChecked(True)  # the current row at once
    assert enabled() == {"poses", "lig_a"}
    tree.setCurrentItem(table.items["lig_b"], 2)
    assert enabled() == {"poses", "lig_b"}
    tree.setCurrentItem(table.items["protein"], 2)
    assert enabled() == {"protein"}
    tree.setCurrentItem(table.items["poses"], 2)  # a group is no step
    assert enabled() == {"protein"}
    table.follow.setChecked(False)
    tree.setCurrentItem(table.items["lig_c"], 2)
    assert enabled() == {"protein"}


def test_pick_selects_the_row():
    """22e: the row of the object an atom was picked in becomes current,
    once per pick; a pick is no step of Follow."""
    _scene()
    cmd.delete("sele")
    table = _table()
    tree = table.tree
    table.follow.setChecked(True)
    tree.setCurrentItem(table.items["protein"], 2)
    shown = set(cmd.get_names("objects", enabled_only=1))

    cmd.edit("lig_b and name CA")  # pk1
    table._follow_pick()
    assert tree.currentItem() is table.items["lig_b"]
    assert set(cmd.get_names("objects", enabled_only=1)) == shown
    tree.setCurrentItem(table.items["protein"], 2)
    table._follow_pick()  # the same pick again: the user's row stays
    assert tree.currentItem() is table.items["protein"]

    cmd.unpick()
    cmd.select("sele", "lig_c and name CA")  # a click in viewing mode
    table._follow_pick()
    assert tree.currentItem() is table.items["lig_c"]
    cmd.select("sele", "name CA")  # several objects: no row
    table._follow_pick()
    assert tree.currentItem() is table.items["lig_c"]


def _click_star(table, name, star, kind=None):
    """A left click on star 1 to 3 of a row, as the view sends it to the
    delegate; `kind` for a double click's event."""
    from pymol.Qt import QtCore, QtGui, QtWidgets
    from pmg_qt import property_table as module

    tree = table.tree
    index = tree.indexFromItem(table.items[name], table.column_of("stars"))
    option = QtWidgets.QStyleOptionViewItem()
    option.rect = QtCore.QRect(100, 40, 120, 22)
    side = min(module.STAR, option.rect.height() - 4)
    x = (
        option.rect.left()
        + module.STAR_LEFT
        + (star - 1) * (side + module.STAR_GAP)
        + side / 2
    )
    event = QtGui.QMouseEvent(
        kind or QtCore.QEvent.Type.MouseButtonRelease,
        QtCore.QPointF(x, 50),
        QtCore.QPointF(x, 50),
        QtCore.Qt.MouseButton.LeftButton,
        QtCore.Qt.MouseButton.NoButton,
        QtCore.Qt.KeyboardModifier.NoModifier,
    )
    return tree.itemDelegate().editorEvent(event, tree.model(), option, index)


def test_stars_clicks():
    """22f: three stars per molecule; a click on an empty star rates up to
    it, on a filled one down to the one before it."""
    from pymol.Qt import QtCore
    from pmg_qt import property_table as module

    _scene()
    table = _table()
    tree = table.tree
    assert (
        tree.headerItem().text(3) == "stars"
    )  # after the name, without a value anywhere
    assert all(
        "stars" not in (cmd.get_property_list(n) or ()) for n in ("lig_a", "protein")
    )

    def rating(name="lig_a"):
        return cmd.get_property("stars", name)

    for star, expected in (
        (1, 1),
        (3, 3),
        (3, 2),
        (2, 1),
        (2, 2),
        (1, 0),
        (2, 2),
        (3, 3),
        (1, 0),
    ):
        assert _click_star(table, "lig_a", star) is True
        assert rating() == expected and isinstance(rating(), int)
        assert table.items["lig_a"].text(3) == str(expected)
    assert "stars" not in (cmd.get_property_list("lig_b") or ())  # only the clicked row
    # a double click is two clicks and opens no editor
    _click_star(table, "lig_a", 2)
    assert (
        _click_star(table, "lig_a", 2, QtCore.QEvent.Type.MouseButtonDblClick) is True
    )
    assert rating() == 2
    # a group has no stars: the click is not taken
    assert not _click_star(table, "poses", 2)
    # beside the stars nothing happens
    rect = QtCore.QRect(100, 40, 120, 22)
    assert [module.star_at(rect, x) for x in (101, 107, 125, 145, 163, 200)] == [
        0,
        1,
        2,
        3,
        0,
        0,
    ]

    # the delegate knows the rating; what is no rating is left as text
    index = tree.indexFromItem(table.items["lig_a"], 3)
    assert tree.itemDelegate().rating(index) == 2
    assert tree.itemDelegate().rating(tree.indexFromItem(table.items["lig_b"], 3)) == 0
    assert (
        tree.itemDelegate().rating(tree.indexFromItem(table.items["poses"], 3)) is None
    )
    assert (
        tree.itemDelegate().rating(tree.indexFromItem(table.items["lig_a"], 4)) is None
    )
    role = QtCore.Qt.ItemDataRole.AccessibleTextRole
    assert table.items["lig_a"].data(3, role) == "Stars: 2 of 3"
    cmd.set_property("stars", 7, "lig_c")  # set from outside: shown, kept
    table.refresh()
    assert (
        tree.itemDelegate().rating(tree.indexFromItem(table.items["lig_c"], 3)) is None
    )
    assert (
        table.items["lig_c"].text(3) == "7" and cmd.get_property("stars", "lig_c") == 7
    )


def test_stars_values(tmp_path, capsys):
    """22f: typed, pasted and imported ratings are whole numbers from 0 to
    3; they sort and export as numbers and come back with a session."""
    from pymol import tables
    from pymol.Qt import QtCore, QtWidgets

    _scene()
    cmd.ungroup("poses")
    cmd.delete("poses")
    table = _table()
    tree = table.tree
    a, b, c = (table.items[n] for n in ("lig_a", "lig_b", "lig_c"))
    _edit(a, 3, "2")  # typed, then Enter
    assert cmd.get_property("stars", "lig_a") == 2
    for bad in ("4", "-1", "1.5", "two"):
        _edit(a, 3, bad)
        assert cmd.get_property("stars", "lig_a") == 2 and a.text(3) == "2"
    assert "rating from 0 to 3" in capsys.readouterr().out
    _edit(a, 3, "0")
    assert cmd.get_property("stars", "lig_a") == 0
    _edit(a, 3, "")  # Delete: no rating
    assert "stars" not in (cmd.get_property_list("lig_a") or ())

    # a pasted block: the good ratings are set, the others left out
    flag = tree.selectionModel().SelectionFlag
    QtWidgets.QApplication.clipboard().setText("3\n9\n1\n")
    tree.clearSelection()
    tree.setCurrentItem(a, 3, flag.Select)
    table.paste()
    assert (
        cmd.get_property("stars", "lig_a") == 3
        and cmd.get_property("stars", "lig_c") == 1
    )
    assert "stars" not in (cmd.get_property_list("lig_b") or ())

    # sorted as numbers, the unrated last; the rows keep their objects
    tree.sortByColumn(3, QtCore.Qt.SortOrder.AscendingOrder)
    assert _shown(table) == ["lig_c", "lig_a", "lig_b", "protein"]
    assert _click_star(table, "lig_b", 2)
    assert _shown(table) == ["lig_c", "lig_b", "lig_a", "protein"]
    assert cmd.get_property("stars", "lig_b") == 2

    # exported as 0 to 3, imported with the same rule
    path = str(tmp_path / "rated.csv")
    table.export(path)
    assert [row[:2] for row in tables.read_table(path)] == [
        ["name", "stars"],
        ["lig_c", "1"],
        ["lig_b", "2"],
        ["lig_a", "3"],
        ["protein", ""],
    ]
    bad = tmp_path / "bad.csv"
    bad.write_text("name,stars,score\nlig_a,5,1\nlig_b,3,2\nlig_c,2.5,3\nprotein,1,4\n")
    cmd.load_table(str(bad))
    assert "2 values of 'stars'" in capsys.readouterr().out
    stars = [
        cmd.get_property("stars", n) for n in ("lig_a", "lig_b", "lig_c", "protein")
    ]
    assert stars == [3, 3, 1, 1]  # 5 and 2.5 changed nothing
    assert cmd.get_property("score", "lig_a") == 1  # the rest of the row came in

    for ext in ("pse", "psex"):
        session = str(tmp_path / ("rated." + ext))
        cmd.save(session)
        cmd.reinitialize()
        cmd.load(session)
        table.refresh()
        assert [cmd.get_property("stars", n) for n in ("lig_a", "lig_b")] == [3, 3]
        assert table.items["lig_a"].text(table.column_of("stars")) == "3"


def test_stars_are_drawn():
    """22f: filled and empty stars differ in the picture of the row, on
    an ordinary and on a selected row."""
    from pymol.Qt import QtCore, QtWidgets

    cmd.fragment("ala", "one")
    table = _table()
    table.resize(600, 200)
    table.show()
    tree = table.tree
    QtWidgets.QApplication.processEvents()

    def picture():
        QtWidgets.QApplication.processEvents()
        rect = tree.visualItemRect(table.items["one"])
        left = tree.columnViewportPosition(3)
        cell = QtCore.QRect(left, rect.top(), tree.columnWidth(3), rect.height())
        return tree.viewport().grab(cell).toImage()

    for selected in (False, True):
        tree.clearSelection()
        if selected:
            table.items["one"].setSelected(True)
        pictures = []
        for rating in (0, 1, 2, 3):
            cmd.set_property("stars", rating, "one")
            table.refresh()
            pictures.append(picture())
        assert all(a != b for i, a in enumerate(pictures) for b in pictures[i + 1 :])

    # a click that goes through the view, as the mouse does
    from PySide6.QtTest import QTest
    from pmg_qt import property_table as module

    def star(number):
        rect = tree.visualRect(tree.indexFromItem(table.items["one"], 3))
        side = min(module.STAR, rect.height() - 4)
        x = (
            rect.left()
            + module.STAR_LEFT
            + (number - 1) * (side + module.STAR_GAP)
            + side // 2
        )
        return QtCore.QPoint(x, rect.center().y())

    left, none = QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.KeyboardModifier.NoModifier
    port = tree.viewport()
    for number, expected in ((2, 1), (2, 2), (3, 3)):  # it has three now
        QTest.mouseClick(port, left, none, star(number))
        QtWidgets.QApplication.processEvents()
        assert cmd.get_property("stars", "one") == expected
    QTest.mouseDClick(port, left, none, star(1))  # no editor on a double click
    QtWidgets.QApplication.processEvents()
    assert not port.findChild(QtWidgets.QLineEdit)
    # beside the stars a double click edits the number, as in any cell
    rect = tree.visualRect(tree.indexFromItem(table.items["one"], 3))
    QTest.mouseDClick(
        port, left, none, QtCore.QPoint(rect.right() - 3, rect.center().y())
    )
    QtWidgets.QApplication.processEvents()
    assert port.findChild(QtWidgets.QLineEdit)
    table.close()
