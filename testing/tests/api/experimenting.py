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


@testing.requires('no_edu') # ray
def testFocalblur():
    cmd.viewport(100, 100)
    cmd.fragment('gly', 'm1')
    view = cmd.get_view()
    sharp = testing.get_imagearray()
    with testing.mktemp('.png') as filename:
        cmd.focal_blur(4.0, 3, filename=filename)
        blurred = testing.get_imagearray(filename)
    assert blurred.shape == sharp.shape
    testing.assert_image_not_equal(sharp, blurred)
    assert cmd.get_view() == view
    # default: a temporary file; the result is the image on display
    cmd.focal_blur(4.0, 2)
    testing.assert_image_not_equal(sharp, testing.get_imagearray(prior=1))
