'''
Testing: pymol.editing
'''

import pytest
from pymol import cmd, testing, stored
from pymol import CmdException

def get_coord_list(selection, state=1):
    return cmd.get_model(selection, state).get_coord_list()

def get_atom_names(selection='all'):
    return [a.name for a in cmd.get_model(selection).atom]


alter_names_atomic = {
    str: ('segi', 'chain', 'resn', 'resi', 'name', 'alt', 'elem', 'text_type'),
    int: ('formal_charge', 'numeric_type', 'ID'),
    float: ('q', 'b', 'partial_charge', 'vdw'),
}

alter_names_atomic_special = {
    str: ('model', 'type'),
    int: ('resv',),
}

alter_names_state = {
    float: ('x', 'y', 'z'),
}


def testIterate():
    cmd.pseudoatom('m1')

    for ptype, names in (
            list(alter_names_atomic.items()) +
            list(alter_names_atomic_special.items())):
        stored.v_names = None
        cmd.iterate('all', 'stored.v_names = [' + ','.join(names) + ']')

        assert stored.v_names != None
        for v in stored.v_names:
            assert isinstance(v, ptype)


@pytest.mark.parametrize("func", [cmd.iterate, cmd.alter])
def testIterateLocalVars(func):
    cmd.pseudoatom('m1')
    stored.v = None
    func('all', 'foobar = model;stored.v = foobar')
    assert stored.v == 'm1'


def testIterateCallback():
    cmd.fragment('gly')
    atoms = []
    cmd.iterate('not hydro', atoms.append)
    assert [a.name for a in atoms] == ['N', 'CA', 'C', 'O']
    assert [a.protons for a in atoms] == [7, 6, 6, 8]


def testIterateDecorator():
    cmd.fragment('gly')
    atoms = []
    @cmd.iterate('not hydro')
    def real_iterate(at):
        atoms.append(at)
    assert [a.name for a in atoms] == ['N', 'CA', 'C', 'O']
    assert [a.protons for a in atoms] == [7, 6, 6, 8]


def testIterate__explicit_degree():
    cmd.fragment("ala")
    result = []
    cmd.iterate("all", "result.append(explicit_degree)", space=locals())
    assert result == [2, 4, 2, 1, 4, 1, 1, 1, 1, 1]


def testIterate__explicit_valence():
    cmd.fragment("ala")
    result = []
    cmd.iterate("all", "result.append(explicit_valence)", space=locals())
    assert result == [2, 4, 3, 2, 4, 1, 1, 1, 1, 1]


def testIterate__explicit_valence__aromatic():
    cmd.fragment("benzene")
    cmd.valence("aromatic", "elem C", "elem C")
    result = []
    cmd.iterate("all", "result.append(explicit_valence)", space=locals())
    assert result == [4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1]


def testIterateState():
    cmd.fragment('ala')
    cmd.create('ala', 'ala', 1, 2)
    assert 2 == cmd.count_states()

    v_count = cmd.count_atoms('all')
    expr = 'v_xyz.append(((model,index), (x,y,z)))'

    # current state
    v_xyz = []
    cmd.iterate_state(-1, 'all', expr, space=locals())
    assert len(v_xyz) == v_count

    # all states
    v_xyz = []
    cmd.iterate_state(0, 'all', expr, space=locals())
    assert len(v_xyz) == v_count * 2

    # atomic=0
    stored.v_xyz = []
    cmd.iterate_state(1, 'all', 'stored.v_xyz.append((x,y,z))', atomic=0)
    assert len(stored.v_xyz) == v_count

    space = {'pytest': pytest, 'NameError': NameError, 'v_list': []}
    cmd.iterate_state(1, 'all',
            'v_list.append(pytest.raises(NameError, lambda: (model, index)))',
            space=space)
    assert len(space['v_list']) == v_count


def testAlter():
    cmd.pseudoatom('m1')

    for ptype, names in alter_names_atomic.items():
        stored.v_mock = tuple(map(ptype, range(len(names))))
        names_fmt = '(' + ','.join(names) + ',)'

        if not (cmd.alter('all', names_fmt + ' = stored.v_mock') and
                cmd.iterate('all', 'stored.v_names = ' + names_fmt)):
            raise UserWarning('iterate failed')

        assert stored.v_names == stored.v_mock


def testAlterState():
    cmd.fragment('ala')
    cmd.create('ala', 'ala', 1, 2)
    v_count = cmd.count_atoms('all')

    v_mock = [list(map(float, list(range(i*3, (i+1)*3)))) for i in range(v_count)]

    v_xyz_1_pre = cmd.get_model('all', state=1).get_coord_list()
    v_xyz_2_pre = cmd.get_model('all', state=2).get_coord_list()

    cmd.alter_state(2, 'all', '(x,y,z) = next(xyz_iter)',
            space={'xyz_iter': iter(v_mock), 'next': next})

    v_xyz_1_post = cmd.get_model('all', state=1).get_coord_list()
    v_xyz_2_post = cmd.get_model('all', state=2).get_coord_list()

    assert v_xyz_1_post == v_xyz_1_pre
    assert v_xyz_2_post == v_mock


def test_alter_list():
    cmd.fragment('gly')
    cmd.alter_list('gly', [[i+1, 'name = "X%d"' % i] for i in range(7)])
    name_list = []
    cmd.iterate('gly', 'name_list.append(name)', space=locals())
    assert name_list == ['X%d' % i for i in range(7)]


def test_alter_exceptions():
    cmd.fragment('gly')
    with pytest.raises(Exception,
                                match='Use alter/alter_state to modify values'):
        cmd.iterate('all', 'b = "abc"')
    with pytest.raises(ValueError, match='float'):
        cmd.alter('all', 'b = "abc"')
    with pytest.raises(IndexError):
        cmd.iterate('all', 'name[100]')


def test_attach():
    cmd.pseudoatom()
    cmd.edit('first all')
    cmd.attach('C', 1, 1)
    assert 2 == cmd.count_atoms()
    cmd.attach('C', 1, 1)
    assert 3 == cmd.count_atoms()
    assert ['C01', 'C02', 'PS1'] == sorted(get_atom_names())


def test_add_bond():
    cmd.pseudoatom('m1', pos=(0,0,0))
    cmd.pseudoatom('m1', pos=(1,0,0))
    cmd.pseudoatom('m1', pos=(1,1,0))
    cmd.add_bond('m1', 1, 2) # 1-indexed
    cmd.add_bond('m1', 2, 3, order=2)
    bonds = cmd.get_bonds('m1') # 0-indexed
    assert bonds == [(0, 1, 1), (1, 2, 2)]


def test_rebond():
    cmd.pseudoatom('m1', pos=(0, 0, 0), vdw=0.8)
    cmd.pseudoatom('m1', pos=(1, 0, 0), vdw=0.8)
    cmd.pseudoatom('m1', pos=(1, 1, 0), vdw=0.8)
    cmd.add_bond('m1', 1, 3) # this bond will be removed by "rebond"
    cmd.rebond('m1')
    bonds = cmd.get_bonds('m1') # 0-indexed
    assert bonds == [(0, 1, 1), (1, 2, 1)]


def test_bond():
    cmd.pseudoatom('m1', pos=(0,0,0))
    cmd.pseudoatom('m1', pos=(1,0,0))
    cmd.pseudoatom('m1', pos=(1,1,0))

    cmd.bond('m1`1', 'm1`2')
    count = cmd.count_atoms('(m1`1) extend 1')
    assert count == 2

    cmd.unbond('m1`1', 'm1`2')
    count = cmd.count_atoms('(m1`1) extend 1')
    assert count == 1


def test_cycle_valence():
    cmd.fragment('gly')
    cmd.edit('ID 0', 'ID 1')

    cmd.cycle_valence()
    assert 4 == cmd.get_model('pkbond').bond[0].order

    cmd.cycle_valence()
    assert 2 == cmd.get_model('pkbond').bond[0].order

    cmd.cycle_valence()
    assert 3 == cmd.get_model('pkbond').bond[0].order


def test_deprotect():
    # see test_protect
    pass


def test_drag():
    cmd.drag
    pytest.skip("TODO")


def test_dss():
    ss_list = []
    cmd.fab('A' * 6, ss=1)
    cmd.dss()
    cmd.iterate('2-5/CA', 'ss_list.append(ss)', space=locals())
    assert ss_list == ['H', 'H', 'H', 'H']


def test_edit():
    cmd.fragment('gly')
    cmd.edit('ID 0', 'ID 1', 'ID 2','ID 3')
    names = cmd.get_names('public_selections')
    assert names == ['pk1', 'pk2', 'pk3', 'pk4', 'pkset', 'pkmol']


def test_fix_chemistry():

    # Baseline bond order
    cmd.fragment('arg')
    # list(set()) to remove possibly duplicate bond info
    bonds = list(set(cmd.get_bonds('arg')))
    total_order = sum(t[2] for t in bonds)
    assert total_order == 25

    # Change bond orders
    cmd.bond('arg`9', 'arg`11', 2)
    bonds = list(set(cmd.get_bonds('arg')))
    total_order = sum(t[2] for t in bonds)
    assert total_order == 27

    # Restore with fix_chemistry
    cmd.fix_chemistry('arg')
    bonds = list(set(cmd.get_bonds('arg')))
    total_order = sum(t[2] for t in bonds)
    assert total_order == 25


def test_flag():
    cmd.fab("ACE")
    natoms = cmd.count_atoms()
    natoms_cys = cmd.count_atoms('resn CYS')
    assert natoms == 36
    assert natoms_cys == 11
    cmd.alter("all", "flags = 0")
    for flag in range(32):
        sele = "flag {}".format(flag)
        assert cmd.count_atoms(sele) == 0
        cmd.flag(flag, "index 1-{}".format(flag + 1), "set")
        assert cmd.count_atoms(sele) == flag + 1
        cmd.flag(flag, "index {}-{}".format(flag + 1, flag + 2), "reset")
        assert cmd.count_atoms(sele) == 2
        cmd.flag(flag, "index 1-{}".format(flag + 1), "clear")
        assert cmd.count_atoms(sele) == 1
        cmd.flag(flag, "last all", "set")
        assert cmd.count_atoms(sele) == 2
    cmd.alter("all", "flags = 0")
    for flag, flagname in [
        (0, 'focus'),
        (1, 'free'),
        (2, 'restrain'),
        (3, 'fix'),
        (4, 'exclude'),
        (5, 'study'),
        (24, 'exfoliate'),  # deprecated
        (25, 'ignore'),
        (26, 'no_smooth'),
    ]:
        sele = "flag {}".format(flag)
        assert cmd.count_atoms(sele) == 0
        cmd.flag(flagname, 'resn CYS')
        assert cmd.count_atoms(sele) == natoms_cys

    cmd.alter("all", "flags = 1 << 25")
    assert cmd.count_atoms("flag 25") == natoms
    # number as string
    cmd.flag("25", "index 11-15")  # reset
    assert cmd.count_atoms("flag 25") == 5
    # abbreviated action
    cmd.flag("25", "index 15-20", "s")  # set
    assert cmd.count_atoms("flag 25") == 10


def test_flag_error_handling():
    with pytest.raises(CmdException, match="out of range"):
        cmd.flag(-1, "all")
    with pytest.raises(CmdException, match="out of range"):
        cmd.flag(32, "all")
    with pytest.raises(cmd.QuietException, match="unknown action"):
        cmd.flag(1, "all", "foo")
    with pytest.raises(CmdException, match="Invalid selection name"):
        cmd.flag(1, "foo")


# 2.1 for get_bonds
def test_fuse():
    cmd.fragment('ala')
    cmd.fragment('gly')
    # non-hydrogens (N has an open valence, O actually not)
    cmd.fuse("gly and elem N", "ala and elem O")
    assert 17 == cmd.count_atoms('ala')
    # hydrogens
    cmd.fuse("/gly///GLY/3HA", "/ala///ALA/3HB")
    assert 22 == cmd.count_atoms("ala")
    # mode 3: don't create a bond
    cmd.fuse("gly", "ala", mode=3)
    assert 29 == cmd.count_atoms("ala")
    # move=0
    cmd.fuse("/gly///GLY/C", "/ala///GLY/C03", move=0)
    assert 36 == cmd.count_atoms("ala")
    assert cmd.get_bonds("ala") == [
        (0, 1, 1),
        (0, 5, 1),
        (1, 2, 1),
        (1, 4, 1),
        (1, 6, 1),
        (2, 3, 2),
        (3, 9, 1),
        (4, 13, 1),
        (4, 7, 1),
        (4, 8, 1),
        (9, 16, 1),
        (9, 25, 1),
        (10, 13, 1),
        (10, 26, 1),
        (11, 14, 1),
        (11, 27, 1),
        (12, 15, 1),
        (12, 28, 1),
        (13, 18, 1),
        (13, 29, 1),
        (14, 19, 1),
        (14, 30, 1),
        (14, 31, 1),
        (15, 20, 1),
        (15, 32, 1),
        (15, 33, 1),
        (16, 17, 1),
        (16, 34, 1),
        (16, 35, 1),
        (17, 21, 2),
        (18, 20, 1),
        (18, 22, 2),
        (19, 23, 2),
        (20, 24, 2),
    ]
    testing.assert_array_equal(cmd.get_coordset("ala"), [
        [-0.68, -1.23, -0.49],
        [-0.0, 0.06, -0.49],
        [-0.51, 0.86, 0.73],
        [1.5, -0.11, -0.49],
        [2.03, -1.23, -0.5],
        [-1.6, 1.01, 0.69],
        [-0.28, 0.34, 1.68],
        [-0.13, -2.16, -0.49],
        [-0.27, 0.6, -1.42],
        [1.24, -2.38, -0.51],
        [-0.1, -1.95, -0.91],
        [-1.12, -2.31, 0.15],
        [-0.8, -2.9, 1.19],
        [1.42, -2.89, 0.42],
        [-0.35, -2.43, -1.81],
        [-0.11, -0.85, -1.02],
        [1.55, 2.1, 1.1],
        [0.13, 2.26, 0.81],
        [-0.57, 3.06, 1.88],
        [0.04, 3.5, 2.86],
        [2.0, 2.52, 1.99],
        [0.02, 2.8, -0.15],
        [-1.19, 0.2, -0.21],
        [0.23, 0.32, -0.5],
        [1.06, -0.39, 0.54],
        [0.55, -0.97, 1.5],
        [-1.56, -0.33, 0.66],
        [0.48, 1.34, -0.51],
        [0.43, -0.16, -1.48],
        [-1.19, 0.2, -0.21],
        [0.23, 0.32, -0.5],
        [1.06, -0.39, 0.54],
        [0.55, -0.97, 1.5],
        [-1.56, -0.33, 0.66],
        [0.48, 1.34, -0.51],
        [0.43, -0.16, -1.48],
    ], 1e-2)
    names = []
    cmd.iterate("ala", "names.append(name)", space=locals())
    assert names == [
        'N', 'CA', 'C', 'O', 'CB', 'H', 'HA', '1HB', '2HB', 'N', 'N01',
        'N02', 'N03', 'C02', 'C04', 'C06', 'CA', 'C', 'C03', 'C05', 'C07',
        'O', 'O04', 'O06', 'O08', 'H', 'H05', 'H08', 'H11', 'H07', 'H09',
        'H10', 'H12', 'H13', '3HA', 'HA'
    ]


def test_get_editor_scheme():
    cmd.get_editor_scheme
    pytest.skip("TODO")


def test_h_add():
    cmd.fragment('gly')
    cmd.h_add()
    assert 5 == cmd.count_atoms('hydro')


def test_h_add_state():
    nheavy = 4
    nhydro = 5
    nfull = nheavy + nhydro

    cmd.fragment('gly', 'm1')
    cmd.remove('hydro')
    assert nheavy == cmd.count_atoms()
    cmd.h_add()
    assert nfull == cmd.count_atoms()

    # multi-state
    cmd.remove('hydro')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)
    cmd.h_add(state=2)
    assert nfull == cmd.count_atoms()
    assert nheavy == cmd.count_atoms('state 1')
    assert nfull == cmd.count_atoms('state 2')
    assert nheavy == cmd.count_atoms('state 3')

    # discrete multi-state
    cmd.remove('hydro')
    cmd.create('m2', 'm1', 1, 1, discrete=1)
    cmd.create('m2', 'm2', 1, 2, discrete=1)
    cmd.create('m2', 'm2', 1, 3, discrete=1)
    assert nheavy * 3 == cmd.count_atoms('m2')
    cmd.h_add('m2 & state 2') # TODO , state=2)
    assert nfull + nheavy * 2 == cmd.count_atoms('m2')
    assert nheavy == cmd.count_atoms('m2 & state 1')
    assert nfull == cmd.count_atoms('m2 & state 2')
    assert nheavy == cmd.count_atoms('m2 & state 3')
    cmd.h_add('m2')
    assert nfull * 3 == cmd.count_atoms('m2')


def test_h_fill():
    cmd.fragment('gly')
    cmd.edit('elem N')
    cmd.h_fill()
    assert 4 == cmd.count_atoms('hydro')


def test_h_fix():
    cmd.h_fix
    pytest.skip("TODO")


def test_invert():
    cmd.fragment('ala')
    xyzfix = get_coord_list('ID 1-7')
    xyzmov = get_coord_list('ID 0+8+9')
    cmd.edit('ID 1', 'ID 2', 'ID 3')
    cmd.invert()
    assert xyzfix == get_coord_list('ID 1-7')
    assert xyzmov != get_coord_list('ID 0+8+9')


def test_map_double():
    cmd.map_double
    pytest.skip("TODO")


def test_map_halve():
    cmd.map_halve
    pytest.skip("TODO")


def test_map_set():
    cmd.map_set
    pytest.skip("TODO")


def test_map_set_border():
    cmd.map_set_border
    pytest.skip("TODO")


def test_map_trim():
    cmd.map_trim
    pytest.skip("TODO")


def test_matrix_copy():
    cmd.fragment('ala')
    cmd.fragment('gly')
    cmd.rotate('x', 90, 'none', object='ala')
    cmd.matrix_copy('ala', 'gly')
    testing.assert_array_equal(cmd.get_object_matrix('gly'),
            (1.0, 0.0, 0.0, 0.0,
             0.0, 0.0,-1.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 1.0), 1e-4)
    cmd.matrix_reset('gly', mode=1)
    testing.assert_array_equal(cmd.get_object_matrix('gly'),
            (1.0, 0.0, 0.0, 0.0,
             0.0, 1.0, 0.0, 0.0,
             0.0, 0.0, 1.0, 0.0,
             0.0, 0.0, 0.0, 1.0), 1e-4)


def test_matrix_copy_multi_target():
    """matrix_copy with wildcard target must produce non-singular
        state matrices for every target (regression test for pointer
        aliasing bug when iterating over multiple targets)"""
    import math
    import numpy

    # Source with a non-trivial state matrix (90deg X rotation)
    cmd.fragment('ala', 'src')
    cmd.transform_object('src', [
        1, 0, 0, 0,
        0, 0,-1, 0,
        0, 1, 0, 0,
        0, 0, 0, 1], homogenous=1)

    # Targets with different non-trivial state matrices.
    # transform_object records in cs->Matrix (unlike cmd.rotate
    # which only modifies coordinates without setting the state matrix).
    matrices = {
        'tgt_a': [0,0,1,0, 0,1,0,0, -1,0,0,0, 0,0,0,1],
        'tgt_b': [0,1,0,0, 1,0,0,0, 0,0,-1,0, 0,0,0,1],
    }
    c, s = math.cos(math.radians(120)), math.sin(math.radians(120))
    matrices['tgt_c'] = [c,-s,0,0, s,c,0,0, 0,0,1,0, 0,0,0,1]

    for name, mat in matrices.items():
        cmd.fragment('ala', name)
        cmd.transform_object(name, mat, homogenous=1)

    # matrix_copy with wildcard - hits all three targets in one call
    cmd.matrix_copy('src', 'tgt_*')

    # Every target's state matrix must be non-singular (det ≈ ±1)
    for name in matrices:
        m = cmd.get_object_matrix(name, 1)
        rot = numpy.array(m[:12]).reshape(3, 4)[:, :3]
        det = numpy.linalg.det(rot)
        svd = numpy.linalg.svd(rot, compute_uv=False)
        assert abs(det) == pytest.approx(1.0, abs=5e-5), f'{name}: state matrix singular (det={det})'
        assert svd[-1] > 0.5, f'{name}: collapsed dimension (svd_min={svd[-1]})'


def test_matrix_reset():
    # see test_matrix_copy
    pass


def test_protect():
    cmd.pseudoatom('m1', pos=[0.,0.,0.])
    cmd.pseudoatom('m1', pos=[1.,0.,0.])

    cmd.protect('m1`1')
    cmd.translate([0.,1.,0.])
    assert [0.,0.,0.] == cmd.get_atom_coords('m1`1')
    assert [1.,1.,0.] == cmd.get_atom_coords('m1`2')

    cmd.deprotect()
    cmd.translate([0.,0.,1.])
    assert [0.,0.,1.] == cmd.get_atom_coords('m1`1')
    assert [1.,1.,1.] == cmd.get_atom_coords('m1`2')


def test_push_undo():
    cmd.push_undo
    pytest.skip("TODO")


def test_redo():
    cmd.redo
    pytest.skip("TODO")


def test_reference():
    # undocumented
    cmd.reference
    pytest.skip("TODO")


def test_remove():
    cmd.fragment('ala')
    cmd.remove('elem C')
    assert 7 == cmd.count_atoms()


@pytest.mark.parametrize("hydro,count", [(0, 7), (1, 3)])
def test_remove_picked(hydro, count):
    cmd.fragment('ala')
    cmd.edit('ID 1', 'ID 2', 'ID 3')
    cmd.remove_picked(hydro)
    assert count == cmd.count_atoms()


def test_rename():
    cmd.fragment('ala')
    n_atoms = cmd.count_atoms()
    v = cmd.alter('elem C', 'name="C"')
    assert v == 3
    assert ['C', 'C', 'C'] == get_atom_names('elem C')
    cmd.rename('ala')
    assert ['C', 'C01', 'C02'] == sorted(get_atom_names('elem C'))
    cmd.alter('index 1-3', 'name="X"')
    cmd.alter('index 4', 'name="Y"')
    assert 3 == cmd.count_atoms('name X')
    assert 1 == cmd.count_atoms('name Y')
    cmd.rename('ala', force=1)
    atom_names = get_atom_names()
    assert 'X' not in atom_names
    assert 'Y' not in atom_names
    assert n_atoms == len(set(atom_names))


def test_replace():
    # NOTES:
    # - doc says "Immature functionality"
    # - will not preserve ID
    # - will not re-add hydrogens with h_fill=1
    cmd.fragment('ala')
    cmd.edit('elem O')
    cmd.replace('S', 0, 0, 0)
    assert 0 == cmd.count_atoms('elem O')
    assert 1 == cmd.count_atoms('elem S')
    assert 1 == cmd.count_atoms('name S01')
    assert 0 == cmd.count_atoms('name S02')
    cmd.edit('elem N')
    cmd.replace('S', 0, 0, 0)
    assert 2 == cmd.count_atoms('elem S')
    assert 1 == cmd.count_atoms('name S02')


def test_rotate():
    from chempy import cpv
    from math import pi

    get_coord_list = lambda s: cmd.get_model(s).get_coord_list()

    cmd.fragment('ala')
    cmd.select('s1', 'hydro')

    c1_hydro = get_coord_list('s1')
    c1_other = get_coord_list('not s1')
    c1_hydro_rot = cpv.transform_array(
            cpv.rotation_matrix(pi * 0.25, [0,0,1]), c1_hydro)

    cmd.rotate('z', 45, 's1', camera=0, origin=(0,0,0))

    c2_hydro = get_coord_list('s1')
    c2_other = get_coord_list('not s1')

    testing.assert_array_equal(c2_other, c1_other)
    testing.assert_array_equal(c2_hydro, c1_hydro_rot, 0.001)


def test_sculpt_activate():
    cmd.sculpt_activate
    pytest.skip("TODO")


def test_sculpt_deactivate():
    cmd.sculpt_deactivate
    pytest.skip("TODO")


def test_sculpt_iterate():
    cmd.fab('AFG', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    n_ca = ('m1 & resi 2 & name N', 'm1 & resi 2 & name CA')
    d0 = cmd.get_distance(*n_ca, state=1)
    # match_state: the minimum distances come from state 2
    cmd.sculpt_activate('m1', state=1, match_state=2)
    cmd.translate([0.6, 0.0, 0.0], n_ca[1], state=1, camera=0)
    assert abs(cmd.get_distance(*n_ca, state=1) - d0) > 0.1
    cmd.sculpt_iterate('m1', state=1, cycles=100)
    assert cmd.get_distance(*n_ca, state=1) == pytest.approx(d0, abs=0.05)
    cmd.sculpt_deactivate('m1')


def test_sculpt_purge():
    cmd.sculpt_purge
    pytest.skip("TODO")


def test_set_dihedral():
    cmd.fragment('ala')
    angle = 45.0
    atoms = ('ID 7', 'ID 2', 'ID 1', 'ID 9')
    cmd.set_dihedral(*atoms, angle=angle)
    v = cmd.get_dihedral(*atoms)
    assert v == pytest.approx(angle, abs=5e-5)


def test_set_geometry():
    cmd.set_geometry
    pytest.skip("TODO")


def test_set_name():
    cmd.pseudoatom('m1')
    cmd.set_name('m1', 'm2')
    assert ['m2'] == cmd.get_names()


def test_set_object_color():
    pytest.skip("TODO")

    cmd.fragment('gly')
    cmd.set_object_color('gly', 'blue')
    assert 'blue' == cmd.get('color', 'gly')


def test_set_object_ttt():
    M = [1.0, 0.0, 0.0, 0.0,
         0.0, 0.0,-1.0, 0.0,
         0.0, 1.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 1.0]
    cmd.pseudoatom('m1')
    cmd.set_object_ttt('m1', M)
    testing.assert_array_equal(M, cmd.get_object_matrix('m1'), 1e-4)


def test_set_symmetry():
    sym = [68.7, 126.8, 184.0, 90.0, 90.0, 90.0, 'P 21 21 21']
    cmd.pseudoatom('m1')
    cmd.set_symmetry('m1', *sym)
    v = cmd.get_symmetry('m1')
    assert v[-1] == sym[-1]
    testing.assert_array_equal(v[:-1], sym[:-1], 1e-4)

    cmd.pseudoatom('m2')
    cmd.symmetry_copy('m1', 'm2')
    v = cmd.get_symmetry('m2')
    assert v[-1] == sym[-1]
    testing.assert_array_equal(v[:-1], sym[:-1], 1e-4)


def test_set_symmetry__state():
    sym1 = [68.7, 126.8, 184.0, 90.0, 90.0, 90.0, 'P 21 21 21']
    sym2 = [12, 34, 56, 90.0, 90.0, 90.0, 'P 1']
    cmd.pseudoatom('m1')
    cmd.create('m1', 'm1', 1, 2)
    assert cmd.count_states('m1') == 2
    cmd.set_symmetry('m1', *sym1, state=1)
    cmd.set_symmetry('m1', *sym2, state=2)
    for globalstate, state, sym in [
        (2, 1, sym1),
        (1, 2, sym2),
        (1, -1, sym1),  # current state
        (2, -1, sym2),  # current state
    ]:
        cmd.frame(globalstate)
        v = cmd.get_symmetry('m1', state=state)
        assert v[-1] == sym[-1]
        testing.assert_array_equal(v[:-1], sym[:-1], 1e-4)

    cmd.pseudoatom('m2', state=1)
    cmd.create('m2', 'm2', 1, 2)
    assert cmd.count_states('m2') == 2
    cmd.symmetry_copy('m1', 'm2', 1, 2)
    cmd.symmetry_copy('m1', 'm2', 2, 1)
    assert cmd.get_symmetry('m2', 1)[-1] == sym2[-1]
    assert cmd.get_symmetry('m2', 2)[-1] == sym1[-1]

    # rendering
    testing.ambient_only()
    cmd.disable('m2')
    cmd.color('blue', 'm1')
    cmd.set('cgo_line_width', 10)
    cmd.show_as('cell', 'm1')
    cmd.frame(1)
    cmd.set_view ((
        0.864273727,    0.052246489,   -0.500302136,
        0.200916424,    0.875955939,    0.438560009,
        0.461155534,   -0.479554355,    0.746567726,
        0.000069976,    0.000004172, -809.162963867,
        71.266143799,   17.057806015,   37.736812592,
        560.533935547, 1097.791748047,  -20.0))
    img1 = testing.get_imagearray(width=100, height=100)
    testing.assert_image_has_color('blue', img1)
    cmd.frame(2)
    img2 = testing.get_imagearray(width=100, height=100)
    testing.assert_image_has_color('blue', img2)
    testing.assert_image_not_equal(img1, img2)


def test_set_state_order():
    import numpy

    cmd.fragment('ala', 'm1')
    for i in (2, 3):
        cmd.create('m1', 'm1', i - 1, i);
        cmd.rotate('x', 10.0, 'm1', i)

    coords1 = cmd.get_coordset('m1', 1)
    coords3 = cmd.get_coordset('m1', 3)

    assert coords1.shape == (10, 3)
    assert not numpy.allclose(coords1, coords3)

    cmd.set_state_order('m1', (3, 2, 1))

    assert numpy.allclose(coords1, cmd.get_coordset('m1', 3))
    assert numpy.allclose(coords3, cmd.get_coordset('m1', 1))


def test_set_title():
    text = 'foo'
    cmd.pseudoatom('m1')
    cmd.set_title('m1', 1, text)
    assert cmd.get_title('m1', 1) == text


def test_set_title_current_state():
    cmd.pseudoatom('m1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)
    cmd.create('m1', 'm1', 1, 4)
    # global state
    cmd.frame(2)
    cmd.set_title('m1', -1, "foo")
    assert cmd.get_title('m1', -1) == "foo" # current state
    assert cmd.get_title('m1', -2) == "foo" # effective state (same as current)
    assert cmd.get_title('m1', 1) == ""
    assert cmd.get_title('m1', 2) == "foo"
    assert cmd.get_title('m1', 3) == ""
    assert cmd.get_title('m1', 4) == ""
    # object state
    cmd.set('state', 3, 'm1')
    cmd.set_title('m1', -1, "bar")
    assert cmd.get_title('m1', -1) == "bar" # current state
    assert cmd.get_title('m1', -2) == "bar" # effective state (same as current)
    assert cmd.get_title('m1', 1) == ""
    assert cmd.get_title('m1', 2) == "foo"
    assert cmd.get_title('m1', 3) == "bar"
    assert cmd.get_title('m1', 4) == ""


def test_smooth():
    pdbfile = testing.datafile("sampletrajectory.pdb")
    dcdfile = testing.datafile("sampletrajectory.dcd")

    cmd.load(pdbfile)
    cmd.load_traj(dcdfile, state=0)

    cmd.select('ref_atom','/sampletrajectory///LYS`244/NZ')

    pre_1_xyz = []
    pre_5_xyz = []
    post_1_xyz = []
    post_5_xyz = []

    cmd.iterate_state(1, 'ref_atom', 'pre_1_xyz.append([x,y,z])', space=locals(), atomic=0)
    cmd.iterate_state(5, 'ref_atom', 'pre_5_xyz.append([x,y,z])', space=locals(), atomic=0)

    cmd.smooth('sampletrajectory',10,10)

    cmd.iterate_state(1, 'ref_atom', 'post_1_xyz.append([x,y,z])', space=locals(), atomic=0)
    cmd.iterate_state(5, 'ref_atom', 'post_5_xyz.append([x,y,z])', space=locals(), atomic=0)

    testing.assert_array_equal(pre_1_xyz[0], post_1_xyz[0], delta=0.01)
    testing.assert_array_not_equal(pre_5_xyz[0], post_5_xyz[0], delta=0.01)

    ref_values_5 = [43.79, 50.05, 14.93]
    testing.assert_array_equal(ref_values_5, post_5_xyz[0], delta=0.01)

    assert cmd.count_states('sampletrajectory') == 11


def test_sort():
    cmd.pseudoatom('m1', name='PS2')
    cmd.pseudoatom('m1', name='PS1')
    cmd.alter('all', 'name = name_list.pop()', space={'name_list': ['PS1', 'PS2']})
    v = [a.name for a in cmd.get_model().atom]
    assert ['PS2', 'PS1'] == v
    cmd.sort()
    v = [a.name for a in cmd.get_model().atom]
    assert ['PS1', 'PS2'] == v


def test_split_states():
    cmd.fragment('ala', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)
    cmd.split_states('m1', 1, 2)
    assert sorted(['m1', 'm1_0001', 'm1_0002']) == sorted(cmd.get_names())


def test_symmetry_copy():
    # see test_set_symmetry
    pass


def test_torsion():
    cmd.fragment('ala')
    delta = 10
    atoms = ('ID 7', 'ID 2', 'ID 1', 'ID 9')
    d1 = cmd.get_dihedral(*atoms)
    cmd.edit(*atoms[1:3])
    cmd.torsion(delta)
    d2 = cmd.get_dihedral(*atoms)
    assert d1 + delta == pytest.approx(d2, abs=5e-5)


def test_transform_object():
    cmd.transform_object
    pytest.skip("TODO")


def test_transform_selection():
    cmd.transform_selection
    pytest.skip("TODO")


def test_translate():
    # see test_protect
    pass


def test_translate_atom():
    cmd.translate_atom
    pytest.skip("TODO")


def test_unbond():
    # see test_bond
    pass


def test_unpick():
    cmd.pseudoatom('m1')
    cmd.edit('m1')
    cmd.unpick()
    assert 'pk1' not in cmd.get_names('selections')


def test_update():
    # 3 states
    cmd.fragment('gly', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)

    # second object, 90 degree rotates
    cmd.copy('m2', 'm1')
    cmd.rotate('x', 90, '(m2)', state=0)

    # reference coordsets
    cs = cmd.get_coordset
    cs1 = cs('m1', 1)
    cs2 = cs('m2', 1)

    # m2/3 will change (pre-check)
    testing.assert_array_equal(cs2, cs('m2', 3))
    testing.assert_array_not_equal(cs1, cs('m2', 3))

    # update explicit state
    cmd.update('m2', 'm1', 3, 2)

    # m2/3 has changed
    testing.assert_array_equal(cs1, cs('m2', 3))
    testing.assert_array_not_equal(cs2, cs('m2', 3))

    # these haven't changed
    testing.assert_array_equal(cs2, cs('m2', 1))
    testing.assert_array_equal(cs2, cs('m2', 2))

    # reset m2/3
    cmd.load_coordset(cs2, 'm2', 3)
    testing.assert_array_equal(cs2, cs('m2', 3))

    # update all states
    cmd.update('m2', 'm1', 0, 0)
    testing.assert_array_equal(cs1, cs('m2', 1))
    testing.assert_array_equal(cs1, cs('m2', 2))
    testing.assert_array_equal(cs1, cs('m2', 3))


def test_valence():
    cmd.fragment('gly')
    cmd.valence(2, 'ID 0', 'ID 1')
    assert 2 == cmd.get_model('ID 0+1').bond[0].order


def test_vdw_fit():
    cmd.vdw_fit
    pytest.skip("TODO")


def test_set_discrete():
    import pymol

    cmd.fragment('ala', 'm1')
    cmd.create('m1', 'm1', 1, 2)

    assert 0 == cmd.count_discrete('*')
    assert 2 == cmd.count_states()
    assert 10 == cmd.count_atoms()

    pymol.editing.set_discrete('m1', 1)

    assert 1 == cmd.count_discrete('*')
    assert 2 == cmd.count_states()
    assert 20 == cmd.count_atoms()

    pymol.editing.set_discrete('m1', 0)

    assert 0 == cmd.count_discrete('*')
    assert 2 == cmd.count_states()
    assert 10 == cmd.count_atoms()
