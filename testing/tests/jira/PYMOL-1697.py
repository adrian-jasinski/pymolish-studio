import pytest
import os
from pymol import cmd, testing, stored

pytestmark = testing.requires('no_edu')


@pytest.mark.parametrize("discr", [1, 0])
@testing.requires('incentive')
@testing.requires('undo')
def testUndoAfterRemoveAtomOnDiscrete(discr):
    cmd.set('suspend_undo', 0)
    cmd.load(testing.datafile('ligs3d.sdf'), discrete=discr)
    natms = cmd.count_atoms()
    cmd.remove("index 1")
    cmd.undo()
    assert natms == cmd.count_atoms()


def testRegression2207():
    '''
        The initial fix for PYMOL-1697 crashed this example
        (PYMOL-2207)
        '''
    cmd.load(testing.datafile('1oky-frag.pdb'))
    cmd.create('1oky-frag', 'resi 80-100', 1, 2)
    cmd.remove('resi 85-95')
    # keep ray efford low
    cmd.viewport(50, 50)
    # caused segfault
    img = testing.get_imagearray(ray=1)
