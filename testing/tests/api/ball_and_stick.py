"""
34a: the representation "ball_and_stick". Its own visibility bit, sizes and
colors; bonds show their order; settings of sticks, spheres and lines do not
change it and it changes none of theirs. Checked through the primitives the
ray tracer gets (cmd.get_povray), which are what the viewport draws.
"""

import re

import pytest

from pymol import cmd, testing

SPHERE = re.compile(
    r"sphere\{<([^>]*)>,\s*([\d.eE+-]+)[^}]*?pigment\{color rgb(?:f|t|ft)?<([^>]*)>"
)
CYLINDER = re.compile(r"cylinder\{<([^>]*)>,\s*<([^>]*)>,\s*([\d.eE+-]+)")


def _scene():
    return cmd.get_povray()[1]


def _balls(minimum=0.2):
    """(radius, (r, g, b)) of the spheres at least `minimum` across: the
    balls, without the round ends of thin bonds."""
    found = []
    for _, radius, color in SPHERE.findall(_scene()):
        if float(radius) >= minimum:
            found.append(
                (
                    round(float(radius), 3),
                    tuple(round(float(c), 2) for c in color.split(",")),
                )
            )
    return found


def _bonds():
    """Radii of the cylinders."""
    return [round(float(radius), 3) for _, _, radius in CYLINDER.findall(_scene())]


def _radii(selection="all"):
    radii = []
    cmd.iterate(selection, "radii.append(vdw)", space={"radii": radii})
    return radii


def test_visibility_is_its_own():
    cmd.fragment("ala", "m")
    cmd.hide("everything")
    assert _scene().count("sphere{") == 0 and not _bonds()
    cmd.show("ball_and_stick", "not hydro")
    assert cmd.count_atoms("rep ball_and_stick") == 5
    assert cmd.count_atoms("rep sticks or rep spheres or rep lines") == 0
    assert len(_balls()) == 5 and _bonds()
    # with sticks, spheres and lines: each keeps its atoms
    cmd.show("sticks", "name CA+CB")
    cmd.show("spheres", "name N")
    cmd.show("lines")
    cmd.hide("ball_and_stick", "name O")
    assert cmd.count_atoms("rep ball_and_stick") == 4
    assert cmd.count_atoms("rep sticks") == 2 and cmd.count_atoms("rep spheres") == 1
    assert cmd.count_atoms("rep lines") == 10
    cmd.hide("sticks")
    cmd.hide("spheres")
    cmd.hide("lines")
    assert cmd.count_atoms("rep ball_and_stick") == 4
    cmd.toggle("ball_and_stick", "m")
    assert cmd.count_atoms("rep ball_and_stick") == 0
    cmd.toggle("ball_and_stick", "m")
    assert cmd.count_atoms("rep ball_and_stick") == 10
    cmd.show_as("sticks")
    assert (
        cmd.count_atoms("rep ball_and_stick") == 0
        and cmd.count_atoms("rep sticks") == 10
    )
    cmd.show_as("ball_and_stick")
    assert (
        cmd.count_atoms("rep ball_and_stick") == 10
        and cmd.count_atoms("rep sticks") == 0
    )
    cmd.hide("everything")
    assert cmd.count_atoms("rep ball_and_stick") == 0 and _scene().count("sphere{") == 0


def test_sizes_are_its_own():
    cmd.fragment("ala", "m")
    cmd.show_as("ball_and_stick")
    assert cmd.get_setting_float("ball_and_stick_scale") == pytest.approx(0.31)
    assert cmd.get_setting_float("ball_and_stick_bond_radius") == pytest.approx(0.12)
    # a ball is 0.31 of the atom's radius, as a sphere at sphere_scale 0.31
    expected = sorted(round(0.31 * r, 3) for r in _radii())
    assert sorted(r for r, _ in _balls()) == expected
    assert max(_bonds()) == pytest.approx(0.12)
    before = _scene()

    # what styles sticks, spheres and lines does not reach it
    for name, value in (
        ("stick_radius", 0.6),
        ("stick_ball", 1),
        ("stick_ball_ratio", 3.0),
        ("stick_color", "red"),
        ("stick_ball_color", "blue"),
        ("stick_transparency", 0.5),
        ("stick_h_scale", 0.3),
        ("stick_valence_scale", 2.0),
        ("valence", 0),
        ("sphere_scale", 2.0),
        ("sphere_color", "yellow"),
        ("sphere_transparency", 0.5),
        ("line_width", 9),
        ("line_color", "white"),
    ):
        cmd.set(name, value)
        cmd.set(name, value, "m")
        assert _scene() == before, name
    cmd.set_bond("stick_radius", 0.7, "all")
    cmd.set_bond("stick_color", "red", "all")
    cmd.set_bond("valence", 0, "all")
    assert _scene() == before

    # and its settings reach nothing else
    cmd.show("sticks")
    cmd.show("spheres")
    cmd.hide("ball_and_stick")
    others = _scene()
    cmd.set("ball_and_stick_scale", 0.8)
    cmd.set("ball_and_stick_bond_radius", 0.3)
    cmd.set("ball_and_stick_color", "green")
    cmd.set("ball_and_stick_color", "red", "name CA")
    assert _scene() == others
    for name in ("stick_radius", "sphere_scale"):
        assert cmd.get_setting_float(name) in (0.6, 2.0)

    # per atom: the ball of the atom, and a bond as thin as its thinner end
    cmd.show_as("ball_and_stick")
    cmd.unset("ball_and_stick_scale")
    cmd.unset("ball_and_stick_bond_radius")
    cmd.unset("ball_and_stick_color")
    cmd.unset("ball_and_stick_color", "name CA")
    assert _scene() == before
    cmd.set("ball_and_stick_scale", 0.5, "name CB")
    radius = _radii("name CB")[0]
    assert round(0.5 * radius, 3) in [r for r, _ in _balls()]
    cmd.set("ball_and_stick_bond_radius", 0.05, "name CB")
    assert 0.05 in _bonds() and 0.12 in _bonds()
    cmd.unset("ball_and_stick_scale", "name CB")
    cmd.unset("ball_and_stick_bond_radius", "name CB")
    assert _scene() == before


def test_colors_are_its_own():
    cmd.fragment("ala", "m")
    cmd.color("grey50")
    cmd.show_as("ball_and_stick", "not hydro")
    grey = tuple(round(c, 2) for c in cmd.get_color_tuple("grey50"))
    assert {c for _, c in _balls()} == {grey}
    colors = []
    cmd.iterate("all", "colors.append(color)", space={"colors": colors})

    def atom_colors():
        now = []
        cmd.iterate("all", "now.append(color)", space={"now": now})
        return now

    cmd.set("ball_and_stick_color", "red")  # all of it
    assert {c for _, c in _balls()} == {(1.0, 0.0, 0.0)}
    cmd.set("ball_and_stick_color", "blue", "name CA")  # one atom
    assert sorted({c for _, c in _balls()}) == [(0.0, 0.0, 1.0), (1.0, 0.0, 0.0)]
    assert atom_colors() == colors  # the atoms keep theirs
    cmd.hide("ball_and_stick")
    cmd.show("sticks")
    stick = {
        tuple(round(float(c), 2) for c in rgb.split(","))
        for _, _, rgb in SPHERE.findall(_scene())
    }
    assert stick == {grey}  # and so do sticks
    cmd.show_as("ball_and_stick", "not hydro")

    # "atomic": by element, whatever color the atoms have
    cmd.unset("ball_and_stick_color", "name CA")
    cmd.set("ball_and_stick_color", "atomic")
    by_element = {c for _, c in _balls()}
    assert len(by_element) == 3 and grey not in by_element  # C, N, O
    assert atom_colors() == colors

    # unset: the color of the atom again, and a new atom color shows
    cmd.unset("ball_and_stick_color")
    assert {c for _, c in _balls()} == {grey}
    cmd.color("yellow", "name N")
    assert (1.0, 1.0, 0.0) in {c for _, c in _balls()}


def test_bond_orders():
    """Single, double and triple bonds as that many cylinders; an aromatic
    bond as the core draws it, a solid and a broken one. `valence`, the
    switch of sticks and lines, is not asked, and the molecule is not
    changed by being drawn."""

    def cylinders(order):
        cmd.reinitialize()
        cmd.pseudoatom("m", pos=[0, 0, 0], elem="C", name="C1", resi="1")
        cmd.pseudoatom("m", pos=[1.4, 0, 0], elem="C", name="C2", resi="1")
        cmd.pseudoatom("m", pos=[2.1, 1.2, 0], elem="C", name="C3", resi="1")
        cmd.pseudoatom("m", pos=[-0.7, 1.2, 0], elem="C", name="C4", resi="1")
        cmd.bond("name C1", "name C2", order)
        cmd.bond("name C2", "name C3", 1)
        cmd.bond("name C1", "name C4", 1)
        cmd.hide("everything")
        cmd.set("valence", 0)
        cmd.show("ball_and_stick")
        count = len(_bonds())
        assert len(_balls()) == 4
        assert [b.order for b in cmd.get_model("m").bond] == [order, 1, 1]
        return count

    single = cylinders(1) // 3  # three single bonds
    assert single >= 1 and cylinders(1) == 3 * single
    assert cylinders(2) == (2 + 2) * single
    assert cylinders(3) == (3 + 2) * single
    assert cylinders(4) > (2 + 2) * single  # one solid, one in pieces


def test_atoms_without_bonds_and_states():
    cmd.pseudoatom("ion", pos=[5, 5, 5], elem="Zn", name="ZN")
    cmd.fragment("gly", "m")
    cmd.create("m", "m", 1, 2)
    cmd.translate([10, 0, 0], "m", state=2)
    cmd.hide("everything")
    cmd.show("ball_and_stick")
    cmd.frame(1)
    first = _balls()
    radius = round(0.31 * _radii("ion")[0], 3)
    assert radius in [r for r, _ in first]  # the ion is a ball
    assert len(first) == cmd.count_atoms("m") + 1
    x1 = sorted(float(c.split(",")[0]) for c, _, _ in SPHERE.findall(_scene()))
    cmd.frame(2)
    x2 = sorted(float(c.split(",")[0]) for c, _, _ in SPHERE.findall(_scene()))
    assert x1 != x2  # the second state where it is
    # coordinates that move take the balls and bonds along
    before = _scene()
    cmd.translate([0, 3, 0], "m", state=2)
    assert _scene() != before


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_session(tmp_path, ext):
    cmd.fragment("ala", "m")
    cmd.show_as("ball_and_stick", "not hydro")
    cmd.show("spheres", "name N")
    cmd.set("ball_and_stick_scale", 0.4, "name CA")
    cmd.set("ball_and_stick_color", "atomic", "m")
    cmd.set("ball_and_stick_bond_radius", 0.08)
    cmd.set("sphere_scale", 0.5, "name CB")  # a setting PyMOL has too
    before = _scene()
    # The settings of atoms that PyMOL does not know have a key of their
    # own: PyMOL 3.2 ends when it saves a session that has one in its list.
    session = cmd.get_session()
    first = cmd.setting._get_index("ball_and_stick_scale")
    known = [entry[0] for _, entries in session["unique_settings"] for entry in entries]
    ours = [
        entry[0]
        for _, entries in session["pymolish_unique_settings"]
        for entry in entries
    ]
    assert known and max(known) < first and ours and min(ours) >= first
    path = str(tmp_path / ("b." + ext))
    cmd.save(path)
    cmd.reinitialize()
    cmd.load(path)
    assert (
        cmd.count_atoms("rep ball_and_stick") == 5
        and cmd.count_atoms("rep spheres") == 1
    )
    assert _scene() == before
    # a session from before has none of it and loads as it was
    cmd.reinitialize()
    cmd.load(testing.datafile("1oky-frag.pdb"))
    assert cmd.count_atoms("rep ball_and_stick") == 0
    assert "pymolish_unique_settings" not in cmd.get_session()  # only when there is one


def test_scene_keeps_it():
    cmd.fragment("ala", "m")
    cmd.show_as("ball_and_stick")
    cmd.set("ball_and_stick_scale", 0.4, "name CA")
    cmd.set("ball_and_stick_color", "red", "m")
    cmd.scene("a", "store")
    a = _scene()
    cmd.show_as("sticks")
    cmd.set("ball_and_stick_scale", 0.2, "name CA")
    cmd.set("ball_and_stick_scale", 0.2, "name CB")
    cmd.set("ball_and_stick_color", "blue", "m")
    cmd.set("ball_and_stick_bond_radius", 0.3, "m")
    cmd.scene("b", "store")
    cmd.scene("a", "recall", animate=0)
    assert _scene() == a and cmd.count_atoms("rep ball_and_stick") == 10
    cmd.scene("b", "recall", animate=0)
    assert cmd.count_atoms("rep ball_and_stick") == 0
    cmd.show("ball_and_stick")
    assert 0.3 in _bonds()
