import numpy
import pytest
import pymol
from pymol import cmd, testing

pytestmark = testing.requires('no_edu')


def _bonds(name, state):
    """Lengths of all bonds of one state."""
    xyz = cmd.get_coords(name, state)
    idx = numpy.array([b[:2] for b in cmd.get_bonds(name)])
    return numpy.linalg.norm(xyz[idx[:, 0]] - xyz[idx[:, 1]], axis=1)


def testMorphLinear():
    cmd.set('suspend_undo')
    cmd.fab('ACD', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.rotate('x', 90, 'm1', 2)
    steps = 5
    cmd.morph('mout', 'm1', refinement=0, steps=steps)
    assert steps == cmd.count_states('mout')
    assert cmd.count_atoms('m1') == cmd.count_atoms('mout')
    # the ends are the two conformations
    assert numpy.allclose(cmd.get_coords('mout', 1), cmd.get_coords('m1', 1))
    assert numpy.allclose(
        cmd.get_coords('mout', steps), cmd.get_coords('m1', 2), atol=1e-3)
    # half way of a rotation by 90 degrees, a straight line shrinks the
    # molecule; the refinement gives the bonds their length back
    ref = _bonds('m1', 1)
    raw = abs(_bonds('mout', 3) - ref).mean()
    cmd.morph('mout', 'm1', refinement=3, steps=steps)
    assert abs(_bonds('mout', 3) - ref).mean() < raw / 4
    assert numpy.allclose(
        cmd.get_coords('mout', steps), cmd.get_coords('m1', 2), atol=1e-3)

    with pytest.raises(pymol.CmdException):
        cmd.morph('mout', 'm1', method='rigimol')


def testMorphTwoObjects():
    cmd.set('suspend_undo')
    cmd.fab('ACDEF', 'm1')
    cmd.fab('CDEFG', 'm2')
    cmd.translate([5, 0, 0], 'm2')
    cmd.morph('mout', 'm1', 'm2', refinement=0, steps=3)
    assert cmd.count_states('mout') == 3
    # the four residues both have, without the atoms only one of them has
    assert cmd.count_atoms('mout & resn CYS+ASP+GLU+PHE') == \
            cmd.count_atoms('mout') > 30
    assert cmd.count_atoms('mout') < cmd.count_atoms('m1')
    assert cmd.get_names() == ['m1', 'm2', 'mout']
    assert not any('morph' in n for n in cmd.get_names('all'))


def testMorphMulti():
    cmd.set('suspend_undo')
    cmd.fab('ACD', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)
    cmd.rotate('x', 90, 'm1', 2)
    cmd.rotate('x', 45, 'm1', 3)
    steps = 5
    cmd.morph('mout', 'm1', None, 0, 0, 0, steps, 'linear')
    assert steps * 2 == cmd.count_states('mout')
    assert cmd.count_atoms('m1') == cmd.count_atoms('mout')
    cmd.morph('mo2', 'm1', None, 0, -1, 0, steps, 'linear')
    assert steps * 3 == cmd.count_states('mo2')
    assert cmd.count_atoms('m1') == cmd.count_atoms('mo2')
