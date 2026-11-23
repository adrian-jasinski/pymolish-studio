"""
Undo and redo of a row of the preset menu (30f, the first piece of 21g):
the session is kept before the row runs; undo puts it back, redo goes
forward again. Without a kept step both restore coordinates as before.
"""

import pytest

from pymol import cmd, menu, preset, snapshots, stage, testing


def _row(label, sele="all"):
    """The command of a row of the preset menu, also of a submenu."""

    def find(rows):
        for row in rows:
            if row[0] == 1 and isinstance(row[2], str) and row[1] == label:
                return row[2]
            if row[0] == 1 and not isinstance(row[2], str):
                found = find(row[2])
                if found:
                    return found

    return find(menu.presets(cmd, sele))


def _look():
    """What a preset changes: representations, colors, an object setting,
    the light, the background, the view, the object names."""
    seen = []
    cmd.iterate("all", "seen.append((reps, color, cartoon))", space={"seen": seen})
    return (
        seen,
        cmd.get_names("all"),
        [round(v, 3) for v in cmd.get_view()],
        cmd.get("ambient"),
        cmd.get("bg_rgb"),
        cmd.get("bg_gradient"),
        cmd.get("cartoon_transparency", "m"),
    )


@pytest.fixture(autouse=True)
def tidy():
    yield
    stage.stage("off")
    cmd.reinitialize()  # light and background, and it empties the steps
    preset.solvent = False


def test_undo_redo():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.select("sele", "resn STU")
    cmd.scene("first", "store")
    start = _look()
    assert cmd.undo() is None and _look() == start  # nothing kept yet

    cmd.do(_row("ligands"), echo=0)  # reps, colors, a view, a measurement
    ligands = _look()
    assert ligands != start and "m_pol_conts" in cmd.get_names("all")
    cmd.do(_row("night"), echo=0)  # theme: colors and the background
    cmd.do(_row("studio"), echo=0)  # light
    cmd.do(_row("50%"), echo=0)  # cartoon transparency
    last = _look()
    assert cmd.get_setting_float("cartoon_transparency", "m") == 0.5

    for _ in range(3):
        cmd.undo()
    assert _look() == ligands
    cmd.undo()
    assert _look() == start and "m_pol_conts" not in cmd.get_names("all")
    assert cmd.get_names("selections") == ["sele"] and cmd.get_scene_list() == ["first"]
    cmd.undo()  # no step left: nothing happens
    assert _look() == start

    for _ in range(4):
        cmd.redo()
    assert _look() == last
    cmd.redo()
    assert _look() == last

    # a new step forgets what could be redone
    cmd.undo()
    cmd.do(_row("pretty"), echo=0)
    pretty = _look()
    cmd.redo()
    assert _look() == pretty


def test_undo_takes_back_what_came_after():
    # the limit that is written down: a snapshot is the whole session
    cmd.fragment("ala", "m")
    cmd.show_as("lines")
    cmd.do(_row("ball and stick"), echo=0)
    cmd.fragment("gly", "later")
    cmd.undo()
    assert cmd.get_names() == ["m"] and cmd.count_atoms("rep ball_and_stick") == 0
    cmd.redo()  # and redo brings all of it back
    assert (
        cmd.get_names() == ["m", "later"]
        and cmd.count_atoms("m & rep ball_and_stick") == 10
    )


def test_floor_and_solvent_state():
    # what lives in the modules, not in the session, goes back too
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    view = [round(v, 3) for v in cmd.get_view()]
    cmd.do(_row("floor"), echo=0)
    assert stage._state["tilt"] and stage.FLOOR in cmd.get_names("all")
    cmd.undo()
    assert not stage._state["tilt"] and stage.FLOOR not in cmd.get_names("all")
    stage.stage("off")  # would turn the view back a second time
    assert [round(v, 3) for v in cmd.get_view()] == view
    cmd.do(_row("show solvent"), echo=0)
    assert preset.solvent
    cmd.undo()
    assert not preset.solvent


def test_limits(capsys):
    cmd.fragment("ala", "m")
    for _ in range(snapshots.STEPS + 3):
        cmd.do(_row("ball and stick"), echo=0)
    assert len(snapshots._undo) == snapshots.STEPS
    # too many atoms for the memory: the preset runs, without a step
    snapshots.clear()
    capsys.readouterr()
    old, snapshots.ATOMS = snapshots.ATOMS, 25
    try:
        cmd.do(_row("pretty"), echo=0)  # 10 atoms: kept
        cmd.do(_row("pretty"), echo=0)
        cmd.do(_row("pretty"), echo=0)  # 30 over three steps: the oldest goes
        assert len(snapshots._undo) == 2
        cmd.fragment("trp", "big")
        cmd.do(_row("ball and stick"), echo=0)
        assert len(snapshots._undo) == 2 and cmd.count_atoms("big & rep ball_and_stick")
        assert "cannot be undone" in capsys.readouterr().out
    finally:
        snapshots.ATOMS = old


def test_emptied_and_coordinates(tmp_path):
    cmd.fragment("ala", "m")
    cmd.do(_row("pretty"), echo=0)
    cmd.reinitialize()
    assert not snapshots._undo and not snapshots._redo
    # a session file that is opened is another document
    cmd.fragment("ala", "m")
    cmd.save(str(tmp_path / "s.pse"))
    cmd.do(_row("pretty"), echo=0)
    cmd.load(str(tmp_path / "s.pse"))
    assert not snapshots._undo
    # without a step, undo and redo are the coordinate ring of the core
    before = cmd.get_coords("m").copy()
    cmd.push_undo("m")
    cmd.translate([5, 0, 0], "m", camera=0)
    cmd.undo()
    assert abs(cmd.get_coords("m") - before).max() < 1e-4
    cmd.redo()
    assert abs(cmd.get_coords("m") - before).max() > 4
