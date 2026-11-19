'''
PYMOL-317
can't select by atom type
'''

import os
from pymol import cmd, testing, stored

pytestmark = [testing.requires('mmlibs'), testing.requires('incentive'), testing.requires('no_edu')]


def _testLabelByAtomType():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.remove("alt 'B'")
    cmd.label('resn STU', 'text_type')
    c3labels = []
    cmd.iterate("resn STU", "c3labels.append(label == 'C.3')", space=locals())
    assert sum(c3labels) == 8


def testSelectByAtomType():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.remove("alt 'B'")
    cmd.select('foo', "resn STU and text_type 'C.3'")
    assert cmd.count_atoms('foo') == 8

    # discrete object
    cmd.delete('*')
    cmd.load(testing.datafile('ligs3d.sdf'))
    assert cmd.count_discrete('*') > 0
    n = cmd.select('foo', "text_type 'C.3'")
    assert n == 115

    # only run label test if selection tests passed. Don't wnat
    # more than one failing tests for builds with NO_MMLIBS
    cmd.delete('*')
    _testLabelByAtomType()
