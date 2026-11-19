"""
pymol.shots: a list of shots built into the movie of the core.
"""

import pytest
from pymol import cmd, shots, testing


@pytest.fixture(autouse=True)
def peptide(clean_session):
    cmd.set("movie_fps", 30)
    cmd.fab("ACDEFGHIK", "pep")
    cmd.orient()


def _view(frame):
    cmd.frame(frame)
    return [round(x, 2) for x in cmd.get_view()[:9]]


def test_turn():
    assert shots.build([shots.shot("turn", "", 2)]) == [1]
    assert cmd.get_movie_length() == 60
    first, half, last = _view(1), _view(30), _view(60)
    assert first == last  # a full turn ends where it began
    assert first[0] == pytest.approx(-half[0], abs=5e-2)  # half way: turned around
    # a quarter turn does not come back
    shots.build([shots.shot("turn", "", 2, angle=90)])
    assert _view(1) != _view(60)


def test_scenes_hold_cut():
    cmd.scene("a", "store")
    cmd.turn("x", 90)
    cmd.scene("b", "store")
    b = [round(x, 2) for x in cmd.get_view()[:9]]
    cmd.turn("x", -90)
    a = [round(x, 2) for x in cmd.get_view()[:9]]
    starts = shots.build(
        [
            shots.shot("scene", "a", 2),
            shots.shot("scene", "b", 6),
            shots.shot("hold", "", 1),
        ]
    )
    assert starts == [1, 61, 241]
    assert cmd.get_movie_length() == 270
    assert _view(1) == a
    assert _view(60) == a  # a scene is held to its end
    flight = _view(61 + 30)  # two seconds of flight, then b
    assert flight != a
    assert flight != b
    assert _view(61 + 60) == b
    assert _view(270) == b
    # a cut: b from the first frame of its shot
    cut = shots.shot("scene", "b", 6, start="cut")
    shots.build([shots.shot("scene", "a", 2), cut])
    assert _view(61) == b


def test_rock_nutate_states():
    cmd.create("pep", "pep", 1, 2)
    cmd.create("pep", "pep", 1, 3)
    starts = shots.build(
        [shots.shot(kind, "", 4) for kind in ("rock", "nutate", "states")]
    )
    assert starts == [1, 121, 241]
    rest = _view(1)
    assert _view(31) != rest  # swung out
    assert _view(120) == rest  # and back
    assert _view(121 + 24) != rest
    assert _view(240) == rest
    cmd.frame(241)
    assert cmd.get_state() == 1
    cmd.frame(360)
    assert cmd.get_state() == 3


def test_effect_and_clear():
    fade = shots.shot("hold", "", 1, effect="fade in surface")
    shots.build([fade])
    cmd.frame(30)
    cmd.frame(1)
    assert cmd.get_setting_float("transparency") == 1
    cmd.frame(30)
    assert cmd.get_setting_float("transparency") == 0
    # the next build has no trace of the fade
    shots.build([shots.shot("hold", "", 1)])
    cmd.set("transparency", 0.5)
    cmd.frame(30)
    cmd.frame(1)
    assert cmd.get_setting_float("transparency") == 0.5
    assert shots.build([]) == []
    assert cmd.get_movie_length() == 0


def test_tour_view_describe():
    cmd.load(testing.datafile("1oky-frag.pdb"), "frag")
    cmd.scene("s1", "store")
    cmd.select("mysele", "pep & resi 3")
    assert [s["target"] for s in shots.tour("scenes")] == ["s1"]
    chains = shots.tour("chains")
    assert [s["kind"] for s in chains[:2]] == ["zoom", "turn"]
    assert (cmd.count_atoms(chains[0]["target"]) > 0) == True
    assert shots.tour("selections")[0]["target"] == "mysele"
    pytest.raises(ValueError, shots.tour, "nothing")
    view = shots.shot("view")
    assert view["view"] == cmd.get_view()
    text = shots.describe([view, shots.shot("turn")])
    space = {}
    exec(text, space)  # the script builds the same movie
    assert cmd.get_movie_length() == 120 + 240
    frames, seconds, size = shots.estimate(40, 30, ray=1)
    assert frames == 360
    assert seconds > 0
    assert size > 0
