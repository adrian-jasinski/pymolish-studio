import pytest
import pymol
from pymol import cmd, testing, stored


def testGetBondPrint():
    cmd.get_bond_print
    pytest.skip("TODO")


def testSpheroid():
    cmd.fragment('gly', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.spheroid('m1')
    assert 1 == cmd.count_states('m1')


def testCheck():
    cmd.check
    pytest.skip("TODO")


def testDump():
    cmd.dump
    pytest.skip("TODO")


@testing.requires('incentive')
@testing.requires('no_edu') # ray
def testFocalblur():
    cmd.viewport(100, 100)
    cmd.fragment('gly', 'm1')
    cmd.focal_blur(4.0, 3)
