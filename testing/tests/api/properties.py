"""
Object properties: a property can be set again with a value of another
type, and deleted.
"""

from pymol import cmd


def test_change_type():
    cmd.fragment("ala", "m1")
    # each step replaced a value of another type: until 4.27.0 the second
    # one ended the program (std::bad_variant_access)
    for value in (-6.5, 12, "see note", 3.25, True, "x", 7, 0.5):
        cmd.set_property("score", value, "m1")
        assert cmd.get_property("score", "m1") == value
        assert type(cmd.get_property("score", "m1")) is type(value)
    assert cmd.get_property_list("m1") == ["score"]
    cmd.set_property("score", None, "m1")
    assert not cmd.get_property_list("m1")
