import pytest
import pymol
from pymol import cmd, testing

pytest.importorskip("rdkit")


def _stereo(selection):
    cmd.assign_stereo()
    labels = []
    cmd.iterate(selection, 'labels.append(stereo)', space=locals())
    return labels


def test_assign_stereo_rdkit():
    assert cmd.count_atoms("stereo R") == 0

    cmd.load(testing.datafile("1ehz-5.pdb"), "m1")
    cmd.assign_stereo(method="rdkit")

    assert cmd.count_atoms("stereo R & not elem P") == 15
    assert cmd.count_atoms("stereo S") == 5

    with pytest.raises(pymol.CmdException):
        cmd.assign_stereo(method="schrodinger")


def testStereo():
    cmd.fragment('ala')
    cmd.remove('hydro')

    # default: S configuration
    assert _stereo('name CA') == ['S']

    # load R configuration (moves CB)
    ala_conf_R = {
        'N'  : (-0.67690, -1.23030, -0.49050),
        'CA' : (-0.00090,  0.06370, -0.49050),
        'C'  : ( 1.49910, -0.11030, -0.49050),
        'O'  : ( 2.03010, -1.22730, -0.50150),
    #   'CB' : (-0.50890,  0.85570,  0.72650), # S configuration
        'CB' : (-0.33784,  0.82664, -1.78310), # R configuration
    }
    cmd.alter_state(1, 'ala', '(x,y,z) = ala_conf_R.get(name)', space=locals())
    assert _stereo('name CA') == ['R']


def testStereoPYMOL2782():
    # L-Cysteine has R configuration
    cmd.fragment('cys')
    assert _stereo('name CA') == ['R']


def testStereoTwoObjects():
    # each object is read on its own; atoms outside the selection keep theirs
    cmd.fragment('cys', 'm1')
    cmd.fragment('ala', 'm2')
    cmd.assign_stereo('m2')
    assert cmd.count_atoms('stereo R+S') == 1
    assert _stereo('name CA') == ['R', 'S']
