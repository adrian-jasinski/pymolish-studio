
'''
Testing properties for simple getting/setting and loading from sdf and mae files
'''

import pytest
from pymol import cmd, testing


# test loading MAE files with no properties (default)
@testing.requires('incentive')
def testMAEloadNoProperties():
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles')
    objs = cmd.get_object_list()
    for obj in objs:
        props = cmd.get_property('', obj)
        assert props is None


# test loading MAE files with all properties
@testing.requires('incentive')
def testMAEloadAllProperties():
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props='*')
    objs = cmd.get_object_list()
    for obj in objs:
        props = cmd.get_property_list(obj)
        assert props is not None


# test loading MAE files with some properties listed
@testing.requires('incentive')
def testMAEloadSomeProperties():
    props = ['s_knime_origin_file_name', 's_knime_origin_hostname']
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props=' '.join(props))
    objs = cmd.get_object_list()
    for obj in objs:
        allprops = cmd.get_property_list(obj)
        assert len(props) == len(allprops)


# test loading MAE files with some properties listed that do not exist
@testing.requires('incentive')
def testMAEloadSomePropertiesDontExist():
    props = ['s_knime_origin_file_name', 's_knime_origin_hostname', 'dontexist']
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props=' '.join(props))
    objs = cmd.get_object_list()
    for obj in objs:
        allprops = cmd.get_property_list(obj)
        assert allprops is not None


# test loading MAE files with no properties listed
@testing.requires('incentive')
def testMAEloadSomePropertiesEmptyList():
    props = []
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props=' '.join(props))
    objs = cmd.get_object_list()
    for obj in objs:
        allprops = cmd.get_property_list(obj)
        assert allprops is None


@testing.requires('incentive')
def testMAEsaveLoadSessions():
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props='*')
    allpropdata = {}
    objs = cmd.get_object_list()
    for obj in objs:
        props = cmd.get_property_list(obj)
        allpropdata[obj] = {}
        for prop in props:
            allpropdata[obj][prop] = cmd.get_property(prop, obj)
    with testing.mktemp('.pse') as psefilename:
        cmd.save(psefilename)
        cmd.load(psefilename)
    # this is to fail the test on purpose
    #        cmd.set_property('i_m_ct_format', 3, '1d_smiles.mol_13')
    objs = cmd.get_object_list()
    for obj in objs:
        props = cmd.get_property_list(obj)
        # test to make sure there are no extra properties or not enough properties
        assert set(props) == set(allpropdata[obj].keys())
        # test to make sure all property values are the same
        for prop in props:
            try:
                assert allpropdata[obj][prop] == cmd.get_property(prop, obj)
            except:
                pytest.fail('properties are not the same: obj=%s prop=%s' % (obj, prop))


@testing.requires('incentive')
def testMAEchempy():
    cmd.load(testing.datafile('1d_smiles.mae'), '1d_smiles', object_props='*')
    objs = cmd.get_object_list()
    for obj in objs:
        model = cmd.get_model(obj)
        prop_list= cmd.get_property_list(obj)
        mol_prop_list = [x[0] for x in model.molecule_properties]
        assert set(prop_list) == set(mol_prop_list)


def testSimple():
    cmd.fab('A', 'm1')
    cmd.fab('A', 'm2')
    v1 = 'foo'
    v2 = 'bar'
    v3 = 'com'

    # single state
    cmd.set_property('filename', v1, 'm1')
    assert 'foo' == v1
    assert cmd.get_property('filename', 'm1') == v1
    assert cmd.get_property('filename', 'm2') == None

    # multiple objects
    cmd.set_property('filename', v1)
    assert cmd.get_property('filename', 'm2') == v1

    # two states
    cmd.create('m1', 'm1', 1, 2)
    assert cmd.count_states() == 2

    # set for all states
    cmd.set_property('filename', v1, 'm1')
    assert cmd.get_property('filename', 'm1', 2) == v1

    # set for particular state
    cmd.set_property('filename', v2, 'm1', 2)
    assert cmd.get_property('filename', 'm1', 1) == v1
    assert cmd.get_property('filename', 'm1', 2) == v2

    # set for current state
    cmd.frame(2)
    cmd.set_property('filename', v3, 'm1', -1)
    assert cmd.get_property('filename', 'm1', 1) == v1
    assert cmd.get_property('filename', 'm1', 2) == v3


def testSDF():
    # get molecule with SDF annotations
    cid = 6830

    cmd.set('load_object_props_default', '')
    cmd.load('CID_%d.sdf' % cid, 'm1')
    assert None == cmd.get_property('PUBCHEM_COMPOUND_CID', 'm1'), 'property loaded, but should not'
    cmd.delete('*')

    cmd.load('CID_%d.sdf' % cid, 'm1', object_props='*')
    assert cid == cmd.get_property('PUBCHEM_COMPOUND_CID', 'm1')

    v_pc = cmd.get_property('PUBCHEM_MMFF94_PARTIAL_CHARGES', 'm1')
    lines = v_pc.rstrip().splitlines()
    n_pc = int(lines[0])
    assert n_pc == len(lines) - 1

    # test loading selective properties
    cmd.set('load_object_props_default', "PUBCHEM_COMPOUND_CID PUBCHEM_CONFORMER_RMSD PUBCHEM_CONFORMER_DIVERSEORDER")
    cmd.load('CID_%d.sdf' % cid, 'm2')
    assert cid == cmd.get_property('PUBCHEM_COMPOUND_CID', 'm2')
    assert None == cmd.get_property('PUBCHEM_EFFECTIVE_ROTOR_COUNT', 'm2')


def testRemoveAtoms():
    # Removing atoms must not remove object properties PYMOL-3583
    cmd.fragment("ala")
    cmd.set_property("foo", 123, "ala")
    assert cmd.get_property("foo", "ala") == 123
    cmd.remove("hydro")
    assert cmd.get_property("foo", "ala") == 123


def testRemoveAtomsPreserveAtomProperties():
    # Removing atoms must preserve atom properties
    cmd.fab("ACD")
    cmd.alter("all", "p.foo = ID = index")
    # force new sorting
    cmd.alter("resi 2", "resv=4")
    cmd.sort()
    # remove some atoms
    cmd.remove("elem C")
    checklist = []
    cmd.iterate("all", "checklist.append((p.foo == ID))", space=locals())
    assert all(checklist)

# vi:nowrap
