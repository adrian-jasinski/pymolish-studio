import pytest
from pymol import cmd, testing, stored, CmdException


def _testMeasure(func, getfunc, natom, value):
    name = "m_obj"
    cmd.fragment("gly")
    
    r = func(name, *["index %d" % (i+1) for i in range(natom)])
    assert r == pytest.approx(value, abs=1e-2)
    assert name in cmd.get_names()
    
    r = getfunc(*["index %d" % (i+1) for i in range(natom)])
    assert r == pytest.approx(value, abs=1e-2)


def testAngle():
    _testMeasure(cmd.angle, cmd.get_angle, 3, 110.99)


def testAutoMeasure():
    cmd.fragment("gly")

    for (N, prefix) in enumerate(["dist", "angle", "dihedral"], 2):
        cmd.set("dist_counter", 0)
        cmd.edit(*["index %d" % (i + 1) for i in range(N)])
        cmd.auto_measure()
        assert prefix + "01" in cmd.get_names(), prefix


def testCountAtoms():
    # used in many tests
    pass


def testSelectDelocalized():
    cmd.fragment("phe")
    count = cmd.count_atoms("deloc.")
    assert count == 8
    count = cmd.count_atoms("delocalized")
    assert count == 8


def testCountFrames():
    assert cmd.count_frames() == 0
    cmd.pseudoatom("m1")
    assert cmd.count_frames() == 1
    cmd.mset("1x3")
    assert cmd.count_frames() == 3


def testCountStates():
    assert cmd.count_states() == 0
    cmd.pseudoatom("m1")
    assert cmd.count_states() == 1
    cmd.create("m1", "m1", 1, 2)
    assert cmd.count_states() == 2


def testDihedral():
    # result was 0.01318 due to numeric precision in get_angle3f
    _testMeasure(cmd.dihedral, cmd.get_dihedral, 4, 0.0)


def testDistance():
    _testMeasure(cmd.distance, cmd.get_distance, 2, 1.46011)


def testMeasureBetweenStates():
    cmd.load(testing.datafile('1v5a-3models.cif'), 'm1')

    # distance
    d = cmd.distance('d1', '24/CZ', 'same', state1=2, state2=3)
    assert d == pytest.approx(3.0, abs=1e-1)

    # angle
    a = cmd.angle('a1', '24/CZ', 'same', 'same', state1=2, state2=3, state3=1)
    assert a == pytest.approx(73.5, abs=1e-1)

    # visual test
    cmd.viewport(100, 100)
    cmd.set('dash_radius', 1.0)
    testing.ambient_only()
    for name in ['d1', 'a1']:
        cmd.disable('*')
        cmd.enable(name)
        cmd.zoom(name)
        testing.assert_image_has_color('yellow')


def testFindPairs():
    # mode 0
    cmd.fragment("gly")
    pairs = cmd.find_pairs("hydro", "elem O")
    pairs_ref = [
        (('gly', 5), ('gly', 4)),
        (('gly', 6), ('gly', 4)),
        (('gly', 7), ('gly', 4)),
    ]
    assert sorted(pairs) == pairs_ref

    # mode 1
    cmd.fab("GGGGG", "m2", ss=1)
    pairs = cmd.find_pairs("m2 & donor", "m2 & acceptor", mode=1)
    assert pairs == [(('m2', 29), ('m2', 4))]


def testGetAngle():
    # see testAngle
    pass


def testGetArea():
    cmd.fragment("gly")
    r = cmd.get_area(load_b=1)
    b_list = []
    cmd.iterate("elem O", "b_list.append(b)", space=locals())
    assert r == pytest.approx(82.505165, abs=1e-2)
    assert b_list[0] == pytest.approx(15.47754, abs=1e-2)
    cmd.set("dot_solvent")
    assert cmd.get_area() == pytest.approx(200.145, abs=1e-2)
    cmd.set("dot_density", 4)
    assert cmd.get_area() == pytest.approx(200.888, abs=1e-2)


def testGetArea_flags():
    cmd.fragment("gly")
    area_not_O = cmd.get_area('not elem O')
    assert cmd.get_area() > area_not_O
    cmd.flag('exfoliate', 'elem O')
    assert cmd.get_area() == area_not_O
    cmd.flag('ignore', 'elem N')
    area_ignore_N = cmd.get_area()
    assert area_ignore_N != area_not_O
    assert cmd.count_atoms() == 7
    cmd.remove('elem N')
    assert cmd.count_atoms() == 6
    assert cmd.get_area() == area_ignore_N
    cmd.flag('ignore', 'all')
    assert cmd.get_area() == 0.0


def testGetAtomCoords():
    cmd.fragment("gly")
    coords = cmd.get_atom_coords("elem O")
    coords_ref = [0.545436, -0.974895, 1.498943]
    testing.assert_array_equal(coords, coords_ref, delta=1e-4)
    pytest.raises(CmdException, cmd.get_atom_coords, "*")


def testGetChains():
    cmd.pseudoatom("m1", chain="C")
    assert cmd.get_chains() == ["C"]


def testGetColorIndex():
    assert cmd.get_color_index("blue") == 2


def testGetColorIndices():
    r = cmd.get_color_indices()
    assert set(r).issuperset([('white', 0), ('black', 1), ('blue', 2)])
    assert not (('grey50', 104) in r)
    r = cmd.get_color_indices(all=1)
    assert ('grey50', 104) in r


def testGetColorTuple():
    assert (0.0, 0.0, 1.0) == cmd.get_color_tuple("blue")


def testGetDihedral():
    # see testDihedral
    pass


def testGetDistance():
    # see testDistance
    pass


def testGetDragObjectName():
    cmd.fragment('gly')
    assert cmd.get_drag_object_name() == ''
    cmd.drag('gly')
    assert cmd.get_drag_object_name() == 'gly'


def testGetExtent():
    cmd.load(testing.datafile("1ehz-5.pdb"), "m1")
    testing.assert_array_equal(cmd.get_extent(),
            [[49.85, 40.59, 41.73], [69.99, 51.73, 56.47]], delta=1e-2)
    testing.assert_array_equal(cmd.get_extent("resi 3"),
            [[58.29, 40.87, 48.52], [64.74, 50.42, 55.29]], delta=1e-2)
    cmd.load(testing.datafile("h2o-elf.cube"), "map1")
    testing.assert_array_equal(cmd.get_extent("map1"),
            [[-0.075, -0.075, -0.075], [5.925, 5.925, 5.925]], delta=1e-2)


def testGetIdtf():
    cmd.fragment('gly')
    cmd.show_as('surface')
    r = cmd.get_idtf()
    assert isinstance(r, tuple)
    assert len(r) == 2
    assert r[0].startswith('FILE_FORMAT "IDTF"')
    assert 'MODEL_POSITION_LIST' in r[1]
    assert 'MODEL_NORMAL_LIST' in r[1]


def testGetLegalName():
    assert cmd.get_legal_name("foo bar baz") == "foo_bar_baz"


def testGetModalDraw():
    assert cmd.get_modal_draw() == 0


def testGetModel():
    '''
        Test coordinates and "reference" coordinates with various
        transformations.
        '''

    # create two-state object
    # displace state 1, will do tests on state 2
    cmd.fragment('ala', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.translate([1, 2, 3], 'm1', 1)

    # prepare state 2
    title = 'Alanin'
    cmd.set_title('m1', 2, title)
    cmd.reference(state=2)

    # with original coordinates
    m = cmd.get_model(state=2)
    a = m.atom[0]

    # title
    assert title == m.molecule.title

    # bonds (covering count, indices and order)
    assert set(tuple(sorted(b.index)) + (b.order,) for b in m.bond) == set([(0, 1, 1), (0, 5, 1), (1, 2, 1), (1, 4, 1), (1, 6, 1),
                (2, 3, 2), (4, 7, 1), (4, 8, 1), (4, 9, 1)])

    # expect equal coord and ref_coord
    coord = [-0.67689997, -1.23029995, -0.49050000]
    testing.assert_array_equal(a.ref_coord,  coord, delta=1e-4)
    testing.assert_array_equal(a.coord,      coord, delta=1e-4)

    # modify ttt
    cmd.set_object_ttt('m1', [
      0, 1, 0, 0,
     -1, 0, 0, 5,
      0, 0, 1, 0,
      0, 3, 0, 1,
    ]) # no state! API flaw, TTT object are not per state
    m = cmd.get_model('m1', state=2)
    a = m.atom[0]

    # ttt should affect both equally
    coord = [1.769700050354004, 5.6768999099731445, -0.49050000309944153]
    testing.assert_array_equal(a.ref_coord,  coord, delta=1e-4)
    testing.assert_array_equal(a.coord,      coord, delta=1e-4)

    # modify coords
    cmd.translate([10, 0, 0], state=2)
    m = cmd.get_model('m1', state=2)
    a = m.atom[0]

    # no effect of ref_coord
    ref = coord
    coord = [11.769700050354004, 5.6768999099731445, -0.49050000309944153]
    testing.assert_array_equal(a.ref_coord,  ref, delta=1e-4)
    testing.assert_array_equal(a.coord,      coord, delta=1e-4)

    # modify coords by alignment
    cmd.fragment('ala', 'm2')
    cmd.rotate('x', 90, 'm2')
    cmd.align('m1', 'm2', mobile_state=2)
    m = cmd.get_model('m1', state=2)
    a = m.atom[0]

    # no effect of ref_coord
    coord = [3.490499973297119, 5.6768999099731445, -1.230299949645996]
    testing.assert_array_equal(a.ref_coord,  ref, delta=1e-4)
    testing.assert_array_equal(a.coord,      coord, delta=1e-4)


def testGetMovieLength():
    cmd.fragment('gly')
    assert cmd.get_movie_length() == 0
    cmd.mset('1x10')
    assert cmd.get_movie_length() == 10
    assert cmd.get_movie_length(images=1) == 0


def testGetMovieLocked():
    assert cmd.get_movie_locked() == 0
    cmd.mset('1x1')
    cmd.mdo(1, 'cmd.color("blue")')
    s = cmd.get_session()
    cmd.set_session(s)
    assert cmd.get_movie_locked() == 1
    cmd.set('security', 0)
    cmd.set_session(s)
    assert cmd.get_movie_locked() == 0


def testGetMtlObj():
    cmd.fragment('gly')
    cmd.show_as('surface')
    r = cmd.get_mtl_obj()
    assert isinstance(r, tuple)
    assert len(r) == 2
    lines = r[1].splitlines()
    assert lines[0].startswith('v ')
    assert lines[1].startswith('v ')
    assert lines[2].startswith('v ')
    assert lines[3].startswith('vn ')
    assert lines[4].startswith('vn ')
    assert lines[5].startswith('vn ')
    assert lines[6].startswith('f ')
    assert all(len(line.split()) == 4 for line in lines)


def testGetNames():
    cmd.fragment('gly')
    cmd.fragment('cys')
    cmd.ramp_new('ramp1', 'none')  # non-molecular object
    cmd.select('foo', 'none')
    assert cmd.get_names() == ['gly', 'cys', 'ramp1']
    assert cmd.get_names(selection="elem S") == ['cys']
    cmd.disable('gly')
    cmd.disable('ramp1')
    assert cmd.get_names(enabled_only=1) == ['cys']
    assert cmd.get_names('selections') == ['foo']
    assert cmd.get_names('all') == ['gly', 'cys', 'ramp1', 'foo']


def testGetNamesOfType():
    cmd.fragment('gly', 'm1')
    cmd.fragment('ala', 'm2')
    cmd.ramp_new('ramp1', 'none')
    assert cmd.get_names_of_type('object:molecule') == ['m1', 'm2']
    assert cmd.get_names_of_type('object:ramp') == ['ramp1']
    assert cmd.get_names_of_type('object:map') == []


def testGetObjectColorIndex():
    cmd.fragment('gly', 'm1')
    cmd.color(3, 'm1')
    assert cmd.get_object_color_index('m1') == 3
    cmd.color(5, '(m1)')
    assert cmd.get_object_color_index('m1') == 3
    cmd.color(5, 'm1')
    assert cmd.get_object_color_index('m1') == 5
    cmd.set_object_color('m1', 7)
    assert cmd.get_object_color_index('m1') == 7


def testGetObjectList():
    cmd.fragment('gly')
    cmd.fragment('cys')
    cmd.ramp_new('ramp1', 'none')  # non-molecular object
    assert cmd.get_object_list() == ['gly', 'cys']
    assert cmd.get_object_list('elem S') == ['cys']
    assert cmd.get_object_list('none') == []
    # whitespace string is empty selection
    assert cmd.get_object_list(' ') == []
    # empty string is a falsy value
    assert not cmd.get_object_list('')
    # empty string is empty selection
    assert cmd.get_object_list('') == []


def testGetObjectList__invalid_selection():
    pytest.raises(CmdException, cmd.get_object_list, 'invalid_selection_name')
    pytest.raises(CmdException, cmd.get_object_list, '(none')  # malformed


def testGetObjectMatrix():
    identity = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0)
    mat_x90 = (
        1.0, 0.0,  0.0, 0.0,
        0.0, 0.0, -1.0, 0.0,
        0.0, 1.0,  0.0, 0.0,
        0.0, 0.0,  0.0, 1.0)

    cmd.fragment('ala', 'm1')
    cmd.fragment('gly', 'm2')

    # default/identity
    mat = cmd.get_object_matrix('m1', incl_ttt=1)
    assert isinstance(mat, tuple)
    testing.assert_array_equal(mat, identity, delta=1e-6)
    mat = cmd.get_object_matrix('m1', incl_ttt=0)
    testing.assert_array_equal(mat, identity, delta=1e-6)

    # TTT
    cmd.rotate('x', 90, object='m1', camera=0, object_mode=0)
    mat = cmd.get_object_matrix('m1', incl_ttt=1)
    testing.assert_array_equal(mat, mat_x90, delta=1e-6)
    mat = cmd.get_object_matrix('m1', incl_ttt=0)
    testing.assert_array_equal(mat, identity, delta=1e-6)

    # state matrix
    cmd.rotate('x', 90, object='m2', camera=0, object_mode=1)
    mat = cmd.get_object_matrix('m2', incl_ttt=1)
    testing.assert_array_equal(mat, mat_x90, delta=1e-6)
    mat = cmd.get_object_matrix('m2', incl_ttt=0)
    testing.assert_array_equal(mat, mat_x90, delta=1e-6)


def assertPhiPsiEqual(pp, pp_ref):
    assert len(pp) == len(pp_ref)
    for key in pp:
        testing.assert_array_equal(pp[key], pp_ref[key], delta=1e-2)


def _testGetPhipsi(func):
    cmd.load(testing.datafile("1oky-frag.pdb"), "m1")
    pp = func("resi 1-81")
    assertPhiPsiEqual(pp, {
        ('m1', 13): (-43.4902, -42.8589),
        ('m1', 20): (-61.0592, -19.4712),
        ('m1', 29): (-72.9009, -8.8334)
    })
    pp = func("resi 117- & name CA")
    assertPhiPsiEqual(pp, {
        ('m1', 316): (-59.7243, -43.9939),
        ('m1', 326): (-61.4714, -47.4775)
    })


def testGetPhipsi():
    return _testGetPhipsi(cmd.get_phipsi)


def testGetPosition():
    cmd.pseudoatom(pos=(1, 2, 3))
    testing.assert_array_equal(cmd.get_position(), [0., 0., 0.], delta=1e-4)
    cmd.zoom(animate=0)
    testing.assert_array_equal(cmd.get_position(), [1., 2., 3.], delta=1e-4)


def testGetPovray():
    cmd.fragment('gly')
    cmd.show_as('sticks')
    pov = cmd.get_povray()
    assert isinstance(pov, tuple)
    assert len(pov) == 2
    assert pov[0].startswith('camera {direction<0.0,0.0')
    assert pov[1].startswith('cylinder{<')


def testGetRawAlignment():
    from collections import defaultdict
    cmd.fab('ACDEGGKLMN', 'm1')
    cmd.fab('CDEFFGGK', 'm2')
    cmd.fab('ASDEKLMNFY', 'm3')
    cmd.align('m2 & guide', 'm1 & guide', cycles=0, object='aln')
    cmd.align('m3 & guide', 'm1 & guide', cycles=0, object='aln')
    cmd.disable('m2')
    # expecting alignment:
    # m1 ACDE--GGKLMN--
    # m2 -CDEFFGGK-----
    # m3 ASDE----KLMQFY
    guideids = defaultdict(list)
    cmd.iterate('guide', 'guideids[model].append(index)', space=locals())
    idx = lambda m, i: (m, guideids[m][i])
    aln_expect = [
        [idx('m1', 0),               idx('m3', 0)],
        [idx('m1', 1), idx('m2', 0), idx('m3', 1)],
        [idx('m1', 2), idx('m2', 1), idx('m3', 2)],
        [idx('m1', 3), idx('m2', 2), idx('m3', 3)],
        [idx('m1', 4), idx('m2', 5),             ],
        [idx('m1', 5), idx('m2', 6),             ],
        [idx('m1', 6), idx('m2', 7), idx('m3', 4)],
        [idx('m1', 7),               idx('m3', 5)],
        [idx('m1', 8),               idx('m3', 6)],
        [idx('m1', 9),               idx('m3', 7)],
    ]
    dictify = lambda aln: [dict(col) for col in aln]
    aln_expect = dictify(aln_expect)

    aln = cmd.get_raw_alignment('aln', 0)
    assert dictify(aln) == aln_expect

    # remove m2 from alignment
    for d in aln_expect:
        d.pop('m2', None)

    aln = cmd.get_raw_alignment('aln', 1)
    assert dictify(aln) == aln_expect


def testGetRenderer():
    r = cmd.get_renderer()
    assert len(r) == 3


def testGetSymmetry():
    cmd.load(testing.datafile('1rx1.pdb'))
    sym = cmd.get_symmetry('1rx1')
    testing.assert_array_equal(sym[:6],
            [34.455, 45.370, 98.701, 90.0, 90.0, 90.0], delta=1e-3)
    assert sym[6] == 'P 21 21 21'

    cmd.fragment('gly', 'm1')
    assert cmd.get_symmetry('m1') is None


def testGetTitle():
    cmd.fragment('gly', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    title = cmd.get_title('m1', 1)
    assert title == ''
    cmd.set_title('m1', 1, 'foo bar')
    title = cmd.get_title('m1', 1)
    assert title == 'foo bar'
    title = cmd.get_title('m1', 2)
    assert title == ''
    cmd.set_title('m1', 2, 'second state')
    title = cmd.get_title('m1', 2)
    assert title == 'second state'


def testGetType():
    cmd.fragment('gly', 'm1')
    assert cmd.get_type('m1') == 'object:molecule'
    cmd.ramp_new('ramp1', 'none')
    assert cmd.get_type('ramp1') == 'object:ramp'
    cmd.select('s1', 'elem C')
    assert cmd.get_type('s1') == 'selection'


def testGetUnusedName():
    n1 = cmd.get_unused_name()
    assert n1 == "tmp01"
    n2 = cmd.get_unused_name("foo", 0)
    assert n2 == "foo"
    cmd.pseudoatom("foo")
    n3 = cmd.get_unused_name("foo", 0)
    assert n3 == "foo01"
    cmd.pseudoatom("foo01")
    cmd.pseudoatom("foo02")
    n4 = cmd.get_unused_name("foo")
    assert n4 == "foo03"
    cmd.delete('*')
    n5 = cmd.get_unused_name("foo")
    assert n5 == "foo01"


def testGetVersion():
    # see tests/api/get_version.py
    pass


def testGetVolumeField():
    import numpy
    cmd.load(testing.datafile('emd_1155.ccp4'), 'map1')
    fieldcopy = cmd.get_volume_field('map1')
    field = cmd.get_volume_field('map1', copy=0)
    assert field.shape == (141, 91, 281)
    assert numpy.allclose(field, fieldcopy)

    # data manipulation with copy=0
    mean1 = field.mean()
    field += 5.0
    mean2 = cmd.get_volume_field('map1', copy=0)[:].mean()
    assert mean1 + 5.0 == pytest.approx(mean2, abs=1e-2)


def testGetVolumeHistogram():
    cmd.load(testing.datafile('h2o-elf.cube'), 'map1')
    hist1 = cmd.get_volume_histogram('map1', 10)
    assert len(hist1) == 14
    hist2 = cmd.get_volume_histogram('map1', 2)
    testing.assert_array_equal(hist2, [-0.0151, 0.9292, 0.0692, 0.1720, 63812.0, 188.0], delta=1e-4)
    testing.assert_array_equal(hist1[:4], hist2[:4])
    assert sum(hist1[4:]) == sum(hist2[4:])
    hist2 = cmd.get_volume_histogram('map1', 2, (0.3, 0.7))
    testing.assert_array_equal(hist2, [0.3, 0.7, 0.0692, 0.172, 62263.0, 1737.0], delta=1e-4)


def testGetVrml():
    cmd.fragment('gly')
    cmd.show_as('sticks')
    s = cmd.get_vrml()
    assert s.startswith('#VRML V')
    assert 'geometry Cylinder' in s
    cmd.show_as('spheres')
    s = cmd.get_vrml()
    assert not ('geometry Cylinder' in s)
    assert 'geometry Sphere' in s


def testIdAtom():
    cmd.fragment('gly', 'm1')
    assert cmd.id_atom('ID 3') == 3
    assert cmd.id_atom('ID 3', 1) == ('m1', 3)
    cmd.feedback("disable", "cmd", "errors")
    pytest.raises(CmdException, cmd.id_atom, 'ID 3+4')
    pytest.raises(CmdException, cmd.id_atom, 'ID 100')


def testIdentify():
    cmd.fragment('gly', 'm1')
    cmd.select('s1', 'ID 3+4')
    r = cmd.identify('s1')
    assert sorted(r) == sorted([3, 4])
    r = cmd.identify('s1', 1)
    assert sorted(r) == sorted([('m1', 3), ('m1', 4)])


def testIndex():
    cmd.fragment('gly', 'm1')
    r = cmd.index('index 3+4')
    assert sorted(r) == sorted([('m1', 3), ('m1', 4)])


def testOverlap():
    # unsupported command
    cmd.pseudoatom('m1', vdw=2.0)
    cmd.pseudoatom('m2', vdw=2.0, pos=(2., 0., 0.))
    r = cmd.overlap('m1', 'm2')
    # this is actually half the vdw overlap
    assert r == 1.0


def testPhiPsi():
    return _testGetPhipsi(cmd.phi_psi)


def testGetBonds():
    assert [] == cmd.get_bonds()
    cmd.fragment('gly')
    assert [] == cmd.get_bonds('none')
    assert [
        (0, 1, 1), # C-C
        (1, 2, 2), # C=O
    ] == cmd.get_bonds('elem C+O')
    assert [
        (0, 1, 1),
        (0, 4, 1),
        (1, 2, 1),
        (1, 5, 1),
        (1, 6, 1),
        (2, 3, 2),
    ] == cmd.get_bonds()


def testPiInteractions():
    # 1rx1 has 4 pi-pi and 1 pi-cation
    coords_ref_pi_pi = [
            30.962, 56.116,  4.616, 27.154, 59.807,  4.965,
            23.588, 39.248, 24.729, 18.578, 38.629, 23.297,
            28.754, 34.308, 11.073, 31.535, 31.381, 12.396,
            36.444, 30.384, 13.916, 31.535, 31.381, 12.396]
    coords_ref_pi_cat = [
            24.198, 57.834, 15.137, 25.219, 59.507, 17.986]
    coords_ref_pi = coords_ref_pi_pi + coords_ref_pi_cat

    cmd.load(testing.datafile('1rx1.pdb'))

    cmd.pi_interactions('p1')
    coords = cmd.get_session('p1', 1)['names'][0][5][2][0][1]
    testing.assert_array_equal(coords, coords_ref_pi, delta=1e-2)

    cmd.distance('p2', '1rx1', 'same', mode=6)
    coords = cmd.get_session('p2', 1)['names'][0][5][2][0][1]
    testing.assert_array_equal(coords, coords_ref_pi_pi, delta=1e-2)

    cmd.distance('p3', '1rx1', 'same', mode=7)
    coords = cmd.get_session('p3', 1)['names'][0][5][2][0][1]
    testing.assert_array_equal(coords, coords_ref_pi_cat, delta=1e-2)


# incentive: 1.8.4, open-source: 2.1
def test_get_object_settings():
    cmd.pseudoatom("m1")
    # global (should have no influence)
    cmd.set("half_bonds")
    # object-level
    cmd.set("cartoon_gap_cutoff", 5, "m1")
    cmd.set("grid_slot", 3, "m1")
    cmd.set("wildcard", "#", "m1")
    # ostate-level
    cmd.set("cartoon_gap_cutoff", 7, "m1", 1)
    cmd.set("ribbon_sampling", 9, "m1", 1)
    # object-level
    s = cmd.get_object_settings("m1")
    assert s == [[412, 6, '#'], [579, 2, 3], [750, 2, 5]]
    # ostate-level
    s = cmd.get_object_settings("m1", state=1)
    assert s == [[19, 2, 9], [750, 2, 7]]
