'''
PYMOL-1356
spheroid command does not work
'''

import pytest
from pymol import cmd, testing, stored

pytestmark = testing.requires('gui')


@pytest.mark.parametrize("use_shader", [True, False])
def testSpheresForSpheroidTrajectory(use_shader):
    pdbfile = testing.datafile("sampletrajectory.pdb")
    dcdfile = testing.datafile("sampletrajectory.dcd")
    cmd.load(pdbfile)
    cmd.load_traj(dcdfile)
    cmd.set('use_shaders', use_shader)
    cmd.spheroid("sampletrajectory", 3)
    testing.ambient_only()
    cmd.color('blue')
    cmd.show_as('spheres')
    testing.assert_image_has_color('blue')
