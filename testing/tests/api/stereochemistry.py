import pytest
import os
from pymol import movie, cmd, testing, stored

pytestmark = testing.requires('incentive')


def test_assign_stereo_schrodinger():
    if not os.getenv("SCHRODINGER"):
        pytest.skip("SCHRODINGER not set")

    assert cmd.count_atoms("stereo R") == 0

    cmd.load(testing.datafile("1ehz-5.pdb"), "m1")
    cmd.assign_stereo(method="schrodinger")

    assert cmd.count_atoms("stereo R") == 15
    assert cmd.count_atoms("stereo S") == 5


def test_assign_stereo_rdkit():
    try:
        import rdkit
    except ImportError:
        pytest.skip("rdkit not available")

    assert cmd.count_atoms("stereo R") == 0

    cmd.load(testing.datafile("1ehz-5.pdb"), "m1")
    cmd.assign_stereo(method="rdkit")

    assert cmd.count_atoms("stereo R & not elem P") == 15
    assert cmd.count_atoms("stereo S") == 5
