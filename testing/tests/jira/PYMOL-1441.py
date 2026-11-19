'''
vis file support
'''

import pytest
from pymol import cmd, testing, stored

try:
    import h5py
except ImportError:
    h5py = None

pytestmark = [pytest.mark.skipif(not h5py, reason='TODO: h5py required'), testing.requires('incentive')]


def test_map():
    cmd.load(testing.datafile("Structure_potential.vis"))

    assert 1 == len(cmd.get_names_of_type('object:map'))
    assert 2 == len(cmd.get_names_of_type('object:surface'))


def test_surface():
    cmd.load(testing.datafile("surf2.vis"))

    assert 1 == len(cmd.get_names_of_type('object:cgo'))
