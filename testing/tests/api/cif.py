from pymol import cmd, testing, stored


def testPYMOL1737():
    cmd.load(testing.datafile('ice_IV.cif'))
    assert 'ice_IV' in cmd.get_object_list()


def testPYMOL1533():
    cmd.load(testing.datafile('1v5a-3models.cif'))
    assert cmd.count_states() == 3


def test_models_diff_atom_count():
    cmd.load(testing.datafile('1v5a-2models-1st-trunc.cif'), 'm1')
    assert cmd.count_states() == 2
    assert cmd.count_atoms() == 387
    assert cmd.count_atoms('state 1') == 139


def test_chemical_conn_bond():
    cmd.load(testing.datafile('1519159.cif'), 'm1')
    model = cmd.get_model()
    assert len(model.atom) == 26
    assert len(model.bond) == 35


def test_CCDC():
    cmd.load(testing.datafile('CAFINE.cif'), 'm1')
    assert cmd.count_atoms() == 25
    sym = cmd.get_symmetry('m1')
    assert sym[6] == 'P 21/a'
    testing.assert_array_equal(sym[:6], [14.8, 16.7, 3.97, 90., 97., 90.], delta=1e-4)


def test_components_multiplex():
    cmd.load(testing.datafile('components-000-001-002.cif'))
    for name, natoms, nbonds in [
            ('002', 67, 67),
            ('001', 87, 90),
            ('000', 9, 8),
            ]:
        model = cmd.get_model(name)
        assert len(model.atom) == natoms
        assert len(model.bond) == nbonds
    # for 000, test bond orders
    assert [b.order for b in model.bond] == [1, 2, 1, 1, 1, 1, 1, 1]


def test_assembly():
    cmd.load(testing.datafile('4m4b-minimal-w-assembly.cif'))
    assert cmd.count_states() == 1
    assert cmd.get_chains() == ['A', 'B']

    cmd.delete('*')
    cmd.set('assembly', '1')

    cmd.load(testing.datafile('4m4b-minimal-w-assembly.cif'))
    assert cmd.count_states() == 2
    assert cmd.get_chains() == ['B']
