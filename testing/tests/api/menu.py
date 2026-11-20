import pytest
import pymol
from pymol import menu, cmd, testing


def _make_objects(n=2):
    for i, aa in enumerate(['gly', 'ala', 'cys', 'his'][:n], 1):
        cmd.fragment(aa, 'm%d' % i)


def _make_multistate(n=3, name='multi1'):
    cmd.fragment('gly', name)
    for i in range(2, n + 1):
        cmd.create(name, name, 1, n)


def _make_seles(n=1):
    _make_objects(n)
    for i in range(1, n + 1):
        cmd.select('s%i' % i, 'm%d' % i)


def _make_scenes(n=3):
    for i in range(1, n + 1):
        cmd.scene('%03d' % i, 'store')


def _make_cgo(oname):
    from pymol import cgo
    cmd.load_cgo([cgo.STOP], oname)


def _make_map(oname):
    molname = 'm_for_map'
    cmd.fragment('gly', molname)
    cmd.set('gaussian_b_floor', 20)
    cmd.map_new(oname, 'gaussian', 0.5, molname)
    cmd.delete(molname)


def _make_mesh(oname):
    mapname = oname + '_map'
    _make_map(mapname)
    cmd.isomesh(oname, mapname)


def _to_dict(m):
    d = {}
    for (t, key, value) in m:
        if t == 1:
            d[key] = value
    return d


def _get_first_evaluable(m):
    if not isinstance(m, list):
        return m
    for (t, key, value) in m:
        if t == 1:
            m_sub = _get_first_evaluable(value)
            if m_sub:
                return m_sub


def _eval_first(m):
    from pymol import preset, util
    s = _get_first_evaluable(m)
    if not s:
        raise UserWarning('empty menu')
    if isinstance(s, str):
        exec(s)
    else:
        s()


def testAlignToObject():
    _make_objects(3)
    m = menu.align_to_object(cmd, 'm2')
    labels = [x[1] for x in m]
    assert 'm1' in labels
    assert 'm2' not in labels
    assert 'm3' in labels


def testAlignToSele():
    _make_seles(3)
    m = menu.align_to_sele(cmd, 's2')
    labels = [x[1] for x in m]
    assert 's1' in labels
    assert 's2' not in labels
    assert 's3' in labels


def testAllAction():
    _make_objects(3)
    sele = 'all'
    m = menu.all_action(cmd, sele)
    assert m[0] == [2, 'Action:', '']


def testCameraMotion():
    nstate = 4
    nscene = 3
    _make_multistate(nstate)
    _make_scenes(nscene)
    m = menu.camera_motion(cmd)
    d = _to_dict(m)
    dscene = _to_dict(d['store with scene'])
    dstate = _to_dict(d['store with state'])
    assert len(dscene) == nscene
    assert len(dstate) == nstate + 1
    assert 'current' in dstate


def testCgoHide():
    sele = 'cgo1'
    _make_cgo(sele)
    m = menu.cgo_hide(cmd, sele)


def testCgoShow():
    sele = 'cgo1'
    _make_cgo(sele)
    m = menu.cgo_show(cmd, sele)


def testColorramps():
    cmd.ramp_new('r1', 'none')
    cmd.ramp_new('r2', 'none')
    m = menu.colorramps(cmd, '')
    d = _to_dict(m)
    assert sorted(d) == ['r1', 'r2']


def testCopyTo():
    nobj = 3
    _make_objects(nobj)
    sele = 'm1'
    m = menu.copy_to(cmd, sele)
    d = _to_dict(m)
    assert 'new' in d
    assert len(d) == nobj


def testGeneralColor():
    sele = 'cgo1'
    _make_cgo(sele)
    m = menu.general_color(cmd, sele)
    _eval_first(m)


def testGroupAction():
    _make_objects()
    sele = 'g1'
    cmd.group(sele, 'm*')
    m = menu.group_action(cmd, sele)
    d = _to_dict(m)
    assert 'rename group' in d


def testMainMenu():
    m = menu.main_menu(cmd, (0., 0., 0.), (123, 456))


def testMapAction():
    sele = 'map1'
    _make_map(sele)
    m = menu.map_action(cmd, sele)
    _eval_first(m)
    m = menu.map_hide(cmd, sele)
    _eval_first(m)
    m = menu.map_show(cmd, sele)
    _eval_first(m)


def testMeasurementColor():
    _make_objects(1)
    sele = 'd1'
    cmd.distance(sele, 'first all', 'last all')
    m = menu.measurement_color(cmd, sele)
    _eval_first(m)
    m = menu.measurement_hide(cmd, sele)
    _eval_first(m)
    m = menu.measurement_show(cmd, sele)
    _eval_first(m)


def testMeshAction():
    sele = 'mesh1'
    _make_mesh(sele)
    m = menu.mesh_action(cmd, sele)
    _eval_first(m)
    m = menu.mesh_hide(cmd, sele)
    _eval_first(m)
    m = menu.mesh_show(cmd, sele)
    _eval_first(m)
    _testMeshColor(sele)


def _testMeshColor(sele):
    m = menu.mesh_color(cmd, sele)
    _eval_first(m)


def testMolAction():
    _make_objects()
    sele = 'm1'
    m = menu.mol_action(cmd, sele)
    _eval_first(m)


def testMouseConfig():
    m = menu.mouse_config(cmd)
    _eval_first(m)


def testObjMotion():
    _make_objects(1)
    sele = 'm1'
    m = menu.obj_motion(cmd, sele)


def testPickMenu():
    _make_objects(1)
    m = menu.pick_menu(cmd, '/m1////', '(first m1)')


def testPickSele():
    _make_seles(1)
    sele = 's1'
    m = menu.pick_sele(cmd, sele, 'dummytitle')


def testPresets(request):
    sele = 'm1'
    cmd.load(testing.datafile('1rx1.pdb'), sele)
    m = menu.presets(cmd, sele)
    d = _to_dict(m)
    _eval_first(d['technical'])
    # 15: ordered, one solvent row instead of twin rows, glass.
    # 15g, 15h: no "simple"; the looks are the last group of the one list
    labels = [row[1] for row in m if row[0] == 1]
    assert labels == [
        'default', 'classified', 'technical', 'ball and stick',
        'b factor putty', 'pretty', 'publication',
        'glass', 'cartoon wire', 'cartoon spring',
        'illustration', 'ligands',
        'ligand sites', 'protein interface', 'protein-protein interaction',
        'antibody and antigen', 'cartoon transparency',
        'show solvent',
        'theme', 'light', 'floor']
    assert [row[1] for row in m if row[0] == 2] == ['Preset:']
    # 30d: themes, lights and the floor each have a submenu
    def sub(name):
        assert d[name][0][0] == 2  # under a caption
        return [row[1] for row in d[name] if row[0] == 1]
    assert sub('theme') == ['clay', 'blue', 'sage', 'mint', 'night']
    assert sub('light') == [
        'standard light', 'figure', 'soft', 'flat', 'comic', 'sketch',
        'x-ray', 'studio', 'top light', 'soft shadow']
    assert sub('floor') == ['floor', 'floor with mirror image', 'no floor']
    lights = _to_dict(d['light'])
    from pymol import preset
    request.addfinalizer(lambda: setattr(preset, 'solvent', False))
    cmd.do(d['show solvent'], echo=0)
    assert 'hide solvent' in [row[1] for row in menu.presets(cmd, sele)]
    cmd.do(d['glass'], echo=0)
    assert cmd.count_atoms('rep surface') > 0
    request.addfinalizer(lambda: preset.look('default'))
    cmd.do(lights['comic'], echo=0)
    assert cmd.get_setting_int('ray_trace_mode') == 3
    cmd.do(lights['standard light'], echo=0)
    assert cmd.get_setting_int('ray_trace_mode') == 0
    # cartoon transparency lasts until the next preset
    cmd.do(_to_dict(d['cartoon transparency'])['50%'], echo=0)
    assert cmd.get_setting_float('cartoon_transparency', sele) == 0.5
    cmd.do(d['pretty'], echo=0)
    assert cmd.get_setting_float('cartoon_transparency', sele) == 0


def testShades():
    # "shades" under spectrum and under by chain: one color, light to dark
    cmd.load(testing.datafile('1oky-frag.pdb'), 'm1')
    for builder in (menu.spectrum, menu.by_chain):
        rows = _to_dict(_to_dict(builder(cmd, 'm1'))['shades'])
        assert len(rows) == 8
        cmd.color('white')
        cmd.do(rows['\\059marine'], echo=0)
        assert cmd.count_atoms('color white') == 0


def testRampAction():
    sele = 'r1'
    cmd.ramp_new(sele, 'none')
    _testRampColor(sele)
    m = menu.ramp_action(cmd, sele)
    _eval_first(m)


def _testRampColor(sele):
    m = menu.ramp_color(cmd, sele)
    _eval_first(m)


def testSeleAction():
    _make_seles()
    sele = 's1'
    m = menu.sele_action(cmd, sele)
    _eval_first(m)


def testConsolidated():
    # 14c: one builder for objects and groups, one for selections
    _make_seles(1)
    cmd.group('g1', 'm1')
    for name in ('sele_action2', 'test1', 'test2', 'mol_toggle',
                 'simple_show', 'simple_hide'):
        assert not hasattr(menu, name), name

    def labels(m):
        return [row[1] for row in m if row[0] == 1]

    def commands(m):
        return [row[2] for row in m if row[0] == 1 and isinstance(row[2], str)]

    mol = labels(menu.mol_action(cmd, 'm1'))
    assert mol[:2] == ['rename object', 'duplicate object']
    assert len(mol) == 11
    group = labels(menu.group_action(cmd, 'g1'))
    assert group[:2] == ['rename group', 'duplicate group']
    assert len(group) == 14
    more = _to_dict(menu.mol_action(cmd, 'm1'))['more']
    assert 'copy to object' in labels(more)
    assert 'copy to object' not in labels(_to_dict(
        menu.group_action(cmd, 'g1'))['more'])
    full = labels(menu.sele_action(cmd, 's1'))
    picked = labels(menu.sele_action(cmd, 's1', 1))
    assert set(full) - set(picked) == {'drag coordinates', 'clean'}
    # no menu has two rows with the same command
    for m in (menu.mol_action(cmd, 'm1'), more, menu.group_action(cmd, 'g1'),
              menu.sele_action(cmd, 's1'), menu.sele_action(cmd, 's1', 1),
              menu.exclude(cmd, 's1')):
        assert len(commands(m)) == len(set(commands(m)))
    cmd.do(_to_dict(menu.mol_action(cmd, 'm1'))['duplicate object'], echo=0)
    assert cmd.count_atoms('m1_cpy') == cmd.count_atoms('m1')
    cmd.do(_to_dict(menu.mol_action(cmd, 'm1'))['duplicate object'], echo=0)
    assert 'm1_cpy01' in cmd.get_names()
    # every direct command of these menus is valid Python
    for m in (menu.mol_action(cmd, 'm1'), more, menu.group_action(cmd, 'g1'),
              menu.sele_action(cmd, 's1')):
        for command in commands(m):
            compile(command, 'menu', 'exec')


def testShowHide():
    # one list: a representation row shows it; the cartoon row has the
    # styles in its hover menu; the rest is under "more"
    cmd.fab('AAAAAAAA', 'm1', ss=1)
    cmd.show_as('lines')
    show = menu.mol_show(cmd, 'm1')
    hide = _to_dict(menu.mol_hide(cmd, 'm1'))
    rows = {row[1].strip(): row for row in show if row[0] == 1}
    assert 'as' not in rows and 'valence' not in rows
    assert list(rows)[-2:] == ['hydrogens', 'more']
    assert len(rows) == 15 and len(hide) == 17
    for more in (rows['more'][2], hide['more']):
        assert {'cell', 'valence', 'flag ignore'} <= set(_to_dict(more))
    for menu_ in (show, menu.mol_hide(cmd, 'm1'), menu.mol_as(cmd, 'm1')):
        for row in menu_:
            for command in row[2:]:
                if isinstance(command, str):
                    compile(command, 'menu', 'exec')

    # only the cartoon row has a submenu
    assert [name for name, row in rows.items() if len(row) > 3] == ['cartoon']
    cmd.do(rows['sticks'][2], echo=0)
    assert cmd.count_atoms('rep sticks') and cmd.count_atoms('rep lines')
    cmd.hide('lines')

    # hydrogens come back the way their neighbors are drawn
    cmd.do(hide['hydrogens'][1][2], echo=0)
    assert not cmd.count_atoms('hydro & rep sticks')
    cmd.do(_to_dict(rows['hydrogens'][2])['polar'], echo=0)
    assert cmd.count_atoms('hydro & rep sticks') == cmd.count_atoms(
        'hydro & !(elem C extend 1)')
    cmd.do(_to_dict(rows['hydrogens'][2])['all'], echo=0)
    assert cmd.count_atoms('hydro & rep sticks') == cmd.count_atoms('hydro')
    assert not cmd.count_atoms('rep lines | rep spheres')

    # cartoon: the row is "default", the hover has the styles
    styles = rows['cartoon'][2]
    assert [row[1] for row in styles] == ['default', 'wire', 'spring']
    assert rows['cartoon'][3] == styles[0][2]

    def style():
        types = set()
        cmd.iterate('m1 & name CA', 'types.add(cartoon)', space={'types': types})
        return (types, cmd.get_setting_int('cartoon_debug'),
                cmd.get('cartoon_tube_radius', 'm1'))

    default = style()
    cmd.do(styles[2][2], echo=0)
    assert style()[0] == {4} and float(style()[2]) == pytest.approx(0.8)
    assert cmd.count_atoms('rep cartoon')
    cmd.do(styles[1][2], echo=0)
    assert style()[1] == 3 and style()[2] == default[2]
    cmd.do(rows['cartoon'][3], echo=0)
    assert style() == default
    assert cmd.count_atoms('rep sticks')  # show, not "as"


def testExclude():
    cmd.fab('AG', 'm1')
    cmd.pseudoatom('m1', resn='ZN', elem='Zn', hetatm=1)
    for label, left in (('polymer', 'not polymer'), ('inorganic', 'not inorganic')):
        cmd.select('s1', 'm1')
        cmd.do(_to_dict(menu.exclude(cmd, 's1'))[label], echo=0)
        assert cmd.count_atoms('s1') == cmd.count_atoms('m1 and ' + left)
        assert cmd.count_atoms('s1') < cmd.count_atoms('m1')
        assert cmd.count_atoms('s1') > 0


def testNoViewRows():
    # zoom, orient, center, origin: toolbar and double click, not menus
    _make_seles(1)
    cmd.group('g1', 'm1')
    for m in [
        menu.all_action(cmd, 'all'),
        menu.mol_action(cmd, 'm1'),
        menu.group_action(cmd, 'g1'),
        menu.sele_action(cmd, 's1'),
        menu.main_menu(cmd, (0., 0., 0.), (0, 0)),
        menu.all_option(cmd, 'all'),
        menu.pick_sele(cmd, 's1', ''),
        menu.pick_option(cmd, 'm1', ''),
        menu.seq_option(cmd, 'm1', '/m1/'),
    ]:
        labels = {row[1].split(' ')[0] for row in m}
        assert not labels & {'zoom', 'orient', 'center', 'origin'}


def testSeqOption():
    _make_objects(1)
    sele = '_seeker'
    cmd.select(sele, 'm1')
    m = menu.seq_option(cmd, sele, '/m1////strip')
    _eval_first(m)


def testSimpleAction():
    sele = 'cgo1'
    _make_cgo(sele)
    m = menu.simple_action(cmd, sele)


def testSliceAction():
    sele = 'slice1'
    mapname = 'map1'
    _make_map(mapname)
    cmd.slice_new(sele, mapname)
    cmd.ramp_new('r2', mapname)
    m = menu.slice_color(cmd, sele)
    _eval_first(m)
    m = menu.slice_hide(cmd, sele)
    _eval_first(m)
    m = menu.slice_show(cmd, sele)
    _eval_first(m)
    m = menu.slice_action(cmd, sele)
    _eval_first(m)


def testSurfaceAction():
    sele = 'surf1'
    mapname = 'map1'
    _make_map(mapname)
    cmd.isosurface(sele, mapname)
    m = menu.surface_action(cmd, sele)
    _eval_first(m)
    m = menu.surface_hide(cmd, sele)
    _eval_first(m)
    m = menu.surface_show(cmd, sele)
    _eval_first(m)


def testVacuum():
    cmd.fab('ACD', 'm1')
    m = menu.vacuum(cmd, 'm1')
    _eval_first(m)


def testVolColor():
    sele = 'vol1'
    mapname = 'map1'
    _make_map(mapname)
    cmd.volume(sele, mapname)
    m = menu.vol_color(cmd, sele)
    # self._eval_first(m)
    m = menu.volume_hide(cmd, sele)
    _eval_first(m)
    m = menu.volume_show(cmd, sele)
    _eval_first(m)
