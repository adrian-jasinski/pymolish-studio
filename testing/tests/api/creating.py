'''
Testing: pymol.creating
'''

import pytest
import pymol
from pymol import cmd, testing, stored



def testGroup():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    m_list = []
    cmd.group('g1', 'm1 m2')
    cmd.iterate('g1', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m1', 'm2'])
    m_list = []
    cmd.ungroup('m2')
    cmd.iterate('g1', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m1'])


def testUngroup():
    # see testGroup
    pass


def testNestedGroup():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    cmd.group('g1', 'm1 m2')
    cmd.group('g2', 'g1 m3')
    m_list = []
    cmd.iterate('g2', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m3', 'm2', 'm1'])


def testNestedGroupRaise():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    cmd.group('g1', 'm1 m2')
    cmd.group('g2', 'g1 m3')
    m_list = []
    cmd.iterate('g2', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m1', 'm2', 'm3'])

    cmd.group('g1', action='raise')
    m_list = []
    cmd.iterate('g2', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m3'])
    m_list = []
    cmd.iterate('g1', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['m1', 'm2'])


def testGroupRename():
    '''
        Rename group entries which have a group name prefix when renaming the group
        '''
    cmd.set('group_auto_mode', 2)
    cmd.pseudoatom('g1.m1')
    cmd.pseudoatom('g1.m2')
    cmd.set_name('g1', 'g2')
    m_list = []
    cmd.iterate('g2', 'm_list.append(model)', space=locals())
    assert sorted(m_list) == sorted(['g2.m1', 'g2.m2'])


def testIsomesh():
    cmd.viewport(100, 100)

    cmd.fragment('gly', 'm1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make mesh
    cmd.isomesh('mesh', 'map')
    cmd.isomesh('mesh', 'map', source_state=1, state=-2)

    ## check mesh presence by color
    meshcolor = 'red'
    cmd.color(meshcolor, 'mesh')
    testing.ambient_only()
    testing.assert_image_has_color(meshcolor)
    cmd.frame(2)
    assert cmd.get_state() == 2
    testing.assert_image_has_color(meshcolor)

    with testing.mktemp('.pse') as filename:
        cmd.save(filename)

        cmd.delete('*')
        testing.assert_image_has_not_color(meshcolor)

        cmd.load(filename)
        testing.assert_image_has_color(meshcolor)
        cmd.frame(2)
        assert cmd.get_state() == 2
        testing.assert_image_has_color(meshcolor)


def testIsosurface():
    cmd.viewport(100, 100)

    cmd.fragment('gly', 'm1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make mesh
    cmd.isosurface('surface', 'map')
    cmd.isosurface('surface', 'map', source_state=1, state=-2)

    ## check mesh presence by color
    meshcolor = 'red'
    cmd.color(meshcolor, 'surface')
    testing.ambient_only()
    testing.assert_image_has_color(meshcolor)
    cmd.frame(2)
    assert cmd.get_state() == 2
    testing.assert_image_has_color(meshcolor)

    with testing.mktemp('.pse') as filename:
        cmd.save(filename)

        cmd.delete('*')
        testing.assert_image_has_not_color(meshcolor)

        cmd.load(filename)
        testing.assert_image_has_color(meshcolor)
        cmd.frame(2)
        assert cmd.get_state() == 2
        testing.assert_image_has_color(meshcolor)


def testIsosurfaceCarve():
    testing.ambient_only()

    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_radius', 0.1)
    cmd.set('dot_radius', 0.2)

    cmd.fragment('gly', 'm1')
    cmd.map_new('map')

    cmd.color('white')
    cmd.color('red', 'elem O')
    cmd.color('blue', 'elem N')
    cmd.ramp_new('m1prox', 'm1', [0, 3], 'object')
    cmd.orient()

    cmd.disable('*')

    for func in [
            cmd.isosurface,
            cmd.isomesh,
            cmd.isodot,
    ]:
        cmd.delete('surface')
        func('surface', 'map', 1.0, 'elem N', carve=1.5)
        cmd.color('m1prox', 'surface')

        img = testing.get_imagearray(width=100, height=100)
        testing.assert_image_has_color("blue", img)
        testing.assert_image_has_not_color("red", img)


def testIsodot():
    cmd.viewport(100, 100)

    cmd.fragment('gly', 'm1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make mesh
    cmd.isodot('dot', 'map')
    cmd.isodot('dot', 'map', source_state=1, state=-2)

    ## check mesh presence by color
    meshcolor = 'red'
    cmd.color(meshcolor, 'dot')
    testing.ambient_only()
    testing.assert_image_has_color(meshcolor)
    cmd.frame(2)
    assert cmd.get_state() == 2
    testing.assert_image_has_color(meshcolor)

    with testing.mktemp('.pse') as filename:
        cmd.save(filename)

        cmd.delete('*')
        testing.assert_image_has_not_color(meshcolor)

        cmd.load(filename)
        testing.assert_image_has_color(meshcolor)
        cmd.frame(2)
        assert cmd.get_state() == 2
        testing.assert_image_has_color(meshcolor)


def testIsolevel():
    cmd.viewport(100, 100)

    cmd.fragment('gly', 'm1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make mesh
    cmd.isodot('dot', 'map')
    cmd.isodot('dot', 'map', source_state=1, state=-2)

    ## check mesh presence by color
    meshcolor = 'red'
    cmd.color(meshcolor, 'dot')
    testing.ambient_only()
    testing.assert_image_has_color(meshcolor)
    cmd.frame(2)
    assert cmd.get_state() == 2
    testing.assert_image_has_color(meshcolor)

    for contourlvl in range(7):
        cmd.isolevel('dot', contourlvl)
        testing.assert_image_has_color(meshcolor)

    cmd.isolevel('dot', 10)
    testing.assert_image_has_not_color(meshcolor)


def testGradient():
    cmd.viewport(100,100)

    cmd.fragment('gly','m1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set("mesh_width", 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make gradient
    cmd.gradient('grad', 'map')
    cmd.gradient('grad', 'map', source_state=1, state=-2)
    
    gradcolor = 'blue'
    cmd.color(gradcolor,'grad')
    testing.ambient_only()
    testing.assert_image_has_color(gradcolor)
    cmd.frame(2)
    assert cmd.get_state() == 2
    testing.assert_image_has_color(gradcolor)

    with testing.mktemp('.pse') as filename:
        cmd.save(filename)

        cmd.delete('*')
        testing.assert_image_has_not_color(gradcolor)

        cmd.load(filename)
        testing.assert_image_has_color(gradcolor)
        cmd.frame(2)
        assert cmd.get_state() == 2
        testing.assert_image_has_color(gradcolor)


def testCopy():
    cmd.fragment('ala', 'm1')
    cmd.copy('m2', 'm1')
    assert cmd.count_atoms('m1') == cmd.count_atoms('m2')


def testCopy_molecule_settings():
    cmd.pseudoatom("m1")
    cmd.pseudoatom("m2")
    assert cmd.get("surface_color", "m1") == "default"
    assert cmd.get("surface_color", "m2") == "default"

    cmd.set("surface_color", "blue", "m1")
    assert cmd.get("surface_color", "m1") == "blue"
    assert cmd.get("surface_color", "m2") == "default"

    cmd.copy("m3", "m1")
    cmd.copy("m4", "m2")
    assert cmd.get("surface_color", "m3") == "blue"
    assert cmd.get("surface_color", "m4") == "default"


def testCopyMap():
    cmd.load(testing.datafile('emd_1155.ccp4'), 'map1')
    cmd.copy('map2', 'map1')
    assert cmd.get_symmetry('map1') == cmd.get_symmetry('map2')
    testing.assert_array_equal(cmd.get_volume_field('map1'), cmd.get_volume_field('map2'))


@pytest.mark.parametrize("matrix_mode,segi", [(0, 0), (1, 1)])
def testSymexp(matrix_mode, segi):
    cmd.set("matrix_mode", matrix_mode)
    cmd.load(testing.datafile('1oky.pdb.gz'), 'm1')
    n = cmd.count_atoms()
    cmd.symexp('s', 'm1', '%m1 & resi 283', 20.0, segi=segi)
    x = cmd.get_object_list()
    assert x == [
        'm1',
        's01000000',
        's03000000',
        's04000000',
        ]
    assert n * 4 == cmd.count_atoms()
    testing.assert_array_equal(
        cmd.get_extent(),
        [[40.8978, -8.901, -47.0803], [162.085, 108.416, 31.309]],
        delta=1e-2)
    segis = dict((name, set()) for name in x)
    cmd.iterate("all", "segis[model].add(segi)", space=locals())
    assert segis["s01000000"] == set(["B000" if segi else ""])
    assert segis["s03000000"] == set(["D000" if segi else ""])
    assert segis["s04000000"] == set(["E000" if segi else ""])


def testSymexpPlaceholderUnitCell():
    cmd.pseudoatom('m1')
    cmd.set_symmetry('m1', 1, 1, 1, 90, 90, 90, 'P 1')

    cmd.symexp('s', 'm1', 'm1', 5)

    assert cmd.get_object_list() == ['m1']


def testFragment():
    frag_name = "ala"
    cmd.fragment(frag_name)
    assert cmd.count_atoms(frag_name) == 10


def testCreate():
    cmd.fragment("ala")
    cmd.create("foo", "ala", 1, 1)

    names = cmd.get_names()
    names.sort()

    assert names == ["ala", "foo"]
    
    # TODO: Create a function to compare to chempy models
    # m1 = cmd.get_model("foo")
    # m2 = cmd.get_model("ala")
    # self.assertChempyModelEquals(m1, m2)

    assert cmd.fit("ala", "foo") == 0.0

    assert cmd.count_states() == 1


def testCreateMultipleStates():
    cmd.fragment("ala")

    # simple creation

    assert cmd.count_states() == 1

    cmd.create("foo", "ala", 1, 1)

    assert cmd.count_states() == 1

    # creation into state 1

    cmd.create("foo", "ala", 1, 1)

    assert cmd.count_states() == 1

    # creation into state 2

    cmd.create("foo", "ala", 1, 2)

    assert cmd.count_states() == 2
    


def create_many_states(fragment, obj, count):
    cmd.fragment(fragment, obj)
    for x in range(2, count + 1):
        cmd.create(obj, obj, 1, x)


def testCreateMany():

    # 10 states
    create_many_states("thr", "foo", 10)

    assert cmd.count_states("foo") == 10
    assert cmd.count_states() == 10

    # 100 states
    create_many_states("trp", "bar", 100)

    assert cmd.count_states("foo") == 10
    assert cmd.count_states("bar") == 100
    assert cmd.count_states() == 100

    # 1000 states
    
    create_many_states("ile", "bam", 1000)

    assert cmd.count_states() == 1000
    


def testCreateTargetState():
    create_many_states("gly", "m1", 4)
    cmd.frame(3)

    cmd.create('m2', 'm1', 0, 0)
    assert cmd.count_states('m2') == 4
    cmd.delete('m2')

    cmd.create('m2', 'm1', 1, 0)
    assert cmd.count_states('m2') == 1
    cmd.delete('m2')

    cmd.create('m2', 'm1', 2, 0)
    assert cmd.count_states('m2') == 2
    cmd.delete('m2')

    cmd.create('m2', 'm1', 0, 2)
    assert cmd.count_states('m2') == 5
    cmd.delete('m2')

    cmd.create('m2', 'm1', 1, 2)
    assert cmd.count_states('m2') == 2
    cmd.delete('m2')

    cmd.create('m2', 'm1', 2, 2)
    assert cmd.count_states('m2') == 2
    cmd.delete('m2')

    cmd.create('m2', 'm1', 0, -1)
    assert cmd.count_states('m2') == 4
    cmd.create('m2', 'm1', 0, -1)
    assert cmd.count_states('m2') == 8
    cmd.create('m2', 'm1', 2, -1)
    assert cmd.count_states('m2') == 9


def testCreateCurrentSourceState():
    create_many_states("gly", "m1", 4)
    cmd.frame(3)

    cmd.create('m2', 'm1', -1, -1)
    assert cmd.count_states('m2') == 1
    cmd.delete('m2')

    cmd.create('m2', 'm1', -1, 0)
    assert cmd.count_states('m2') == 3
    cmd.delete('m2')

    cmd.create('m2', 'm1', -1, 1)
    assert cmd.count_states('m2') == 1
    cmd.delete('m2')

    cmd.create('m2', 'm1', -1, 2)
    assert cmd.count_states('m2') == 2
    cmd.delete('m2')


# PYMOL-3372
@pytest.mark.parametrize("discrete_source", [0, 1])
def testCreateDiscrete(discrete_source):
    create_many_states("methanol", "m1", 2)
    create_many_states("benzene", "m2", 2)
    pymol.editing.set_discrete("m1", discrete=discrete_source)
    pymol.editing.set_discrete("m2", discrete=discrete_source)

    # create new
    cmd.create('dm', 'm1', 0, -1, discrete=1)
    assert cmd.count_discrete('dm')
    assert cmd.count_states('dm') == 2
    assert cmd.count_atoms('dm') == 2 * 6
    assert len(cmd.get_bonds('dm')) == 5

    # append to existing
    cmd.create('dm', 'm2', 0, -1, discrete=1)
    assert cmd.count_discrete('dm')
    assert cmd.count_states('dm') == 4
    assert cmd.count_atoms('dm') == 2 * 6 + 2 * 12
    assert len(cmd.get_bonds('dm', 1)) == 5
    assert len(cmd.get_bonds('dm', 4)) == 12
    assert len(cmd.get_bonds('dm', 0)) == 2 * 5 + 2 * 12


def testExtract():
    cmd.fragment('ala', 'm1')
    cmd.extract('m2', 'elem C')
    assert cmd.count_atoms('m1') == 7
    assert cmd.count_atoms('m2') == 3


@pytest.mark.skip(reason="Not yet implemented.")
def testUnquote():
    pass


def testPseudoatom():
    cmd.set('retain_order')

    cmd.pseudoatom('m1', '', 'A1', 'B2', 1, 'D',
            'E5', 'F', 7.0, 0, 9.0, 0.1, '11', 'foo12',
            (13, 14, 15), 1)
    cmd.pseudoatom('m2', '', 'A1', 'B2', 2, 'A',
            'E5', 'F', 7.0, 0, 9.0, 0.1, '12', 'bar12',
            (13, 10, 15), 1)

    # append to m1, pos and vdw vom selection
    cmd.pseudoatom('m1', 'all', 'A2', 'B2', 3, 'D',
            'E5', 'F', -1, 1, 19.0, 0.2, '13', 'com12',
            None, 1, 'extent')

    r_list = []
    f_indices = [7, 9, 10, 13, 14, 15]

    cmd.iterate_state(1, 'all',
            'r_list.append([model, name, resn, resi, chain, segi, elem, '
            'vdw, type, b, q, color, label, x, y, z])', space=locals())

    for ref, values in zip(r_list, [
        ['m1', 'A1', 'B2', '1', 'D', 'E5', 'F', 7.0, 'ATOM', 9.0, 0.1, 11, 'foo12', 13.0, 14.0, 15.0],
        ['m1', 'A2', 'B2', '3', 'D', 'E5', 'F', 2.0, 'HETATM', 19.0, 0.2, 13, 'com12', 13.0, 12.0, 15.0],
        ['m2', 'A1', 'B2', '2', 'A', 'E5', 'F', 7.0, 'ATOM', 9.0, 0.1, 12, 'bar12', 13.0, 10.0, 15.0],
        ]):
        for i in f_indices:
            values[i] = round(values[i], 1)
            ref[i] = round(ref[i], 1)
        assert ref == values


def testPseudoatomName():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m1')
    assert 2 == cmd.count_atoms()
    assert 1 == cmd.count_atoms('name PS1')
    assert 1 == cmd.count_atoms('name PS2')


def testRampMapBoundary():

    # Test for partial ramp map boundary

    cmd.viewport(100, 100)

    # Long peptide so the surface extends well beyond a partial map
    cmd.fab('AAAAAAAAAA', 'mol')
    cmd.set('gaussian_b_floor', 30)

    # Map covers only the first residue
    cmd.map_new('partial_map', selection='resi 1', buffer=3.0)

    # Solid green ramp spanning the map's value range
    cmd.ramp_new('ramp1', 'partial_map', [-1, 10, 20],
                 ['green', 'green', 'green'])

    cmd.show_as('surface', 'mol')
    cmd.set('surface_color', 'ramp1', 'mol')
    cmd.disable('ramp1')
    testing.ambient_only()

    # View the whole molecule: should have green (in-bounds)
    # and white (out-of-bounds default) regions
    cmd.orient('mol')
    img = testing.get_imagearray(width=100, height=100)
    testing.assert_image_has_color('green', img)
    testing.assert_image_has_color('white', img)


def test_set_raw_alignment():
    cmd.fab('ACDEF', 'm1')
    cmd.fab('CDE', 'm2')
    index_m1 = [('m1', 12), ('m1', 23), ('m1', 35)]
    index_m2 = [('m2',  2), ('m2', 13), ('m2', 25)]
    raw = [list(t) for t in zip(index_m1, index_m2)]
    cmd.set_raw_alignment('aln', raw)
    assert cmd.index('m1 & aln') == index_m1
    assert cmd.index('m2 & aln') == index_m2
