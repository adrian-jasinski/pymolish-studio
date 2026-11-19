"""
PYMOL-3487 Partial load of ramps
"""

from os.path import join
from pymol import cmd, testing

data_dir = "PYMOL-3487-data"


def _assert_colors(colors=['red', 'yellow']):
    testing.ambient_only()
    cmd.orient()
    img = testing.get_imagearray(width=100, height=100, ray=1)
    for color in colors:
        testing.assert_image_has_color(color, img)
    return img


def test_order1():
    cmd.load(join(data_dir, "session1.pze"), partial=1)
    ramp1_index = cmd.get_color_index("ramp1")
    cmd.load(join(data_dir, "session2.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    cmd.load(join(data_dir, "session3.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    assert cmd.get_session()["color_ext"] == [
        ["ramp1", 1],
        ["ramp2", 1],
    ]
    _assert_colors()
    assert ramp1_index == -10
    ramp2_index = cmd.get_color_index("ramp2")
    assert ramp2_index == -11


def test_order2():
    cmd.load(join(data_dir, "session2.pze"), partial=1)
    ramp1_index = cmd.get_color_index("ramp1")
    cmd.load(join(data_dir, "session3.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    ramp2_index = cmd.get_color_index("ramp2")
    cmd.load(join(data_dir, "session1.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    assert cmd.get_session()["color_ext"] == [
        ["ramp1", 1],
        ["ramp2", 1],
    ]
    _assert_colors()
    assert ramp1_index == -10
    assert ramp2_index == -11


def test_order3():
    cmd.load(join(data_dir, "session3.pze"), partial=1)
    ramp2_index = cmd.get_color_index("ramp2")
    cmd.load(join(data_dir, "session1.pze"), partial=1)
    assert cmd.get_color_index("ramp2") == ramp2_index
    ramp1_index = cmd.get_color_index("ramp1")
    cmd.load(join(data_dir, "session2.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    assert cmd.get_session()["color_ext"] == [
        ["ramp1", 1],
        ["ramp2", 1],
    ]
    _assert_colors()
    assert ramp1_index == -10
    assert ramp2_index == -11


def test_overwrite_existing():
    cmd.pseudoatom('existing1', pos=(1.4, 3.8, 0.0))
    cmd.pseudoatom('existing2', pos=(-1.0, 0.5, -0.1))
    cmd.ramp_new("ramp1", "existing1", [0, 10], ["green", "green"])
    ramp1_index = cmd.get_color_index("ramp1")
    cmd.ramp_new("ramp3", "existing2", [0, 10], ["magenta", "magenta"])
    ramp3_index = cmd.get_color_index("ramp3")
    assert cmd.get_color_index("ramp1") == ramp1_index
    assert ramp3_index != ramp1_index
    assert cmd.get_session()["color_ext"] == [
        ["ramp1", 1],
        ["ramp3", 1],
    ]
    assert ramp1_index == -10
    assert ramp3_index == -11

    cmd.show_as('surface', 'existing1 existing2')
    cmd.set('surface_color', 'ramp1', 'existing2')
    cmd.set('surface_color', 'ramp3', 'existing1')
    cmd.disable('ramp*')
    _assert_colors(['green', 'magenta'])

    cmd.load(join(data_dir, "session1.pze"), partial=1)
    cmd.load(join(data_dir, "session2.pze"), partial=1)
    cmd.load(join(data_dir, "session3.pze"), partial=1)
    assert cmd.get_color_index("ramp1") == ramp1_index
    assert cmd.get_color_index("ramp3") == ramp3_index
    assert cmd.get_session()["color_ext"] == [
        ["ramp1", 1],
        ["ramp3", 1],
        ["ramp2", 1],
    ]
    ramp2_index = cmd.get_color_index("ramp2")
    assert ramp1_index == -10
    assert ramp3_index == -11
    assert ramp2_index == -12

    cmd.recolor()
    img = _assert_colors(['red', 'yellow', 'magenta'])
    testing.assert_image_has_not_color('green', img)

    assert cmd.get_setting_int("surface_color", "mol1") == ramp1_index
    assert cmd.get_setting_int("surface_color", "mol2") == ramp2_index
    assert cmd.get_setting_int("surface_color", "existing1") == ramp3_index
    assert cmd.get_setting_int("surface_color", "existing2") == ramp1_index
