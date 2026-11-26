"""
11c: color_cpk colors by element in the CPK colors of RasMol, the whole
residues of a selection; with "ball_and_stick" only the overrides of that
representation, so that atoms, spheres and the cartoon keep their colors.
"""

import pytest

from pymol import cmd, menu, palettes, testing


def _rgb(hexcolor):
    return tuple(round(int(hexcolor[i : i + 2], 16) / 255, 3) for i in (0, 2, 4))


def _atom_colors(selection="all"):
    """{(resn, name): rgb} of the atoms' colors."""
    found = {}
    cmd.iterate(
        selection,
        "found[resn, name] = tuple(round(c, 3) for c in get_color_tuple(color))",
        space={
            "found": found,
            "get_color_tuple": cmd.get_color_tuple,
            "round": round,
            "tuple": tuple,
        },
    )
    return found


def test_the_table():
    assert palettes.CPK["C"] == "c8c8c8" and palettes.CPK["O"] == "f00000"
    assert palettes.CPK["N"] == "8f8fff" and palettes.CPK["S"] == "ffc832"
    assert palettes.CPK["Zn"] == palettes.CPK["Br"] == "a52a2a"
    assert palettes.CPK_OTHER == "ff1493"
    assert len(palettes.CPK) == 28 and all(len(c) == 6 for c in palettes.CPK.values())


def test_elements():
    cmd.fragment("cys", "m")  # C, N, O, S, H
    cmd.pseudoatom("m", elem="Zn", name="ZN", resn="ZN", resi="50", pos=[9, 0, 0])
    cmd.pseudoatom("m", elem="Br", name="BR", resn="BRO", resi="51", pos=[9, 3, 0])
    cmd.pseudoatom("m", elem="Xx", name="XX", resn="UNK", resi="52", pos=[9, 6, 0])
    cmd.color("green")
    assert cmd.color_cpk("m") == cmd.count_atoms("m")
    colors = _atom_colors()
    for name, element in (
        ("CA", "C"),
        ("N", "N"),
        ("O", "O"),
        ("SG", "S"),
        ("HA", "H"),
    ):
        assert colors["CYS", name] == _rgb(palettes.CPK[element]), name
    assert colors["ZN", "ZN"] == colors["BRO", "BR"] == _rgb("a52a2a")  # metal, halogen
    assert colors["UNK", "XX"] == _rgb("ff1493")  # no color of its own
    # no named color was defined or redefined, and no palette was touched
    assert cmd.get_color_tuple("green") == pytest.approx((0, 1, 0))
    assert cmd.get_color_tuple("carbon") == pytest.approx((0.2, 1.0, 0.2))


def test_whole_residues_and_modified_ones():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.color("green")
    before = _atom_colors("not resi 160+241")
    # one atom of a residue colors the residue, and only it
    cmd.color_cpk("resi 160 and name CA")
    colors = _atom_colors("resi 160")
    assert len(colors) == cmd.count_atoms("resi 160") > 1
    assert set(colors.values()) <= {_rgb(c) for c in palettes.CPK.values()}
    assert len(set(colors.values())) >= 3  # C, N, O
    # a modified residue (SEP, phosphoserine): its atoms by element too
    cmd.color_cpk("resn SEP and name P")
    sep = _atom_colors("resn SEP")
    assert sep["SEP", "P"] == _rgb(palettes.CPK["P"]) and sep["SEP", "CA"] == _rgb(
        "c8c8c8"
    )
    assert _atom_colors("not resi 160+241") == before


def test_ball_and_stick_only():
    """The balls and sticks get the CPK colors; atoms, spheres, sticks and
    the cartoon keep theirs."""
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.set_color("mine", [0.2, 0.4, 0.6])
    cmd.color("mine")
    cmd.set("sphere_color", "yellow", "resn STU")
    cmd.set("cartoon_color", "red", "m")
    cmd.show("spheres", "resn STU")
    cmd.show("ball_and_stick", "resn STU")
    atoms = _atom_colors()

    def overrides(setting):
        values = set()
        cmd.iterate(
            "resn STU",
            "values.add(getattr(s, key))",
            space={"values": values, "key": setting, "getattr": getattr},
        )
        return values

    spheres = overrides("sphere_color")
    cmd.color_cpk("resn STU and name N1", "ball_and_stick")
    assert _atom_colors() == atoms
    assert overrides("sphere_color") == spheres
    assert cmd.get("cartoon_color", "m") == "red"
    assert cmd.get_color_tuple("mine") == pytest.approx((0.2, 0.4, 0.6))
    balls = {}
    cmd.iterate(
        "resn STU", "balls[elem] = s.ball_and_stick_color", space={"balls": balls}
    )
    for element, color in balls.items():
        assert color == 0x40000000 | int(palettes.CPK[element], 16), element
    stored = set()
    cmd.iterate(
        "not resn STU", "stored.add(s.ball_and_stick_color)", space={"stored": stored}
    )
    assert stored == {None}  # only that residue

    # the ray tracer gets balls in those colors and spheres in theirs
    scene = cmd.get_povray()[1]
    assert "0.7843,0.7843,0.7843" in scene.replace(" ", "")  # CPK carbon
    assert "1.0000,1.0000,0.0000" in scene.replace(" ", "")  # the yellow spheres

    # a scene and a session keep it; unset gives the atoms' colors back
    cmd.scene("cpk", "store")
    cmd.unset("ball_and_stick_color", "resn STU")
    cmd.iterate(
        "resn STU", "stored.add(s.ball_and_stick_color)", space={"stored": stored}
    )
    assert stored == {None}
    cmd.scene("cpk", "recall", animate=0)
    again = {}
    cmd.iterate(
        "resn STU", "again[elem] = s.ball_and_stick_color", space={"again": again}
    )
    assert again == balls

    with pytest.raises(Exception):
        cmd.color_cpk("m", "spheres")


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_session(tmp_path, ext):
    cmd.fragment("cys", "m")
    cmd.show_as("ball_and_stick")
    cmd.color_cpk("m", "ball_and_stick")
    cmd.color_cpk("name SG")
    before = cmd.get_povray()[1]
    atoms = _atom_colors()
    path = str(tmp_path / ("cpk." + ext))
    cmd.save(path)
    cmd.reinitialize()
    cmd.load(path)
    assert _atom_colors() == atoms and cmd.get_povray()[1] == before


def test_menu_is_the_command():
    cmd.fragment("cys", "m")
    cmd.fragment("ala", "n")
    cmd.color("green")
    rows = {
        row[1]: row[2]
        for row in menu.by_elem(cmd, "m")
        if row[0] == 1 and isinstance(row[2], str)
    }
    row = [command for label, command in rows.items() if label.startswith("CPK")]
    assert len(row) == 1
    cmd.do(row[0], echo=0)
    by_menu = _atom_colors("m")
    cmd.color("green")
    cmd.color_cpk("m")
    assert _atom_colors("m") == by_menu and by_menu["CYS", "SG"] == _rgb("ffc832")
    assert set(_atom_colors("n").values()) == {(0.0, 1.0, 0.0)}

    balls = {
        row[1]: row[2]
        for row in menu.by_rep_sub(cmd, "ball and stick", "ball_and_stick_color", "m")
        if row[0] == 1
    }
    assert "CPK (balls only)" in balls and "by element" in balls and "unset" in balls
    cmd.do(balls["CPK (balls only)"], echo=0)
    found = set()
    cmd.iterate(
        "m and elem S", "found.add(s.ball_and_stick_color)", space={"found": found}
    )
    assert found == {0x40000000 | 0xFFC832}
    assert _atom_colors("m") == by_menu  # the atoms were not touched
    # the same entry is not offered for other representations
    assert "CPK (balls only)" not in {
        r[1] for r in menu.by_rep_sub(cmd, "spheres", "sphere_color", "m")
    }
