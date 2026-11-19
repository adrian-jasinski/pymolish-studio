'''
Regression test for PYMOL-757
Certain mouse actions in edit mode cause objects to be ungrouped
'''

from pymol import cmd, testing
from pymol.wizard import Wizard

class MockWizard(Wizard):
    def get_event_mask(self):
        return Wizard.event_mask_dirty
    def do_dirty(self):
        cmd.select('s1', 'none')
        cmd.delete('s1')


@testing.requires('gui')
def testDirtyDelete():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.group('g1', 'm1 m2')
    cmd.set_wizard(MockWizard())

    cmd.draw()

    v = cmd.get_object_list('(g1)')
    assert v == ['m1', 'm2']
