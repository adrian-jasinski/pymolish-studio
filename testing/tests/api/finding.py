"""
search_sequence (modules/pymol/finding.py), cluster_ligands and
color_group_with_gradient (modules/pymol/grouping.py).
"""

import pytest
from pymol import CmdException, cmd, grouping, testing


def residues(selection):
    found = []
    cmd.iterate(
        "(%s) and name CA" % selection,
        "found.append((model, chain, int(resi)))",
        space={"found": found},
    )
    return found


def test_search_sequence():
    cmd.fab("ACDNGSACD", "p1", chain="A")
    cmd.fab("GSACD", "p2", chain="B")
    cmd.alter("p2", "resi=str(int(resi) + 100)")
    assert cmd.search_sequence("acd", "hit") == 3
    assert residues("hit") == ([("p1", "A", n) for n in (1, 2, 3, 7, 8, 9)]
        + [("p2", "B", n) for n in (103, 104, 105)])
    # whole residues are selected, not only the CA atoms
    assert cmd.count_atoms("hit and p2") == cmd.count_atoms("p2 and resi 103-105")
    # a regular expression, the default name, a selection to look in
    assert cmd.search_sequence("N[^P][ST]", selection="p1") == 1
    assert residues("seq_NPST") == [("p1", "A", n) for n in (4, 5, 6)]
    # no match across two chains, an empty selection when nothing is found
    assert cmd.search_sequence("CDGS", "none_found") == 0
    assert cmd.count_atoms("none_found") == 0
    pytest.raises(CmdException, cmd.search_sequence, "A[")
    assert "search_sequence" in cmd.keyword


def ligands():
    """Six one-atom objects: three near the origin, two near x=50, one
        alone at x=200."""
    for name, x in zip("abcdef", (0, 3, 6, 50, 52, 200)):
        cmd.pseudoatom("lig_" + name, pos=[x, 0, 0])
    cmd.group("ligs", "lig_*")


def test_cluster_ligands():
    ligands()
    groups = cmd.cluster_ligands("lig_*")
    assert groups == ["cluster_1", "cluster_2", "cluster_3"]
    assert grouping.members("cluster_1") == ["lig_a", "lig_b", "lig_c"]
    assert grouping.members("cluster_2") == ["lig_d", "lig_e"]
    assert grouping.members("cluster_3") == ["lig_f"]
    # a chain of small steps is one cluster: 0, 3, 6 with a cutoff of 4
    assert len(cmd.cluster_ligands("lig_*", cutoff=4)) == 3
    # a number of groups instead of a cutoff; emptied groups go away
    assert cmd.cluster_ligands("lig_*", 2) == ["cluster_1", "cluster_2"]
    assert len(grouping.members("cluster_1")) == 5
    assert "cluster_3" not in cmd.get_names()
    cmd.cluster_ligands("lig_*", prefix="site", cutoff=1000)
    assert len(grouping.members("site_1")) == 6
    pytest.raises(CmdException, cmd.cluster_ligands, "lig_a")
    assert "cluster_ligands" in cmd.keyword


def test_color_group_with_gradient():
    ligands()
    cmd.color_group_with_gradient("ligs", "red")
    colors = []
    cmd.iterate("ligs", "colors.append(color)", space={"colors": colors})
    rgb = [cmd.get_color_tuple(c) for c in colors]
    reds = [c[0] for c in rgb]
    assert reds == sorted(reds)  # dark to light
    assert reds[0] == pytest.approx(0.3, abs=5e-3)
    assert reds[-1] == pytest.approx(1.0, abs=5e-3)
    assert all(c[1] == 0 and c[2] == 0 for c in rgb)
    # a second gradient leaves the first one alone
    cmd.color_group_with_gradient("lig_a", "blue")
    assert cmd.get_color_tuple(color_of("lig_f"))[0] == pytest.approx(1.0, abs=5e-3)
    pytest.raises(CmdException, cmd.color_group_with_gradient, "none")
    assert "color_group_with_gradient" in cmd.keyword


def color_of(name):
    colors = []
    cmd.iterate(name, "colors.append(color)", space={"colors": colors})
    return colors[0]
