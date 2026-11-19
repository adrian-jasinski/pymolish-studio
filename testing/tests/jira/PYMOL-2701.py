'''
mol2 formal charge assigment (import)
'''

from pymol import cmd, CmdException, testing, stored


def testMol2FormalChargeAssignment():
    cmd.fragment('lys')
    cmd.fragment('lys')

    with testing.mktemp('.mol2') as filename:
        cmd.save(filename, state=0)
        cmd.delete('*')
        cmd.load(filename)

    assert cmd.get_model('name NZ', state=1).atom[0].formal_charge == 1
    assert cmd.get_model('name NZ', state=2).atom[0].formal_charge == 1
