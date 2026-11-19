'''
PYMOL-317
can't select by atom type
'''

import pytest
import os
from pymol import cmd, testing, stored

pytestmark = [testing.requires('incentive'), testing.requires('no_edu')]


def testAtomStateLevelSettingsOnRemove():
    if cmd.get_setting_int('suspend_undo'):
        pytest.skip("need suspend_undo=0")

    cmd.load(testing.datafile("1molecule.mae"))
    cmd.load(testing.datafile("1molecule.mae"))
    cmd.label("index 10", "'Test Label'")
    plv = [ 5., 0., 0.]
    cmd.alter_state(1, "index 10", "s.label_placement_offset = %s" % plv)
    cmd.remove("index 10")
    cmd.undo()
    stored.offset = None
    cmd.iterate_state(1, "index 10", "stored.offset = list(s.label_placement_offset)")
    assert stored.offset == plv


def testAtomLevelSettingsOnRemove():
    if cmd.get_setting_int('suspend_undo'):
        pytest.skip("need suspend_undo=0")

    cmd.load(testing.datafile("1molecule.mae"))
    cmd.load(testing.datafile("1molecule.mae"))
    cmd.label("index 10", "'Test Label'")
    plv = [ 5., 0., 0.]
    cmd.alter("index 10", "s.label_placement_offset = %s" % plv)
    cmd.remove("index 10")
    cmd.undo()
    stored.offset = None
    cmd.iterate_state(1, "index 10", "stored.offset = list(s.label_placement_offset)")
    assert stored.offset == plv


def testAtomLevelSettingsOnRemove2():
    if cmd.get_setting_int('suspend_undo'):
        pytest.skip("need suspend_undo=0")

    cmd.load(testing.datafile("1molecule.mae"))
    cmd.load(testing.datafile("1molecule.mae"))
    cmd.label("index 10", "'Test Label'")
    plv = [ 5., 0., 0.]
    cmd.alter("index 10", "s.label_placement_offset = %s" % plv)
    cmd.remove("index 10")
    cmd.undo()
    stored.offset = None
    cmd.iterate("index 10", "stored.offset = list(s.label_placement_offset)")
    assert stored.offset == plv
