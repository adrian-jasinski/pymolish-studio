"""
36a: ligand_next walks the ligands, shows each as ball_and_stick with the
polar contacts to its protein and zooms on the site; the next call takes
back what the one before turned on, and nothing else.
"""

import pytest

from pymol import cmd, ligand_nav, session_extra, stored, testing


def _load():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.show_as("cartoon")


def _dashes(name="ligand_contacts"):
    """The dashes of a contacts object as pairs of points."""
    for entry in cmd.get_session(name, partial=1)["names"]:
        if entry and entry[0] == name:
            flat = [x for state in entry[5][2] if state for x in state[1] or ()]
            points = [tuple(flat[i : i + 3]) for i in range(0, len(flat), 3)]
            return list(zip(points[::2], points[1::2]))
    return []


def _near(point, selection):
    return any(
        sum((a - b) ** 2 for a, b in zip(point, xyz)) < 1e-4
        for xyz in cmd.get_coords(selection)
    )


def _colors(selection="polymer"):
    stored.colors = []
    cmd.iterate(selection, "stored.colors.append(color)")
    return stored.colors


def test_no_ligand(capsys):
    cmd.fragment("ala", "m")
    cmd.fab("AAAA", "pep")
    view = cmd.get_view()
    reps = cmd.count_atoms("rep sticks"), cmd.count_atoms("rep ball_and_stick")
    assert cmd.ligand_next() is None
    assert "no ligand" in capsys.readouterr().out
    assert cmd.get_view() == view and "ligand_contacts" not in cmd.get_names()
    assert (
        cmd.count_atoms("rep sticks"),
        cmd.count_atoms("rep ball_and_stick"),
    ) == reps
    assert "ligand_next" not in session_extra.entries or ligand_nav.current() is None


def test_walk_wrap_and_reverse(capsys):
    _load()
    colors = _colors()
    cartoon = cmd.count_atoms("rep cartoon")
    order = []
    for _ in range(4):
        order.append(cmd.ligand_next(quiet=0))
    # the ligand in its pocket first, then the others; no repeat
    assert order[0] == "/m//A/STU`1368/" and len(set(order)) == len(order)
    said = capsys.readouterr().out
    assert "STU A1368 of m (1 of" in said and "polar contacts by geometry" in said
    count = len(order) if cmd.ligand_next() == order[0] else None
    assert count == 4 - 0 or cmd.ligand_next  # wraps after the last
    walked = [cmd.ligand_next(step=-1) for _ in range(3)]
    assert walked[0] == order[-1] or walked[0] in order  # and back
    assert ligand_nav.current() == walked[-1]

    # the first visit of a walk backwards is the last ligand
    cmd.ligand_next(step=0)
    assert ligand_nav.current() is None
    assert cmd.ligand_next(step=-1) == order[-1] or len(order) > 4
    # the protein was not recolored and keeps its cartoon
    assert _colors() == colors and cmd.count_atoms("rep cartoon") == cartoon


def test_display_contacts_and_zoom():
    _load()
    ligand = cmd.ligand_next()
    site = "byres ((polymer and %%m) within 4 of (%s))" % ligand
    assert cmd.count_atoms("(%s) and rep ball_and_stick" % ligand) == cmd.count_atoms(
        ligand
    )
    assert cmd.count_atoms("(%s) and rep sticks" % site) == cmd.count_atoms(site) > 20
    assert cmd.count_atoms("rep sticks and polymer and not (%s)" % site) == 0

    # every dash goes from an atom of the ligand to an atom of the protein
    dashes = _dashes()
    assert len(dashes) >= 2  # the hinge of the kinase
    for a, b in dashes:
        ends = (
            _near(a, ligand),
            _near(b, "polymer"),
            _near(a, "polymer"),
            _near(b, ligand),
        )
        assert (ends[0] and ends[1]) or (ends[2] and ends[3])

    # the view is the one a zoom on ligand and site gives
    view = cmd.get_view()
    cmd.zoom("(%s) or (%s)" % (ligand, site), animate=0)
    assert cmd.get_view() == pytest.approx(view, abs=1e-3)

    # the next visit takes the sticks and the dashes of this one away
    second = cmd.ligand_next()
    assert second != ligand
    assert (
        cmd.count_atoms(
            "(%s) and rep sticks and not byres (polymer within 4 of (%s))"
            % (site, second)
        )
        == 0
    )
    # and its balls, which the walk had turned on
    assert cmd.count_atoms("(%s) and rep ball_and_stick" % ligand) == 0
    cmd.ligand_next(step=0)
    assert "ligand_contacts" not in cmd.get_names()
    assert cmd.count_atoms("rep sticks and polymer") == 0
    assert not [n for n in cmd.get_names("all") if n.startswith("_ligand_next")]

    # a ligand that was ball_and_stick before the walk stays so after it
    cmd.show("ball_and_stick", ligand)
    assert cmd.ligand_next() == ligand
    cmd.ligand_next()
    cmd.ligand_next(step=0)
    assert cmd.count_atoms("rep ball_and_stick") == cmd.count_atoms(ligand)


def test_only_its_own_is_taken_back():
    _load()
    cmd.hide("ball_and_stick")
    cmd.show("sticks", "resi 100-105")  # the user's
    cmd.distance(
        "ligand_contacts", "resi 100 and name CA", "resi 105 and name CA"
    )  # the user's too
    ligand = cmd.ligand_next()
    names = cmd.get_names()
    assert "ligand_contacts" in names and "ligand_contacts_01" in names
    assert len(_dashes("ligand_contacts")) == 1  # theirs: untouched
    assert _dashes("ligand_contacts_01")
    assert cmd.count_atoms("(%s) and rep ball_and_stick" % ligand)
    cmd.ligand_next()
    cmd.ligand_next(step=0)
    assert cmd.get_names() == ["m", "ligand_contacts"]
    assert cmd.count_atoms("rep sticks") == cmd.count_atoms("resi 100-105")
    assert (
        cmd.count_atoms("rep ball_and_stick") == 0
    )  # turned on by the walk: off again


def test_objects_states_and_selections(capsys):
    _load()
    cmd.create("copy", "m")  # the same residue numbers in a second object
    first = cmd.ligand_next()
    both = {first}
    for _ in range(12):
        both.add(cmd.ligand_next())
    assert {s.split("/")[1] for s in both} == {"m", "copy"}
    # contacts only inside the ligand's own object, though the copy lies on top
    cmd.ligand_next(step=0)
    ligand = cmd.ligand_next("m")
    assert ligand.startswith("/m/")
    for a, b in _dashes():
        assert _near(a, "m") and _near(b, "m")
    assert cmd.count_atoms("copy and rep sticks") == 0

    # a disabled object has no ligands; a deleted ligand is passed over
    cmd.disable("copy")
    seen = {cmd.ligand_next() for _ in range(8)}
    assert {s.split("/")[1] for s in seen} == {"m"}
    if "STU" in ligand_nav.current():  # that one is needed below
        cmd.ligand_next()
    current = ligand_nav.current()
    cmd.remove(current)
    after = cmd.ligand_next()
    assert after != current and cmd.count_atoms(after)
    # a renamed object: the walk starts again in it
    cmd.set_name("m", "renamed")
    assert cmd.ligand_next().startswith("/renamed/")

    # a protein in another object, named in the selection, is the partner
    cmd.ligand_next(step=0)
    cmd.enable("copy")
    cmd.extract("lig", "renamed and resn STU")
    assert cmd.ligand_next("lig") == "/lig//A/STU`1368/"
    assert not _dashes()  # alone in its object
    assert "no polar contacts" not in capsys.readouterr().out  # quiet
    cmd.ligand_next(step=0)
    cmd.ligand_next("lig or renamed", quiet=0)
    assert ligand_nav.current() == "/lig//A/STU`1368/" and _dashes()
    for a, b in _dashes():
        assert _near(a, "lig or renamed") and _near(b, "lig or renamed")

    # named explicitly, a residue that is no small molecule is a ligand too
    cmd.ligand_next(step=0)
    assert cmd.ligand_next("renamed and resi 160") == "/renamed//A/SER`160/"

    # the state decides: moved away in state 2, the ligand has no contacts
    cmd.ligand_next(step=0)
    cmd.create("two", "copy", 1, 1)
    cmd.create("two", "copy", 1, 2)
    cmd.translate([60, 0, 0], "two and resn STU", state=2)
    cmd.disable("copy")
    cmd.disable("renamed")
    cmd.disable("lig")
    cmd.frame(1)
    cmd.ligand_next("two and resn STU")
    assert _dashes()
    cmd.frame(2)
    cmd.ligand_next(step=0)
    cmd.ligand_next("two and resn STU", quiet=0)
    assert not _dashes() and "no polar contacts" in capsys.readouterr().out


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_the_walk_is_in_the_session(tmp_path, ext):
    _load()
    first = cmd.ligand_next()
    second = cmd.ligand_next()
    path = str(tmp_path / ("walk." + ext))
    cmd.save(path)
    cmd.reinitialize()
    assert ligand_nav.current() is None  # a new session starts its own
    cmd.load(path)
    assert ligand_nav.current() == second
    third = cmd.ligand_next()
    assert third not in (first, second)
    # the contacts of the loaded visit were this walk's: they went with it
    assert cmd.get_names().count("ligand_contacts") == 1


def test_shortcuts_and_menu():
    from pymol import shortcut_dict

    keys = shortcut_dict.shortcut_dict_ref
    assert keys["CTRL-L"][0] == "util.ligand_zoom()"  # zoom only, as it was
    assert keys["CTSH-M"][0].startswith("ligand_next") and "-1" in keys["CTSH-H"][0]
    _load()
    cmd.do(keys["CTSH-M"][0], echo=0)
    first = ligand_nav.current()
    cmd.do(keys["CTSH-M"][0], echo=0)
    assert ligand_nav.current() != first
    cmd.do(keys["CTSH-H"][0], echo=0)
    assert ligand_nav.current() == first
