"""
ligand_2d: which small molecules count as ligands, the contacts found in
1OKY (staurosporine in PDK1), the ring layout without overlaps, the picture
as SVG and PNG. Needs rdkit, except the layout.
"""

import math
from xml.etree import ElementTree

import pytest

from pymol import CmdException, cmd, ligand2d, testing

try:
    import rdkit  # noqa: F401
except ImportError:
    rdkit = None

needs_rdkit = pytest.mark.skipif(not rdkit, reason="rdkit not installed")


def _apart(places, size=ligand2d.SIZE):
    """No two residue circles overlap: their centers are a circle apart."""
    return all(
        math.dist(a, b) >= size for i, a in enumerate(places) for b in places[i + 1 :]
    )


def test_legend_fits():
    # 30a: the legend wraps into rows; no entry starts beyond the picture
    for width, most in ((344, 5), (429, 4), (1200, 2)):
        entries, rows = ligand2d._legend(width)
        assert [name for name, _, _ in entries] == [*ligand2d.COLORS, *ligand2d.LINES]
        assert rows <= most and rows == entries[-1][2] + 1
        assert all(14 <= x < width - 60 for _, x, _ in entries), width
        first_line = len(ligand2d.COLORS)  # the contacts start a row
        assert entries[first_line][1] == 14
        assert entries[first_line][2] > entries[first_line - 1][2]


def test_layout():
    atoms = [(100 + 30 * i, 200) for i in range(8)]  # a chain of atoms
    # nothing to place, and one residue
    assert ligand2d.layout(atoms, []) == ([], 0.0)
    (place,), radius = ligand2d.layout(atoms, [[0]])
    assert place[0] < 100 and abs(place[1] - 200) < 1  # left of the left end
    # residues that all touch the same atom still stand apart
    places, _ = ligand2d.layout(atoms, [[7]] * 6)
    assert _apart(places)
    assert all(p[0] > 205 for p in places)  # and on its side of the ligand
    # more residues than fit: the ring grows
    small = ligand2d.layout(atoms, [[i % 8] for i in range(8)])[1]
    places, large = ligand2d.layout(atoms, [[i % 8] for i in range(40)])
    assert large > small and _apart(places)
    # each one is at the angle of its atom when there is room
    places, _ = ligand2d.layout(atoms, [[0], [7]])
    assert places[0][0] < 100 < 310 < places[1][0]


@needs_rdkit
def test_ligands_and_contacts():
    with pytest.raises(CmdException, match="no ligand"):
        cmd.ligand_2d()
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    found = ligand2d.ligands()
    assert found[0] == ("STU A1368", "/m//A/STU`1368/")  # the one in the pocket first
    assert {label.split()[0] for label, _ in found[1:]} == {"GOL"}
    cmd.disable("m")
    assert ligand2d.ligands() == []  # only in what is switched on
    cmd.enable("m")

    residues = cmd.ligand_2d()  # the first ligand
    by_name = {"%s%s" % r["label"]: r for r in residues}
    contacts = {name: {c[0] for c in r["contacts"]} for name, r in by_name.items()}
    # the two hydrogen bonds to the hinge of the kinase, and the charged amine
    assert "hydrogen bond" in contacts["SER160"]
    assert "hydrogen bond" in contacts["ALA162"]
    assert "salt bridge" in contacts["GLU166"]
    assert "cation-ring" in contacts["LYS111"]
    assert by_name["GLU166"]["kind"] == "negative"
    assert by_name["LEU88"]["kind"] == "hydrophobic" and not contacts["LEU88"]
    assert cmd.count_atoms(by_name["SER160"]["sele"]) == cmd.count_atoms("m and resi 160")
    # a wider cutoff draws more residues
    assert len(cmd.ligand_2d("resn STU", cutoff=6)) > len(residues)


@needs_rdkit
def test_picture(tmp_path):
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    mol, residues = ligand2d.analyze("resn STU")
    svg, size, places = ligand2d.draw(mol, residues)
    assert len(places) == len(residues) and _apart(places)
    assert all(0 < x < size[0] and 0 < y < size[1] for x, y in places)  # inside
    root = ElementTree.fromstring(svg)
    assert root.tag.endswith("svg")
    # a filled circle and its outline per residue and per kind of the legend
    kinds = len(ligand2d.COLORS)
    ellipses = [e for e in root.iter() if e.tag.endswith("ellipse")]
    assert len(ellipses) == 2 * (len(residues) + kinds)
    assert all(e.get("rx") == e.get("ry") for e in ellipses)
    assert float(ellipses[0].get("rx")) == ligand2d.SIZE / 2
    # 30a: each fill is the gradient of its kind
    assert svg.count("<linearGradient") == kinds
    assert svg.count("fill:url(#") == len(residues) + kinds
    assert "fill:url(#%s)" % residues[0]["kind"] in ellipses[0].get("style")
    # rdkit writes a space as a path without data; Qt warns about those
    assert "d=''" not in svg
    # on a dark window: other tones, deep fills under white text
    dark = ligand2d.draw(mol, residues, background=(0.2, 0.2, 0.2), ink=(0.9, 0.9, 0.9))[0]
    stops = lambda text: text[text.index("<defs>") : text.index("</defs>")]
    assert stops(dark) != stops(svg)
    for color in ligand2d.COLORS.values():
        top, bottom, edge, ink = ligand2d._tones(color, True)
        assert sum(top) > sum(bottom) and sum(ink) - sum(top) > 1.2
        top, bottom, edge, ink = ligand2d._tones(color, False)
        assert sum(top) > sum(bottom) > sum(edge) and sum(bottom) - sum(ink) > 1.2
    png, _, _ = ligand2d.draw(mol, residues, svg=False)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert ligand2d.draw(mol, residues, selected={0})[0] != svg  # the blue ring
    # the command writes both kinds of file
    for name in ("a.svg", "a.png"):
        path = tmp_path / name
        cmd.ligand_2d("resn STU", filename=str(path))
        assert path.stat().st_size > 2000
