"""
The packed session file .psex: round trip, size against a .pse, files that
are renamed or damaged.
"""

import os
import shutil

import pytest

from pymol import CmdException, cmd, testing


def _scene():
    cmd.load(testing.datafile("1oky-frag.pdb"), "m1")
    cmd.fragment("gly", "m2")
    cmd.set_property("score", -6.4, "m2")
    cmd.select("s1", "m1 and name CA")
    cmd.scene("first", "store")
    cmd.mset("1 x10")
    return cmd.count_atoms(), cmd.get_view()


def _check(atoms, view):
    assert cmd.get_names() == ["m1", "m2"]
    assert cmd.count_atoms() == atoms
    assert cmd.count_atoms("s1") > 0
    assert cmd.get_scene_list() == ["first"]
    assert cmd.get_movie_length() == 10
    assert cmd.get_property("score", "m2") == -6.4
    testing.assert_array_equal(cmd.get_view(), view, 1e-4)


def test_round_trip(tmp_path):
    atoms, view = _scene()
    psex, pse = str(tmp_path / "a.psex"), str(tmp_path / "a.pse")
    cmd.save(pse)
    cmd.save(psex)
    assert cmd.get("session_file") == psex.replace("\\", "/")
    assert open(psex, "rb").read(5) == b"PSEX\x01"
    assert os.path.getsize(psex) * 5 < os.path.getsize(pse)
    for name in (psex, pse):
        cmd.reinitialize()
        cmd.load(name)
        _check(atoms, view)


def test_renamed(tmp_path):
    atoms, view = _scene()
    psex, pse = str(tmp_path / "a.psex"), str(tmp_path / "a.pse")
    cmd.save(pse)
    cmd.save(psex)
    as_pse, as_psex = str(tmp_path / "packed.pse"), str(tmp_path / "plain.psex")
    shutil.copy(psex, as_pse)
    shutil.copy(pse, as_psex)
    for name in (as_pse, as_psex):  # told apart by the mark, not the name
        cmd.reinitialize()
        cmd.load(name)
        _check(atoms, view)


def test_damaged(tmp_path):
    _scene()
    psex = str(tmp_path / "a.psex")
    cmd.save(psex)
    data = open(psex, "rb").read()
    cut, newer = str(tmp_path / "cut.psex"), str(tmp_path / "newer.psex")
    open(cut, "wb").write(data[: len(data) // 2])
    open(newer, "wb").write(b"PSEX\x02" + data[5:])
    cmd.reinitialize()
    with pytest.raises(CmdException, match="damaged"):
        cmd.load(cut)
    with pytest.raises(CmdException, match="newer"):
        cmd.load(newer)
    assert cmd.get_names() == []
