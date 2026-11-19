import pytest
import sys
import random
from pymol import cmd, testing, stored

expr_list = [
    'segi', 'chain', 'resn', 'resi', 'name', 'alt', 'elem', 'text_type',
    'formal_charge', 'numeric_type', 'ID',
    'q', 'b', 'partial_charge', 'vdw',
]


def _assertIterate(expr, selection):
    stored.v = []
    cmd.iterate(selection, 'stored.v.append(%s)' % expr)
    assert len(stored.v) == cmd.count_atoms(selection)
    return stored.v


def assertEqualIterate(a, b, selection='*', msg=None):
    for va, vb in _assertIterate('(%s,%s)' % (a, b), selection):
        for t in (float, int):
            if isinstance(va, t) or isinstance(vb, t):
                va, vb = t(va), t(vb)
        assert va == vb, '%s=%s != %s=%s' % (a, repr(va), b, repr(vb))


def assertTrueIterate(expr, selection='*', msg=None):
    for v in _assertIterate(expr, selection):
        assert v, expr


def assertViewIs(view):
    view = [round(v, 2) for v in view]
    ref = [round(v, 2) for v in cmd.get_view()]
    assert view == ref, 'view differs'


def _load_default_scene():
    cmd.load('viewing-ref/ref.pse')
    cmd.set_view((
        1.0,    0.0,    0.0,
        0.0,    1.0,    0.0,
        0.0,    0.0,    1.0,
        0.0,    0.0,  -43.0,
        2.6,   -1.9,    0.0,
       36.4,   49.6,  -20.0))


def _testZoomGeneric(func, views):
    _load_default_scene()
    cmd.frame(2)

    for (state, view) in views.items():
        func(state=state)
        assertViewIs(view)

    func(state=-1)
    assertViewIs(views[2])


def testZoom():
    views = {
        0: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -30.417539596557617,
            1.666666865348816, -1.6666665077209473, 0.0, 23.981420516967773,
            36.853660583496094, -20.0),
        1: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -14.178204536437988,
            0.0, 0.0, 0.0, 11.178204536437988, 17.178203582763672, -20.0),
        2: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, -14.178204536437988,
            4.999999046325684, 0.0, 0.0, 11.178204536437988, 17.178203582763672, -20.0),
    }
    _testZoomGeneric(cmd.zoom, views)

    cmd.zoom('all', 2.0, 3, 1)
    assertViewIs((1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
        0.0, 0.0, -25.093609, 0.0, -5.0, 0.0, 19.783993, 30.403225, -20.0))


def testCenter():
    views = {
        0: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, -43.0, 1.666666865348816, -1.6666665077209473, 0.0,
            36.400001525878906, 49.599998474121094, -20.0),
        1: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, -43.0, 0.0, 0.0, 0.0,
            36.400001525878906, 49.599998474121094, -20.0),
        2: (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
            0.0, 0.0, -43.0, 4.999999046325684, 0.0, 0.0,
            36.400001525878906, 49.599998474121094, -20.0),
    }
    _testZoomGeneric(cmd.center, views)


def testOrient():
    views = {
        0: (0.6800623536109924, -0.7324044704437256, 0.03314966708421707, 0.7331299781799316,
            0.6789760589599609, -0.03888334706425667, 0.005970506463199854, 0.05074610933661461,
            0.9986937046051025, 0.0, 0.0, -30.417539596557617, 1.666666865348816,
            -1.6666665077209473, 0.0, 23.981420516967773, 36.853660583496094, -20.0),
        1: (-0.4805402159690857, -0.8505961298942566, 0.21346519887447357, 0.7515078186988831,
            -0.5248664617538452, -0.39968883991241455, 0.4520145058631897, -0.031645797193050385,
            0.8914490342140198, 0.0, -0.0, -14.178204536437988, 0.0, 0.0, 0.0, 11.178204536437988,
            17.178203582763672, -20.0),
        2: (-0.4805402159690857, -0.8505960702896118, 0.21346530318260193, 0.7515078186988831,
            -0.52486652135849, -0.3996887803077698, 0.4520145058631897, -0.03164568170905113,
            0.8914490938186646, 0.0, -0.0, -14.178204536437988, 4.999999046325684, 0.0, 0.0,
            11.178204536437988, 17.178203582763672, -20.0),
    }
    _testZoomGeneric(cmd.orient, views)


def testClip():
    for a in "xyz":
        cmd.turn(a, random.random() * 10 - 5)
        cmd.move(a, random.random() * 10 - 5)
    v = cmd.get_view()
    cmd.clip("near", -5)
    assert v[15] + 5 == pytest.approx(cmd.get_view()[15], abs=1e-3)
    cmd.clip("far", 10)
    assert v[16] - 10 == pytest.approx(cmd.get_view()[16], abs=1e-3)
    cmd.clip("move", -15)
    a = cmd.get_view()
    assert v[15] == pytest.approx(a[15] - 20, abs=1e-3)
    assert v[16] == pytest.approx(a[16] - 5, abs=1e-3)
    cmd.clip("slab", 20)
    v = cmd.get_view()
    assert v[16] - v[15] == pytest.approx(20.0, abs=1e-3)
    cmd.pseudoatom()
    cmd.clip("atoms", 5, "all")
    v = cmd.get_view()
    assert v[16] - v[15] == pytest.approx(10.0, abs=1e-3)


def testOrigin():
    from chempy import cpv
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3', pos=[1,0,0])
    # by selection
    cmd.origin('m3')
    cmd.rotate('y', 90, 'm1')
    # by position
    cmd.origin(position=[-1,0,0])
    cmd.rotate('y', 90, 'm2')
    coords = []
    cmd.iterate_state(1, 'm1 m2', 'coords.append([x,y,z])', space=locals())
    d = cpv.distance(*coords)
    assert d == pytest.approx(2 * 2**0.5, abs=5e-8)


def testMove():
    for a in "xyz":
        cmd.turn(a, random.random() * 10 - 5)
        cmd.move(a, random.random() * 10 - 5)
    v = list(cmd.get_view())
    d = (2,4,6)
    cmd.move("x", d[0])
    cmd.move("y", d[1])
    cmd.move("z", d[2])
    m = cmd.get_view()
    v[9] += d[0]
    v[10] += d[1]
    v[11] += d[2]
    v[15] -= d[2]
    v[16] -= d[2]
    testing.assert_array_equal(v, m, delta=1e-3)


def testEnable():
    cmd.create('m1', 'none')
    cmd.create('m2', 'none')
    cmd.disable()
    assert cmd.get_names('public_objects', 1) == []
    cmd.enable('m1')
    assert cmd.get_names('public_objects', 1) == ['m1']
    cmd.enable()
    assert cmd.get_names('public_objects', 1) == ['m1', 'm2']


def testDisable():
    # see testEnable
    pass


def testToggle():
    if testing.PYMOL_VERSION[1] > 1.84:
        cmd.set('auto_show_classified', 0)

    cmd.fragment('gly')
    cmd.show('sticks')
    cmd.show('spheres')
    cmd.toggle()
    assert cmd.count_atoms('rep lines') == 0
    assert cmd.count_atoms('rep sticks') == 7
    assert cmd.count_atoms('rep spheres') == 7
    cmd.toggle()
    cmd.toggle('sticks', '(all)')
    assert cmd.count_atoms('rep lines') == 7
    assert cmd.count_atoms('rep sticks') == 0
    assert cmd.count_atoms('rep spheres') == 7
    cmd.toggle('sticks', '(all)')
    cmd.toggle('spheres', '(all)')
    assert cmd.count_atoms('rep lines') == 7
    assert cmd.count_atoms('rep sticks') == 7
    assert cmd.count_atoms('rep spheres') == 0


def testShow():
    if testing.PYMOL_VERSION[1] > 1.84:
        cmd.set('auto_show_classified', 0)

    cmd.fragment('ala')
    assert cmd.count_atoms('rep sticks') == 0
    cmd.show('sticks')
    assert cmd.count_atoms('rep sticks') == 10
    cmd.hide('lines', 'not elem C')
    assert cmd.count_atoms('rep lines') == 3


def testHide():
    # see testShow
    pass


def testView():
    cmd.turn('x', 30)
    a = cmd.get_view()
    cmd.view('A', 'store')
    cmd.turn('y', 30)
    assert a != cmd.get_view()
    cmd.view('A', 'recall', animate=0)
    assert a == cmd.get_view()


def testScene():
    cmd.fragment('ala', 'm1')
    cmd.fragment('gly', 'm2')
    cmd.create('m2', 'm2', 1, 2)
    cmd.create('m2', 'm2', 1, 3)
    cmd.create('m2', 'm2', 1, 4)

    # store
    cmd.show_as('sticks', 'm1')
    cmd.show_as('spheres', 'm2')
    cmd.color('blue', 'm1')
    cmd.color('yellow', 'm2')
    view_001 = cmd.get_view()
    cmd.scene('new', 'store', 'hello world')

    # store
    cmd.frame(3)
    cmd.show_as('lines')
    cmd.color('red')
    cmd.turn('x', 45)
    view_002 = cmd.get_view()
    cmd.scene('new', 'store')

    # we actually don't know the auto naming counter
    # self.assertEqual(cmd.get_scene_list(), ['001', '002'])
    names = cmd.get_scene_list()

    # recall
    cmd.scene(names[0], 'recall', animate=0)
    testing.assert_array_equal(view_001, cmd.get_view(), delta=1e-3)
    assert cmd.count_atoms('m1') == cmd.count_atoms('color blue')
    assert cmd.count_atoms('m1') == cmd.count_atoms('rep sticks')
    assert cmd.count_atoms('m2') == cmd.count_atoms('color yellow')
    assert cmd.count_atoms('m2') == cmd.count_atoms('rep spheres')
    assert cmd.get_wizard() != None
    assert cmd.get_state() == 1

    # recall
    cmd.scene(names[1], 'recall', animate=0)
    testing.assert_array_equal(view_002, cmd.get_view(), delta=1e-3)
    assert 0 == cmd.count_atoms('color blue')
    assert 0 == cmd.count_atoms('rep sticks')
    assert cmd.count_atoms() == cmd.count_atoms('color red')
    assert cmd.count_atoms() == cmd.count_atoms('rep lines')
    assert cmd.get_wizard() == None
    assert cmd.get_state() == 3

    # with movie (not playing) it must not recall the state
    cmd.mset('1-4')
    cmd.frame(1)
    cmd.scene(names[1], 'recall', animate=0)
    assert cmd.get_state() == 1

    # rename and delete
    cmd.scene('F2', 'store')
    cmd.scene(names[0], 'rename', new_key='F1')
    cmd.scene(names[1], 'delete')
    assert cmd.get_scene_list() == ['F1', 'F2']


def testSceneInsertBeforeAfter():
    # insert_before and insert_after
    cmd.scene('F1', 'store')
    cmd.scene('F2', 'store')
    cmd.scene('F1')
    cmd.scene('new', 'insert_after')
    cmd.scene('new', 'insert_before')
    names = cmd.get_scene_list()
    assert names[0] == 'F1'
    assert names[3] == 'F2'
    # we don't know the auto naming counter, but we know this:
    assert names[1] > names[2]


def testSceneOrder():
    cmd.scene('Z0', 'store')
    cmd.scene('F1', 'store')
    cmd.scene('F10', 'store')
    cmd.scene('F2', 'store')
    cmd.scene_order('*', True)
    assert cmd.get_scene_list() == ['F1', 'F2', 'F10', 'Z0']
    cmd.scene_order('F10 F1')
    assert cmd.get_scene_list() == ['F2', 'F10', 'F1', 'Z0']
    cmd.scene_order('F10 F1', location='top')
    assert cmd.get_scene_list() == ['F10', 'F1', 'F2', 'Z0']
    cmd.scene_order('F10 F1', location='bottom')
    assert cmd.get_scene_list() == ['F2', 'Z0', 'F10', 'F1']


def testSceneOrderWithSpaces():
    cmd.scene('Z0 1 2', 'store')
    cmd.scene('F1 ABC', 'store')
    cmd.scene('F10 XX', 'store')
    cmd.scene_order('*', True)
    assert cmd.get_scene_list() == ['F1 ABC', 'F10 XX', 'Z0 1 2']
    cmd.scene_order(['F10 XX', 'F1 ABC'])
    assert cmd.get_scene_list() == ['F10 XX', 'F1 ABC', 'Z0 1 2']


def testSceneMessage():
    message = 'check'
    name = 'TestM'
    cmd.scene(name, 'store')
    cmd.set_scene_message(name, message)
    assert cmd.get_scene_message(name) == message


@testing.requires('gui')
def testStereo():
    for (k,v) in cmd.stereo_dict.items():
        if v < 1:
            continue
        cmd.stereo(k)
        assert cmd.get_setting_int('stereo')
        assert cmd.get_setting_int('stereo_mode') == v
    cmd.stereo('off')
    assert not cmd.get_setting_int('stereo')
    cmd.stereo('on')
    assert cmd.get_setting_int('stereo')
    shift = cmd.get_setting_float('stereo_shift')
    cmd.stereo('swap')
    assert cmd.get_setting_float('stereo_shift') == pytest.approx(-shift, abs=5e-8)


def testTurn():
    cmd.turn('z', 90)
    v = cmd.get_view()
    testing.assert_array_equal(v[:9], [0.,1.,0.,-1.,0.,0.,0.,0.,1.], delta=1e-3)


def testRock():
    cmd.rock(1)
    assert cmd.get_setting_int('rock')
    cmd.rock(0)
    assert not cmd.get_setting_int('rock')
    cmd.rock(-1)
    assert cmd.get_setting_int('rock')
    cmd.rock(-1)
    assert not cmd.get_setting_int('rock')


@pytest.mark.parametrize("func", [cmd.label, cmd.label2])
def testLabel(func):
    cmd.pseudoatom('m1')
    for expr in expr_list + ['resn + " " + resi']:
        func('*', expr)
        assertEqualIterate('label', expr)
    func()
    assertTrueIterate('label == ""')


def testLabelUnicode():
    if sys.version_info[0] < 3:
        uchr = unichr
    else:
        uchr = chr

    stored.L_unicode = u''.join(uchr(i) for i in range(32, 0x1FF))
    stored.L_utf8 = stored.L_unicode.encode('utf-8')

    assert not isinstance(stored.L_unicode, bytes)
    assert isinstance(stored.L_utf8, bytes)

    cmd.pseudoatom('pseudo_unicode', label=stored.L_unicode)
    cmd.pseudoatom('pseudo_utf8', label=stored.L_utf8)
    cmd.pseudoatom('label_unicode')
    cmd.pseudoatom('label_utf8')
    cmd.label('label_unicode', 'stored.L_unicode')
    cmd.label('label_utf8', 'stored.L_utf8')

    stored.check_unicode = []
    cmd.iterate('all', 'stored.check_unicode.append(label == stored.L_unicode)')
    assert all(stored.check_unicode)


def testWindow():
    cmd.window
    pytest.skip('TODO')


def testViewport():
    v = (100,50)
    cmd.viewport(*v)
    assert cmd.get_viewport() == v


def testCartoon():
    cmd.load(testing.datafile("1t46-frag.pdb"))
    cmd.cartoon("skip")
    cmd.cartoon("rect", "resi 590-593")
    cmd.cartoon("oval", "resi 595-598")
    cmd.cartoon("tube", "resi 600-602")
    cmd.cartoon("putty", "resi 606-620")
    cmd.cartoon("dumbbell", "resi 623-625")
    cmd.set("cartoon_highlight_color", "red")
    cmd.color("yellow")
    cmd.show_as("cartoon")
    cmd.viewport(200, 100)
    cmd.set_view(
        (-0.102381177, 0.9807688, -0.16615206, -0.781365454, 0.024080699,
         0.623609841, 0.615618646, 0.193670169, 0.763873398, -0.000125334,
         -0.000184208, -65.135032654, 24.068731308, 26.194671631,
         53.642494202, 40.266975403, 89.999656677, -20.))
    testing.ambient_only()
    testing.assert_image_equal("viewing-ref/cartoon.png", delta=1)


def testCapture():
    cmd.capture
    pytest.skip('TODO')


def testDraw():
    cmd.draw
    pytest.skip('TODO')


def testRay():
    # tested in many other tests
    pass


def testRefresh():
    cmd.refresh
    pytest.skip('TODO')


def testReset():
    # view
    v = cmd.get_view()
    cmd.turn('x', 10)
    cmd.move('y', 10)
    assert v != cmd.get_view()
    cmd.reset()
    assert v == cmd.get_view()
    # object
    cmd.pseudoatom("m1")
    x = cmd.get_object_matrix("m1")
    cmd.translate([1,2,3], object="m1")
    assert x != cmd.get_object_matrix("m1")
    cmd.reset("m1")
    assert x == cmd.get_object_matrix("m1")


def testDirty():
    cmd.dirty
    pytest.skip('TODO')


def testRebuild():
    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.pseudoatom("m1", pos=(0, 0, 0), vdw=1)
    cmd.pseudoatom("m2", pos=(0, 0, -4), vdw=1)
    cmd.zoom()
    cmd.show('spheres')
    cmd.color("blue", "m1")
    cmd.color("red", "m2")
    testing.assert_image_has_not_color('red')
    cmd.alter("m2", "vdw=2")
    testing.assert_image_has_not_color('red')
    cmd.rebuild()
    testing.assert_image_has_color('red')


@pytest.mark.parametrize("rep", ["spheres", "nb_spheres", "sticks", "lines", "nonbonded",
                 "surface"])
def testRecolor(rep):
    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.fragment("gly")
    if rep in ('nb_spheres', 'nonbonded'):
        cmd.unbond("*", "*")
    if rep in ('lines', 'nonbonded'):
        cmd.set("line_width", 5)
    cmd.zoom()
    cmd.color("blue")
    cmd.show_as(rep)
    testing.assert_image_has_color('blue')
    cmd.alter("all", "color = 0x40FF0000")
    testing.assert_image_has_color('blue')
    cmd.recolor()
    testing.assert_image_has_color('red')


def testColor():
    cmd.fragment('ala')
    cmd.color(3)
    colors = set()
    cmd.iterate('all', 'colors.add(color)', space=locals())
    assert sorted(colors) == sorted([3])


def test_color_deep():
    cmd.viewport(100, 70)
    testing.ambient_only()

    cmd.fragment('trp', 'm1')
    cmd.orient('m1')
    cmd.show_as('sticks')
    cmd.show('spheres', 'name C')
    cmd.set('stick_color', 'blue', 'm1')
    cmd.set('stick_color', 'red', 'name CH2+CZ3+CE3+CD2')
    cmd.set('sphere_color', 'yellow', 'name C')

    cmd.color('green')

    img = testing.get_imagearray()
    testing.assert_image_has_color('blue', img)
    testing.assert_image_has_color('red', img)
    testing.assert_image_has_color('yellow', img)
    testing.assert_image_has_not_color('green', img)

    cmd.color_deep('green')

    img = testing.get_imagearray()
    testing.assert_image_has_not_color('blue', img)
    testing.assert_image_has_not_color('red', img)
    testing.assert_image_has_not_color('yellow', img)
    testing.assert_image_has_color('green', img)


def _testSpectrum_setup():
    cmd.pseudoatom('m1', pos=(-2,0,0))
    cmd.pseudoatom('m2', pos=(0,0,0))
    cmd.pseudoatom('m3', pos=(2,0,0))
    cmd.show_as('spheres')
    testing.ambient_only()
    cmd.viewport(40,20)
    cmd.zoom()


def testSpectrum():
    _testSpectrum_setup()
    cmd.spectrum()
    img = testing.get_imagearray()
    testing.assert_image_has_color('blue', img, delta=1)
    testing.assert_image_has_color('red', img)


def testSpectrumany():
    _testSpectrum_setup()
    cmd.spectrum('count', 'red blue')
    img = testing.get_imagearray()
    testing.assert_image_has_color('red', img)
    testing.assert_image_has_color('blue', img)
    testing.assert_image_has_color('0x7f007f', img, delta=30)


def testSetColor():
    _testSpectrum_setup()
    cmd.color('red')
    testing.assert_image_has_color('red')

    # redefine existing name, [0-1] float range
    cmd.set_color('red', [0., 0., 1.])
    cmd.recolor()
    testing.assert_image_has_color('blue')

    # add new name, [0-1] float range
    cmd.set_color('thomas', [0., 1., 0.])
    cmd.color('thomas')
    testing.assert_image_has_color('green')

    # redefine existing (custom) name, [0-255] int range
    cmd.set_color('thomas', [0x00, 0x80, 0x80])
    cmd.recolor()
    testing.assert_image_has_color('0x008080')

    # add new very long name, [0-255] int range
    longname = 'some' + 'very' * 10 + 'longcolorname'
    cmd.set_color(longname, [0xFF, 0xFF, 0x00])
    cmd.color(longname)
    testing.assert_image_has_color('yellow')


def testGetSetVis():
    # which objects are switched on comes back, also inside a closed group
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    cmd.group('g1', 'm2 m3')
    cmd.disable('m1')
    cmd.disable('m3')
    vis = cmd.get_vis()
    cmd.enable('m1')
    cmd.enable('m3')
    cmd.disable('g1')
    assert cmd.get_names('public_objects', enabled_only=1) == ['m1', 'm2', 'm3']
    cmd.set_vis(vis)
    assert cmd.get_names('public_objects', enabled_only=1) == ['m2', 'g1']
    cmd.set_vis({})
    assert cmd.get_names('public_objects', enabled_only=1) == ['m2', 'g1']
