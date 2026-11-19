'''
ignore_case_chain
'''

from pymol import cmd, CmdException, testing, stored


def testIgnoreCase():
    # check defaults
    assert cmd.get_setting_int('ignore_case') == 1
    assert cmd.get_setting_int('ignore_case_chain') == 0

    # data
    natoms = 10
    cmd.fragment('ala', 'm1')
    cmd.copy('m2', 'm1')
    cmd.alter('m1', 'chain, segi = "C", "S"')
    cmd.alter('m2', 'chain, segi = "c", "s"')
    cmd.alter('m2', 'resn, name = resn.lower(), name.lower()')

    assert cmd.count_atoms('chain C') == natoms
    assert cmd.count_atoms('segi  S') == natoms
    assert cmd.count_atoms('chain c') == natoms
    assert cmd.count_atoms('segi  s') == natoms
    assert cmd.count_atoms('resn ALA') == natoms * 2
    assert cmd.count_atoms('resn ala') == natoms * 2
    assert cmd.count_atoms('name CA') == 2
    assert cmd.count_atoms('name ca') == 2

    cmd.set('ignore_case_chain')

    assert cmd.count_atoms('chain C') == natoms * 2
    assert cmd.count_atoms('segi  S') == natoms * 2
    assert cmd.count_atoms('chain c') == natoms * 2
    assert cmd.count_atoms('segi  s') == natoms * 2

    cmd.set('ignore_case', 0)

    assert cmd.count_atoms('resn ALA') == natoms
    assert cmd.count_atoms('resn ala') == natoms
    assert cmd.count_atoms('name CA') == 1
    assert cmd.count_atoms('name ca') == 1
