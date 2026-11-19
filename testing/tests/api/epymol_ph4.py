import os
import sys
from pymol import cmd, testing, stored

pytestmark = testing.requires('incentive')


def test_load_hypothesis_xyz():
    from epymol import ph4
    ph4.load_hypothesis_xyz(
            testing.datafile('phase/hypothesis.xyz'),
            ref=testing.datafile('phase/ALL.xyz'))
    extent = cmd.get_extent('hypothesis')
    testing.assert_array_equal(extent,
            [[-4.218, -2.742, -3.702], [10.536, 6.152, 3.536]],
            delta=1e-2)


def test_load_hypothesis_xvol():
    from epymol import ph4
    ph4.load_hypothesis_xvol(
            testing.datafile('phase/1M7Q_hypo.xvol'))
    extent = cmd.get_extent('1M7Q_hypo')
    testing.assert_array_equal(extent,
            [[33.622, 23.055, 23.741], [54.344, 38.530, 37.948]],
            delta=1e-2)


def test_load_hypothesis_phypo():
    from epymol import ph4
    ph4.load_phypo(
            testing.datafile('phase/ADHHRR_1_trans.phypo'),
            'g1', zoom=-1, mimic=1, atom_props='', _self=cmd)
    assert cmd.count_atoms('g1.ADHHRR_1 and name A2+H6') == 2
    assert cmd.count_atoms('g1.endo-1') == 35
    assert cmd.count_atoms('g1.endo-2') == 37
    assert cmd.count_atoms('g1.endo-36') == 28
    assert cmd.count_atoms('g1.ADHHRR_1_xvol') == 936
    assert 'g1.ADHHRR_1_cgo' in cmd.get_names_of_type('object:cgo')
