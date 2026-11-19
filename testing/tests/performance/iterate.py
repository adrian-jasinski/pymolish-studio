'''
Stress testing for iterate/alter
'''

from pymol import cmd, testing, stored


def load_big_example_multistate():
    # 4434 atoms in 61 states (270474 atoms)
    cmd.load(testing.datafile('2cas.pdb.gz'))
    cmd.load(testing.datafile('2cas.dcd'))


def testAlterState():
    load_big_example_multistate()

    v_count = cmd.count_atoms() * cmd.count_states()
    assert v_count > 10**5

    xyz = []
    with testing.timing('i', 5.0):
        cmd.iterate_state(0, 'all', 'xyz.append((x,y,z))', space=locals())

    assert v_count == len(xyz)

    with testing.timing('a', 5.0):
        cmd.alter_state(0, 'all', '(x,y,z) = next(xyz_rev)',
                space={'xyz_rev': reversed(xyz), 'next': next})

    cmd.iterate_state(0, 'last all', 'stored.xyz = (x,y,z)')
    assert stored.xyz == xyz[0]
