"""
stage: a floor under what is shown, horizontal for the view, a mirror image
under it, and "off" that leaves nothing behind. The three light setups are
looks made of settings that exist.
"""

import numpy
import pytest

from pymol import CmdException, cmd, preset, stage as stage_module


@pytest.fixture(autouse=True)
def no_stage():
    yield
    cmd.stage("off")
    preset.look("default")


def _up():
    view = cmd.get_view()
    return numpy.array(view[1:9:3])


def test_floor():
    with pytest.raises(CmdException, match="nothing is shown"):
        cmd.stage()
    cmd.fragment("trp", "m")
    cmd.fragment("ala", "hidden")
    cmd.translate([0, -40, 0], "hidden")
    cmd.disable("hidden")
    cmd.turn("z", 30)
    view, up = cmd.get_view(), _up()
    fog = cmd.get_setting_int("ray_trace_fog")
    cmd.stage()
    assert "_floor" in cmd.get_names("all") and "_floor" not in cmd.get_names("public")
    # horizontal for the view it was made in, 2 A under the lowest shown atom
    low, high = cmd.get_extent("_floor")
    corners = numpy.array([low, high])
    atoms = cmd.get_coords("m")
    height = (atoms @ up).min() - stage_module.MARGIN
    assert float(((cmd.get_coords("m") @ up) > height).all())
    # (the hidden object, 40 A lower, did not push the floor down)
    assert height > (cmd.get_coords("hidden") @ up).max()
    assert numpy.ptp(corners @ up) < numpy.ptp(corners, axis=0).max()  # flat along "up"
    # the view was tilted to show it, the rear plane moved back and fog set
    # so that the far edge of the floor fades out; "off" gives all of it back
    assert cmd.get_view()[:9] != view[:9]
    assert cmd.get_view()[16] > view[16] and cmd.get_setting_int("ray_trace_fog") == 1
    cmd.stage("off")
    assert "_floor" not in cmd.get_names("all")
    assert cmd.get_view() == pytest.approx(view, abs=1e-4)
    assert cmd.get_setting_int("ray_trace_fog") == fog
    # twice in a row is one floor and one tilt
    cmd.stage()
    cmd.stage()
    cmd.stage("off")
    assert cmd.get_view() == pytest.approx(view, abs=1e-4)
    with pytest.raises(CmdException, match="mode"):
        cmd.stage("ceiling")


def test_mirror():
    cmd.fragment("trp", "m")
    up = _up()
    atoms = cmd.get_coords("m")
    height = (atoms @ up).min() - stage_module.MARGIN
    cmd.stage("mirror")
    assert "_mirror_m" in cmd.get_names("all")
    assert "_mirror_m" not in cmd.get_names("public")  # not a row of the panels
    image = cmd.get_coords("_mirror_m")
    # each atom as far under the floor as the original is above it
    assert (image @ up - height) == pytest.approx(-(atoms @ up - height), abs=1e-3)
    assert float(cmd.get("cgo_transparency", "_floor")) == pytest.approx(0.25)
    cmd.stage("floor")  # a plain floor again: the copy goes
    assert "_mirror_m" not in cmd.get_names("all")
    cmd.stage("off")
    assert [n for n in cmd.get_names("all") if n.startswith("_")] == []


def test_lights():
    for name in ("studio", "top light", "soft shadow"):
        preset.look(name)  # every key is a setting the core knows
    assert cmd.get_setting_int("light_count") == 5
    preset.look("default")
    assert cmd.get_setting_int("light_count") == 2
    from pymol import menu

    # 30d: each in a submenu of the preset menu
    subs = {r[1]: [x[1] for x in r[2] if x[0] == 1] for r in menu.presets(cmd, "all") if isinstance(r[2], list)}
    assert subs["floor"] == ["floor", "floor with mirror image", "no floor"]
    assert subs["light"].index("standard light") < subs["light"].index("top light")
