'''
CCP4/MRC ORIGIN
'''

import pytest
from chempy import cpv
from pymol import cmd, testing

EDGELENGTHS = (5.85, 5.85, 5.85)
ORIGINS = {
    # only SKWTRN
    "h2o-elf-skwtrn.ccp4": (1.2, 3.4, 5.6),
    # NSTART and SKWTRN, additive
    "h2o-elf-nstart-skwtrn.ccp4": (1.8, 3.85, 6.35),
    # NSTART and ORIGIN, not additive (NSTART is ignored)
    "h2o-elf-nstart-origin.mrc": (1.2, 3.4, 5.6),
    # only NSTART (not ignored)
    "h2o-elf-nstart.ccp4": (0.6, 0.45, 0.75),
}


@pytest.mark.parametrize("filename", ORIGINS)
def test(filename):
    cmd.load(testing.datafile(filename), 'map')

    ori = ORIGINS[filename]
    ext = [ori, cpv.add(ori, EDGELENGTHS)]

    testing.assert_array_equal(cmd.get_extent('map'), ext, delta=1e-3)

    with testing.mktemp('.map') as filename:
        cmd.save(filename, 'map')
        cmd.delete('*')
        cmd.load(filename, 'map')

    testing.assert_array_equal(cmd.get_extent('map'), ext, delta=1e-3)
