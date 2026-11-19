
from pymol import cmd, testing, stored

pytestmark = testing.requires('no_edu')


@testing.requires('incentive')
def testClean():
    cmd.fragment('his')
    xyz1 = cmd.get_model('his').get_coord_list()
    energy = cmd.clean('his')
    xyz2 = cmd.get_model('his').get_coord_list()
    assert len(xyz1) == len(xyz2)

    # coords have changed
    assert xyz1 != xyz2

    # energy for HIS = 32.73887
    assert 30.0 < energy < 35.0
