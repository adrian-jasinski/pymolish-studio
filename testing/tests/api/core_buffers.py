"""
Testing: commands whose scratch buffers changed in step 8c and that no
other test reached (coverage run of 2026-11-25).
"""

import pytest

from pymol import cmd, testing


def bond_orders(selection):
    return sorted(b.order for b in cmd.get_model(selection).bond)


def test_valence_guess():
    cmd.fragment("benzene", "m1")
    cmd.valence("1", "m1", "m1")
    assert bond_orders("m1") == [1] * 12
    cmd.valence("guess", "m1", "m1")
    assert bond_orders("m1") == [1] * 6 + [4] * 6


def test_valence_from_source():
    # crashed until 4.76.6: the first atom of a match marked bond -1
    cmd.fragment("benzene", "m1")
    cmd.fragment("benzene", "src")
    expected = bond_orders("src")
    cmd.valence("1", "m1", "m1")
    cmd.valence("copy", "m1", "m1", source="src")
    assert bond_orders("m1") == expected


def test_get_bond_print():
    cmd.fragment("benzene", "m1")
    cmd.alter("m1", 'numeric_type = 1 if elem == "C" else 2')
    result = cmd.get_bond_print("m1", 3, 2)
    # [type][type][bonds apart]: carbons 1, hydrogens 2
    assert result[1][1] == [6, 12, 12, 6]
    assert result[1][2] == [0, 6, 12, 12]
    assert result[2][2] == [6, 0, 0, 12]
    assert result[0] == [[0] * 4] * 3


def test_select_byfragment():
    cmd.fab("AAA", "m1")
    cmd.edit("m1 & resi 2 & name CA", "m1 & resi 2 & name CB")
    assert cmd.count_atoms("byfragment pk1") == cmd.count_atoms("_pkfrag1")
    assert cmd.count_atoms("byfragment pk2") == 4  # CB and its hydrogens
    assert cmd.count_atoms("byfragment none") == 0


def test_discrete_session(tmp_path):
    cmd.load(testing.datafile("ligs3d.sdf"), "m1", discrete=1)
    before = [cmd.count_atoms("m1", state=s) for s in range(1, 11)]
    assert cmd.count_discrete("m1") == 1
    filename = str(tmp_path / "discrete.pse")
    cmd.save(filename)
    cmd.delete("*")
    cmd.load(filename)
    assert cmd.count_discrete("m1") == 1
    assert [cmd.count_atoms("m1", state=s) for s in range(1, 11)] == before


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_sdf_property_names(tmp_path, newline):
    with open(testing.datafile("ligs3d.sdf")) as handle:
        molblock = handle.read().split("M  END")[0] + "M  END\n"
    data = (
        "> <plain>\n1\n\n"  # between angle brackets
        ">  r_m_strip\n3\n\n"  # prefix up to the second underscore goes
        "> a/b\n4\n\n"  # special character: not a name, stays data
        ">  noprefix\n5\n\n"  # no rule applies: not a name, stays data
        "$$$$\n"
    )
    filename = str(tmp_path / "props.sdf")
    with open(filename, "w", newline=newline) as handle:
        handle.write(molblock + data)
    cmd.load(filename, "m1", object_props="*")
    assert cmd.get_property_list("m1") == ["plain", "strip"]
    assert cmd.get_property("plain", "m1") == 1
    assert cmd.get_property("strip", "m1") == "3\n> a/b\n4\n>  noprefix\n5\n"


def test_async_builds_states():
    # coordinate sets of several states are updated in threads
    testing.ambient_only()
    cmd.fab("AAAA", "m1", ss=1)
    cmd.create("m1", "m1", 1, 2)
    cmd.create("m1", "m1", 1, 3)
    cmd.set("async_builds")
    cmd.set("max_threads", 4)
    cmd.set("all_states")
    cmd.show_as("sticks")
    cmd.color("yellow")
    cmd.orient()
    img = testing.get_imagearray(width=100, height=100, ray=1)
    testing.assert_image_has_color("yellow", img)


def test_sphere_normals_of_a_subset():
    # sphere_mode 7 read past its coordinate buffer until 4.76.14 when the
    # spheres were shown for a part of the object
    cmd.load(testing.datafile("1oky.pdb.gz"), "m1")
    cmd.hide("everything")
    cmd.set("sphere_mode", 7)
    cmd.show("spheres", "m1 & index 2000-2010")
    assert cmd.get_povray()[1].count("sphere{") == 11
