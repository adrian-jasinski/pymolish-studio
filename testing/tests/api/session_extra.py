"""
The "pymolish" key of a session: what a feature keeps there comes back from
a .pse and a .psex, an entry of a newer version survives load and save,
reinitialize and a session without the key empty it.
"""

import pytest

from pymol import cmd, session_extra


def test_unknown_entries_survive():
    cmd.fragment("ala")
    session = cmd.get_session()
    assert "pymolish" not in session  # nothing to keep: no key
    future = {"version": 9, "hologram": {"depth": [1, 2]}, "table": {"columns": ["a"]}}
    session["pymolish"] = future
    cmd.set_session(session)
    assert session_extra.entries["hologram"] == {"depth": [1, 2]}
    again = cmd.get_session()["pymolish"]
    assert again == future  # the newer version number too
    assert again["hologram"] is not session_extra.entries["hologram"]  # a copy


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_file_round_trip(tmp_path, ext):
    cmd.fragment("ala")
    session_extra.entries["table"] = {"columns": ["score"], "hidden": ["note"]}
    path = str(tmp_path / ("s." + ext))
    cmd.save(path)
    cmd.reinitialize()
    assert session_extra.entries == {}
    cmd.load(path)
    assert session_extra.entries == {
        "version": session_extra.VERSION,
        "table": {"columns": ["score"], "hidden": ["note"]},
    }
    assert cmd.count_atoms() == 10

    # a session without the key leaves nothing of the one before
    cmd.reinitialize()
    cmd.fragment("gly")
    plain = cmd.get_session()
    session_extra.entries["table"] = {"columns": ["x"]}
    cmd.set_session(plain)
    assert session_extra.entries == {}
