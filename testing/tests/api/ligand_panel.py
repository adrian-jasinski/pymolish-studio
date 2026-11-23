"""
Ligand panel: the list of ligands, a click on a residue of the picture
selects it in 3D, a selection in 3D is ringed in the picture, the message
without a ligand, saving. Headless (offscreen QApplication). Needs rdkit.
"""

import os

import pytest

from pymol import cmd, testing

pytest.importorskip("rdkit")


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _panel():
    from pmg_qt.ligand_panel import LigandPanel

    panel = LigandPanel(cmd)
    panel.resize(700, 700)
    panel.show()
    panel.refresh()
    return panel


def _point(panel, name):
    """The middle of a residue's shape, in the coordinates of the label."""
    from pymol.Qt import QtCore

    index = ["%s%s" % r["label"] for r in panel.residues].index(name)
    x, y = panel.places[index]
    scale = panel._scale
    left = (panel.picture.width() - panel._size[0] * scale) / 2
    top = (panel.picture.height() - panel._size[1] * scale) / 2
    return QtCore.QPointF(x * scale + left, y * scale + top)


def test_no_ligand():
    cmd.fragment("ala")
    panel = _panel()
    assert panel.choice.count() == 0
    assert panel.picture.text() == "No ligand in the visible objects."
    panel._clicked(_no_point(), False)  # a click on the message does nothing
    assert "sele" not in cmd.get_names("selections")


def _no_point():
    from pymol.Qt import QtCore

    return QtCore.QPointF(10, 10)


def test_clicks_and_selection(tmp_path):
    from pymol.Qt import QtWidgets

    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    panel = _panel()
    labels = [panel.choice.itemText(i) for i in range(panel.choice.count())]
    assert labels[0] == "STU A1368" and len(labels) == 4
    assert not panel.picture.pixmap().isNull() and len(panel.places) == len(
        panel.residues
    )

    # a click on a residue selects it in 3D and shows it as sticks
    panel._clicked(_point(panel, "SER160"), False)
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 160")
    assert cmd.count_atoms("m and resi 160 and rep sticks") > 0
    ser = ["%s%s" % r["label"] for r in panel.residues].index("SER160")
    assert panel.selected == {ser}  # and it is ringed in the picture
    # Ctrl adds; a plain click replaces; a click beside the shapes does nothing
    panel._clicked(_point(panel, "ALA162"), True)
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 160+162")
    assert len(panel.selected) == 2
    panel._clicked(_no_point(), False)
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 160+162")
    panel._clicked(_point(panel, "GLU166"), False)
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 166")

    # the other way: what is selected in 3D is ringed at the next poll
    before = panel.picture.pixmap().toImage()
    cmd.select("sele", "m and resi 88+111 and name CA")
    panel.poll()
    names = {"%s%s" % panel.residues[i]["label"] for i in panel.selected}
    assert names == {"LEU88", "LYS111"}
    assert panel.picture.pixmap().toImage() != before
    cmd.delete("sele")
    panel.poll()
    assert panel.selected == set()

    # the picture follows the size of the panel, and clicks still land
    panel.resize(420, 420)
    QtWidgets.QApplication.processEvents()
    assert panel._scale < 1
    panel._clicked(_point(panel, "SER160"), False)
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 160")

    # 24d: shrunk and grown again and again, the whole picture is inside
    # the label, uses the room there is, and clicks still land
    for width, height in ((300, 300), (1400, 1500), (260, 900), (900, 320), (700, 700)):
        panel.resize(width, height)
        QtWidgets.QApplication.processEvents()
        pixmap, label = panel.picture.pixmap(), panel.picture
        drawn = pixmap.deviceIndependentSize()
        assert (
            drawn.width() <= label.width() + 1 and drawn.height() <= label.height() + 1
        )
        assert label.width() - drawn.width() < 2 or label.height() - drawn.height() < 2
        panel._clicked(_point(panel, "ALA162"), False)
        assert cmd.count_atoms("sele") == cmd.count_atoms("m and resi 162")
    panel.resize(1400, 1500)
    QtWidgets.QApplication.processEvents()
    assert panel._scale > 1.25  # no ceiling: a large panel gets a large picture
    panel.hide()
    panel.resize(200, 200)  # hidden: nothing to divide by, nothing drawn wrong
    panel.show()
    panel.resize(700, 700)
    QtWidgets.QApplication.processEvents()

    # another ligand from the list
    panel.choice.setCurrentIndex(1)
    panel.refresh(keep=True)
    assert panel.choice.currentText().startswith("GOL") and panel.residues
    assert panel.choice.count() == 4  # the list was not rebuilt

    path = tmp_path / "picture.svg"
    panel.save(str(path))
    assert path.read_text().lstrip().startswith("<?xml")


def test_panel_follows_ligand_next():
    """36a: an open panel shows the ligand that ligand_next went to."""
    from pymol import ligand_nav

    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    panel = _panel()
    first = panel.choice.currentData()
    visited = cmd.ligand_next()
    assert visited == first  # both begin with the ligand in its pocket
    visited = cmd.ligand_next()
    assert visited != first
    panel.poll()
    assert panel.choice.currentData() == visited == ligand_nav.current()
    assert panel.residues is not None and not panel.picture.pixmap().isNull()
    # a choice made in the panel stays until the walk goes on
    panel.choice.setCurrentIndex(0)
    panel.refresh(keep=True)
    panel.poll()
    assert panel.choice.currentData() == first
    visited = cmd.ligand_next()
    panel.poll()
    assert panel.choice.currentData() == visited
    panel.close()


def test_24c_show_in_3d_tooltips_and_tab():
    from pymol.Qt import QtWidgets

    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    panel = _panel()
    ours = {
        "ligand_2d",
        "ligand_2d_hydrogen_bond",
        "ligand_2d_salt_bridge",
        "ligand_2d_cation_ring",
    }
    # Show in 3D: the contacts as dashes, in a group of their own
    assert not ours & set(cmd.get_names("all"))
    panel.in_3d.setChecked(True)
    assert ours <= set(cmd.get_names("all"))
    # another ligand: its own dashes (glycerol has no contacts drawn)
    panel.choice.setCurrentIndex(1)
    panel.refresh(keep=True)
    group = {"ligand_2d"} if panel._dashes else set()
    assert set(cmd.get_names("all")) - {"m"} == set(panel._dashes) | group
    panel.choice.setCurrentIndex(0)
    panel.refresh(keep=True)
    assert ours <= set(cmd.get_names("all"))
    # closed: they go; opened again with the box on: they come back
    panel.close()
    assert cmd.get_names("all") == ["m"]
    panel.show()
    panel.refresh()
    assert ours <= set(cmd.get_names("all"))
    panel.in_3d.setChecked(False)
    assert cmd.get_names("all") == ["m"]

    # the tooltip of a residue: kind, contacts with distances, nearest atoms
    text = panel._tip(_point(panel, "SER160"))
    assert text.startswith("SER 160, polar\nhydrogen bond ")
    assert text.endswith(" Å") and "nearest atoms" in text
    assert panel._tip(_no_point()) == ""

    # Tab walks the residues around the ring, Enter selects; past the last
    # one the focus goes on
    seen = []
    while panel._step(True):
        seen.append(panel.current)
        assert QtWidgets.QToolTip.text().startswith(
            "%s %s" % panel.residues[seen[-1]]["label"]
        )
    assert sorted(seen) == list(range(len(panel.residues))) and panel.current is None
    panel._step(True)
    panel._step(True)
    second = panel.residues[panel.current]
    panel._entered(False)
    assert cmd.count_atoms("sele") == cmd.count_atoms(second["sele"])
    assert panel._step(False) and panel._step(False) is False  # back past the first
    panel.close()
