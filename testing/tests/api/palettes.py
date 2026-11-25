"""
Object color palettes: the data (size, contrast against the background each
palette is made for, distance between neighbors in the cycle) and the
"palette" command (new objects, recolor, default, reinitialize, sessions).
"""

import pytest
import math

import pymol

from pymol import cmd, palettes, testing

BACKGROUND = {"dark": (0, 0, 0), "white": (1, 1, 1)}


def rgb(color):
    return [int(color[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def luminance(color):  # WCAG 2 relative luminance
    r, g, b = (
        v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in color
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + 0.05) / (low + 0.05)


@pytest.fixture(autouse=True)
def default_palette(clean_session):
    yield
    cmd.palette("default")


def carbon_colors():
    """Color index of the first carbon of each object."""
    colors = []
    for name in cmd.get_names():
        cmd.iterate(
            "first (%s & elem C)" % name, "colors.append(color)", space=locals()
        )
    return colors


def test_data(subtests):
    assert list(palettes.PALETTES) == [
            "vivid",
            "deep",
            "pastel",
            "soft",
            "colorblind",
            "nord",
            "dracula",
            "catppuccin",
            "chimerax",
            "halo",
        ]
    # 37c: thirty each. What a palette began with keeps its value and place:
    # (how many it had, its first color, the last of those)
    began = {
        "vivid": (21, "00e676", "aeea00"),
        "deep": (15, "1565c0", "8d6e63"),
        "pastel": (12, "8fe3ef", "b0bfd0"),
        "soft": (22, "6192c3", "9a49b6"),
        "colorblind": (18, "e69f00", "882255"),
        "nord": (8, "88c0d0", "5e81ac"),
        "dracula": (7, "8be9fd", "ff5555"),
        "catppuccin": (11, "89b4fa", "f5e0dc"),
        "chimerax": (10, "d2b48c", "800080"),
        "halo": (12, "00f4d6", "ff8a00"),
    }
    assert palettes.BUILTIN == tuple(began)
    for name, (background, colors) in palettes.PALETTES.items():
        with subtests.test(name):
            count, first, last = began[name]
            assert len(colors) == 30
            assert (colors[0], colors[count - 1]) == (first, last)
            assert len(set(colors)) == len(colors)
            values = [rgb(c) for c in colors]
            for a, b in zip(values, values[1:] + values[:1]):
                assert math.dist(a, b) > 0.2, (name, a, b)
            # colorblind: published sets for any background, not judged
            for value in values if background in BACKGROUND else ():
                assert contrast(value, BACKGROUND[background]) >= 3


def test_new_objects():
    cmd.palette("vivid")
    for name in ("ala", "gly", "ser"):
        cmd.fragment(name)
    vivid = [cmd.get_color_index("vivid_%02d" % i) for i in (1, 2, 3)]
    assert carbon_colors() == vivid
    assert cmd.get_object_color_index("gly") == vivid[1]
    testing.assert_array_equal(cmd.get_color_tuple("vivid_01"), rgb("00e676"), 1e-3)
    # only carbons
    assert cmd.count_atoms("ala & not elem C & color vivid_01") == 0

    cmd.delete("*")
    cmd.palette("default")
    for name in ("ala", "gly", "ser"):
        cmd.fragment(name)
    assert carbon_colors() == [26, 5, 154]


def test_recolor():
    for name in ("ala", "gly"):
        cmd.fragment(name)
    cmd.palette("deep")
    assert carbon_colors() == [26, 5]  # untouched
    cmd.palette("deep", recolor=1)
    deep = [cmd.get_color_index("deep_%02d" % i) for i in (1, 2, 3)]
    assert carbon_colors() == deep[:2]
    assert cmd.count_atoms("ala & elem O & color deep_01") == 0
    cmd.fragment("ser")  # continues the cycle
    assert carbon_colors() == deep

    cmd.palette("soft")
    cmd.util.color_objs()
    soft = cmd.get_color_index("soft_02")
    assert cmd.count_atoms("gly & color %d" % soft) == cmd.count_atoms("gly")


def test_chains():
    cmd.fab("AA", "m1", chain="A")
    cmd.fab("GG", "m2", chain="B")
    cmd.palette("vivid")
    cmd.set("auto_color_next", 5)
    cmd.util.cbc()
    for chain, color in (("A", "vivid_01"), ("B", "vivid_02")):
        assert cmd.count_atoms("chain %s & color %s" % (chain, color)) == cmd.count_atoms("chain " + chain)
    assert cmd.get_setting_int("auto_color_next") == 5
    cmd.palette("default")
    cmd.util.cbc("elem C")
    assert cmd.count_atoms("chain B & elem C & color cyan") == 4
    assert cmd.count_atoms("chain B & elem N & color vivid_02") == 2


def test_the_cycle_uses_all_thirty():
    cmd.palette("nord")  # it began with eight
    for i in range(31):
        cmd.fragment("gly", "p%02d" % i)
    names = ["nord_%02d" % (i % 30 + 1) for i in range(31)]
    assert carbon_colors() == [cmd.get_color_index(name) for name in names]
    assert len(set(carbon_colors())) == 30
    assert palettes.cycle() == names[:30]


def test_wraps_and_unknown():
    cmd.palette("deep")
    n = len(palettes.PALETTES["deep"][1])
    cmd.set("auto_color_next", n - 1)
    cmd.fragment("ala")
    cmd.fragment("gly")
    assert carbon_colors() == [cmd.get_color_index("deep_%02d" % i) for i in (n, 1)]
    pytest.raises(pymol.CmdException, cmd.palette, "nosuch")
    assert palettes.active == "deep"


def test_survives_reinitialize_and_session():
    cmd.palette("soft")
    cmd.reinitialize()
    cmd.fragment("ala")
    assert carbon_colors() == [cmd.get_color_index("soft_01")]
    testing.assert_array_equal(cmd.get_color_tuple("soft_01"), rgb("6192c3"), 1e-3)

    # a session saved without the palette colors drops them from the
    # color list; loading it must not leave the table pointing at nothing
    cmd.palette("default")
    cmd.reinitialize()
    cmd.fragment("gly")
    with testing.mktemp(".pse") as filename:
        cmd.save(filename)
        cmd.palette("soft")
        cmd.load(filename)
    cmd.fragment("ala")
    # the session brings its own auto_color_next: 1
    assert carbon_colors() == [26, cmd.get_color_index("soft_02")]
    testing.assert_array_equal(cmd.get_color_tuple("soft_01"), rgb("6192c3"), 1e-3)
