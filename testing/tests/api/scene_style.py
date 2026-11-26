"""
35b: a scene keeps the style a preset or a coloring gives (cartoon type,
settings of atoms, bonds and objects, light and background, the definitions
of named colors) and brings it back; a setting that was not there when the
scene was stored is taken away again. color=0, rep=0 and settings=0 leave
their part alone; a scene of an older version changes no style.
"""

import re

import pytest

from pymol import cmd, preset, setting, stage, testing

# written by a preset, but no appearance
NOT_STYLE = {"auto_classify_atoms", "auto_show_classified"}
ATOM_SETTINGS = (
    "sphere_scale",
    "stick_radius",
    "cartoon_color",
    "sphere_color",
    "stick_color",
)
OBJECT_SETTINGS = ("stick_radius", "cartoon_transparency", "surface_color", "valence")
GLOBAL_SETTINGS = (
    "ambient",
    "ray_trace_mode",
    "light_count",
    "light",
    "bg_rgb",
    "depth_cue",
)


def _written_by_presets():
    """Names of settings in the code of the presets and of the stage."""
    names = set(setting.get_name_list())
    found = set()
    for module in (preset, stage):
        text = open(module.__file__).read()
        found |= set(re.findall(r"""['"]([a-z][a-z_0-9]+)['"]""", text)) & names
    for look in preset.LOOKS.values():
        found |= set(look)
    return sorted(found - NOT_STYLE)


def _other(name):
    """A value of a setting that is not the one it has."""
    kind, value = cmd.get_setting_tuple(name)
    if kind == 1:  # boolean
        return int(not value[0])
    if kind == 2:  # int
        return value[0] + 1
    if kind == 3:  # float
        return value[0] + 0.25
    if kind == 4:  # float3
        return [v * 0.5 + 0.1 for v in value]
    if kind == 5:  # color
        return "0x123456" if value[0] != 0x40123456 else "0x654321"
    return value[0] + "x"


def test_every_preset_setting_is_kept():
    """The inventory: what a preset, a look, a theme or the stage writes
    comes back with the scene, at the global and at the object level."""
    cmd.fragment("ala", "m")
    names = _written_by_presets()
    assert len(names) > 40 and "ambient" in names and "ball_and_stick_color" in names
    before = {name: cmd.get_setting_tuple(name) for name in names}
    cmd.scene("a", "store")
    for name in names:
        cmd.set(name, _other(name))
        cmd.set(name, _other(name), "m")  # the object had none
    changed = [name for name in names if cmd.get_setting_tuple(name) != before[name]]
    assert changed == names
    cmd.scene("a", "recall", animate=0)
    lost = [name for name in names if cmd.get_setting_tuple(name) != before[name]]
    assert lost == []
    left = {s[0] for s in cmd.get_object_settings("m") or ()}
    assert not left & set(names)


def _look(objects=("m",)):
    """What a scene has to bring back, as plain data."""
    atoms = []
    cmd.iterate(
        "all",
        "atoms.append((model, index, color, reps, cartoon, "
        + ", ".join("s." + name for name in ATOM_SETTINGS)
        + "))",
        space={"atoms": atoms},
    )
    objects = {
        name: sorted((s[0], s[2]) for s in cmd.get_object_settings(name) or ())
        for name in cmd.get_names("objects")
    }
    bonds = [
        cmd.get_bond(name, "all", quiet=1)
        for name in ("stick_radius", "stick_color", "valence")
    ]
    world = [cmd.get_setting_tuple(name) for name in GLOBAL_SETTINGS]
    return atoms, objects, bonds, world, cmd.get_color_tuple("mine")


def _style_a():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.set_color("mine", [0.2, 0.4, 0.6])
    cmd.show_as("cartoon", "polymer")
    cmd.show("sticks", "organic")
    cmd.cartoon("tube", "resi 100-140")
    cmd.color("mine", "resi 100-120")
    cmd.set("cartoon_color", "yellow", "resi 130-140")  # atoms
    cmd.set("sphere_scale", 0.41, "organic")  # atoms
    cmd.set("stick_radius", 0.33, "m")  # the object
    cmd.set_bond("stick_radius", 0.12, "organic and elem C")
    cmd.set("ambient", 0.31)
    cmd.scene("a", "store")
    return _look()


def _style_b():
    """Another preset, look and theme, new colors, and overrides that
    were not there before."""
    preset.ball_and_stick("m")
    preset.look("comic")
    preset.theme("night", "m")
    cmd.cartoon("rectangle", "resi 100-200")
    cmd.color("red", "resi 100-110")
    cmd.set_color("mine", [0.9, 0.1, 0.1])  # redefined
    cmd.color("mine", "resi 121-125")  # and used: only then the scene keeps it
    cmd.set("cartoon_color", "blue", "resi 150-160")
    cmd.set("sphere_color", "green", "organic")
    cmd.set("sphere_scale", 0.2, "organic and elem N")
    cmd.set("cartoon_transparency", 0.5, "m")
    cmd.set("valence", 0, "m")
    cmd.set_bond("stick_color", "orange", "organic")
    cmd.set_bond("valence", 1, "organic and elem C")
    cmd.scene("b", "store")
    return _look()


def test_a_b_a():
    a = _style_a()
    b = _style_b()
    assert (
        a != b
        and a[0] != b[0]
        and a[1] != b[1]
        and a[2] != b[2]
        and a[3] != b[3]
        and a[4] != b[4]
    )
    atoms = cmd.count_atoms()
    for name, look in (("a", a), ("b", b), ("a", a), ("b", b)):
        cmd.scene(name, "recall", animate=0)
        now = _look()
        for part, was, got in zip(
            ("atoms", "objects", "bonds", "world", "color"), look, now
        ):
            assert was == got, "%s of scene %s" % (part, name)
    assert cmd.count_atoms() == atoms  # nothing of the molecule is touched

    # an update, a rename and a copy of the list keep the style with the scene
    cmd.scene("a", "recall", animate=0)
    cmd.set("ambient", 0.77)
    cmd.scene("a", "update")
    cmd.scene("a", "rename", new_key="first")
    cmd.scene_order("b first")
    cmd.scene("b", "recall", animate=0)
    assert cmd.get_setting_float("ambient") != pytest.approx(0.77)
    cmd.scene("first", "recall", animate=0)
    assert cmd.get_setting_float("ambient") == pytest.approx(0.77)
    assert _look()[:3] == a[:3]

    # an object that was deleted or renamed since is passed over
    cmd.set_name("m", "renamed")
    cmd.scene("b", "recall", animate=0)
    cmd.delete("renamed")
    cmd.scene("first", "recall", animate=0)
    assert cmd.get_names() == []


def test_parts():
    """color=0, rep=0, settings=0 and sele leave their part as it is."""
    a = _style_a()
    b = _style_b()

    def recall(**keywords):
        cmd.scene("b", "recall", animate=0)
        assert _look() == b
        cmd.scene("a", "recall", animate=0, **keywords)
        return _look()

    def atom_part(look, colors):
        """The colors, or the rest, of each atom: color, cartoon_color,
        sphere_color, stick_color against reps, cartoon, sizes."""
        pick = (2, 7, 8, 9) if colors else (3, 4, 5, 6)
        return [tuple(atom[i] for i in pick) for atom in look[0]]

    now = recall(color=0)
    assert atom_part(now, True) == atom_part(b, True) and now[4] == b[4]
    assert atom_part(now, False) == atom_part(a, False)
    assert cmd.get_setting_tuple("bg_rgb") == b[3][4]  # a color setting
    assert cmd.get_setting_float("ambient") == pytest.approx(0.31)  # of A

    now = recall(rep=0)
    assert atom_part(now, True) == atom_part(a, True) and now[4] == a[4]
    assert atom_part(now, False) == atom_part(b, False)

    now = recall(settings=0)  # as before 4.47: visibility and atom colors
    assert [atom[:4] for atom in now[0]] == [atom[:4] for atom in a[0]]
    assert [atom[4:] for atom in now[0]] == [atom[4:] for atom in b[0]]
    assert now[1:] == b[1:]

    now = recall(sele="resi 100-120")
    inside = {atom[1] for atom in now[0]} & set(cmd.index_list("resi 100-120"))
    for was_a, was_b, got in zip(a[0], b[0], now[0]):
        assert got == (was_a if got[1] in inside else was_b)

    # a scene stored without the style brings none back
    cmd.scene("b", "recall", animate=0)
    cmd.scene("plain", "store", settings=0)
    cmd.scene("a", "recall", animate=0)
    cmd.scene("plain", "recall", animate=0)
    assert _look()[1:] == a[1:] and [atom[4:] for atom in _look()[0]] == [
        atom[4:] for atom in a[0]
    ]


if not hasattr(cmd, "index_list"):

    def _index_list(selection):
        found = []
        cmd.iterate(selection, "found.append(index)", space={"found": found})
        return found

    cmd.index_list = _index_list


@pytest.mark.parametrize("ext", ["pse", "psex"])
def test_session(tmp_path, ext):
    a = _style_a()
    b = _style_b()
    path = str(tmp_path / ("scenes." + ext))
    cmd.save(path)
    cmd.reinitialize()
    cmd.load(path)
    for name, look in (("a", a), ("b", b), ("a", a)):
        cmd.scene(name, "recall", animate=0)
        assert _look() == look, name

    # a scene as an older version wrote it: six items, no style
    session = cmd.get_session()
    order, scenes = session["moviescenes"]
    index = scenes.index("a") + 1
    assert len(scenes[index]) == 7
    scenes[index] = scenes[index][:6]
    scenes[index][0] &= ~64
    cmd.set_session(session)
    cmd.scene("b", "recall", animate=0)
    cmd.scene("a", "recall", animate=0)
    now = _look()
    assert [atom[:4] for atom in now[0]] == [
        atom[:4] for atom in a[0]
    ]  # as it always did
    assert [atom[4:] for atom in now[0]] == [atom[4:] for atom in b[0]] and now[
        1:
    ] == b[1:]


def test_movie_visits_scenes():
    """Playback recalls scenes in the core: the style comes with them."""
    a = _style_a()
    b = _style_b()
    cmd.mset("1x20")
    cmd.mview("store", 1, scene="a")
    cmd.mview("store", 10, scene="b")
    cmd.mview("store", 20, scene="a")
    for frame, look in ((1, a), (10, b), (20, a)):
        cmd.frame(frame)
        cmd.refresh()
        now = _look()
        assert now[0] == look[0] and now[1] == look[1] and now[2] == look[2], frame
        assert now[3][0] == look[3][0]  # ambient
