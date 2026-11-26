
import pytest
from pymol import cmd, testing, stored, preset


def _assertSimpleReps():
    assert cmd.count_atoms('rep cartoon') == 0
    assert cmd.count_atoms('rep ribbon & guide') == cmd.count_atoms('guide')
    assert cmd.count_atoms('rep sticks & organic') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep nonbonded & solvent') == cmd.count_atoms('solvent')


def _assertPrettyReps():
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.count_atoms('rep ribbon') == 0
    # 34c: ligands are ball_and_stick, not sticks
    assert cmd.count_atoms('rep ball_and_stick & organic') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep sticks & organic') == 0
    assert cmd.count_atoms('rep nonbonded') == 0
    assert cmd.count_atoms('rep nonbonded') == 0


def testSimple():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.simple('all')
    _assertSimpleReps()


def _menuRows(rows, path=''):
    """(label, command) of every row of a menu and of its submenus; a row
    of a submenu is labelled "submenu > row"."""
    for row in rows:
        if row[0] == 1 and isinstance(row[2], str):
            yield path + row[1], row[2]
        elif row[0] == 1:
            yield from _menuRows(row[2], path + row[1] + ' > ')


def testKeepsCartoonAndSurfaceColors(request):
    # 15l, 30d: no row of the menu colors the cartoon, of a protein (guide
    # atoms) or of a nucleic acid (P and the bases), and none colors a
    # surface. Two exceptions. The color themes: coloring is what they
    # are for (2026-11-20, question 32); test_themes has them. The two
    # presets for complexes: the surface is orange where chains touch,
    # and only there.
    from pymol import menu
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.fab('ACDEFGHIK', 'pep', chain='B')
    cmd.load(testing.datafile('1bna.cif'), 'dna')
    cmd.color('yellow')
    yellow, orange = 6, cmd.get_color_index('orange')
    request.addfinalizer(cmd.reinitialize)  # light, background, the floor
    request.addfinalizer(lambda: cmd.stage('off'))
    request.addfinalizer(lambda: setattr(preset, 'solvent', False))

    def surface():
        # the color a surface is drawn in: its own, else the atom's. Not
        # the nitrogen that is all there is of the last residue of 1oky:
        # it has no carbon to take a color from. Not the ligand and the
        # water of "ligand sites": flagged "ignore" (25), they have no
        # surface.
        stored.drawn = set()
        cmd.iterate('rep surface & byres elem C & !flag 25', 'stored.drawn.add('
                    'color if s.surface_color in (None, -1) else s.surface_color)')
        return stored.drawn

    ran = surfaces = 0
    for label, command in _menuRows(menu.presets(cmd, 'all')):
        if label.startswith('theme > '):
            continue
        before = surface()
        cmd.do(command, echo=0)
        assert _colors('guide | (dna & polymer)') == {yellow}, label
        if label in ('protein-protein interaction', 'antibody and antigen'):
            assert surface() == {yellow, orange}, label  # not the whole surface
        elif 'from_menu' in command:  # a preset: it draws everything anew
            assert surface() <= {yellow}, label
        else:  # transparency, solvent, a light, the floor: what was there
            assert surface() == before, label
        for name in cmd.get_names('public_objects'):  # nor through the object
            assert cmd.get('surface_color', name) == 'default', label
        ran += 1
        surfaces += bool(surface())
    assert ran > 30 and surfaces >= 8


def _surfaceColors(selection):
    stored.surface = set()
    cmd.iterate(selection, 'stored.surface.add(s.surface_color)')
    return stored.surface


def testInteraction():
    # two chains in two objects, built on top of each other: all touch;
    # a third far away touches nothing
    index = cmd.get_color_index
    cmd.fab('ACDEFGHIK', 'one', chain='A')
    cmd.fab('LMNPQRSTV', 'two', chain='A')
    cmd.fab('ACDEFGHIK', 'far', chain='A')
    cmd.translate([100, 0, 0], 'far')
    before = _colors('all')
    preset.interaction('all')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep cartoon | rep sticks') == 0
    # 30d: the surface is orange where chains touch and has no color of
    # its own elsewhere; the atoms keep theirs
    assert index('orange') in _surfaceColors('one | two')
    assert _surfaceColors('(one | two) & elem C') <= {None, index('orange')}
    assert _surfaceColors('far & elem C') == {None}
    assert _surfaceColors('far & elem O') == _colors('far & elem C')
    assert _colors('all') == before
    assert '_p_tmp' not in cmd.get_names('all')
    # the next preset undoes the surface and its colors
    preset.pretty('all')
    assert cmd.count_atoms('rep surface') == 0
    assert _surfaceColors('all') == {None}


def _colors(selection):
    stored.colors = set()
    cmd.iterate(selection, 'stored.colors.add(color)')
    return stored.colors


def testAntibody():
    index = cmd.get_color_index
    # found by the start of framework 2, whatever the chains are called
    cmd.fab('AAWVRQAPGKGLEW', 'm', chain='X')
    cmd.fab('AAWYQQKPGKAPKL', 'm2', chain='Y')
    cmd.fab('ACDEFGHIKLMNPQ', 'ag', chain='Z')
    before = _colors('guide')
    preset.antibody('all')
    assert _colors('guide') == before  # 15l: the cartoon keeps its colors
    # the antigen: a surface in its own colors with the epitope in orange
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('ag')
    assert cmd.count_atoms('rep cartoon') == cmd.count_atoms('m | m2')
    assert _surfaceColors('ag & elem C') <= {None, index('orange')}
    assert index('orange') in _surfaceColors('ag')
    assert _surfaceColors('m | m2') == {None}
    assert cmd.count_atoms('rep sticks & (m | m2)') > 0

    # without the motif: the chains named H and L
    cmd.delete('all')
    cmd.fab('ACDEFGHIK', 'h', chain='H')
    cmd.fab('ACDEFGHIK', 'l', chain='L')
    cmd.fab('ACDEFGHIK', 'ag', chain='A')
    preset.antibody('all')
    assert cmd.count_atoms('rep cartoon') == cmd.count_atoms('h | l')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('ag')

    # no antibody at all: the interaction picture
    cmd.delete('all')
    cmd.fab('ACDEFGHIK', 'pa', chain='A')
    cmd.fab('ACDEFGHIK', 'pb', chain='B')
    preset.antibody('all')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('all')
    assert '_p_tmp' not in cmd.get_names('all')


def testEnabledOnly(request):
    # the toolbar applies a preset to "enabled": a hidden object is left
    from pymol import menu
    cmd.fab('ACDEFGHIK', 'shown')
    cmd.fab('ACDEFGHIK', 'hidden')
    cmd.disable('hidden')

    def reps(name):
        return [cmd.count_atoms('%s & rep %s' % (name, r))
                for r in ('lines', 'sticks', 'cartoon', 'surface', 'spheres')]

    before = reps('hidden')
    request.addfinalizer(cmd.reinitialize)  # light, background, the floor
    request.addfinalizer(lambda: cmd.stage('off'))
    request.addfinalizer(lambda: setattr(preset, 'solvent', False))  # the solvent row
    for label, command in _menuRows(menu.presets(cmd, 'enabled')):
        cmd.do(command, echo=0)
        assert reps('hidden') == before, label
    rows = dict((r[1], r[2]) for r in menu.cartoon_transparency(cmd, 'enabled'))
    cmd.do(rows['50%'], echo=0)
    assert cmd.get_setting_float('cartoon_transparency', 'shown') == 0.5
    assert cmd.get_setting_float('cartoon_transparency', 'hidden') == 0


def testTechnical():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.technical('all')
    # cartoon, not ribbon: only "simple" keeps the ribbon
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.count_atoms('rep ribbon') == 0
    assert cmd.count_atoms('rep nonbonded & solvent') == cmd.count_atoms('solvent')
    assert '1oky_pol_conts' in cmd.get_names('all')


def testPublication():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.publication('all')
    _assertPrettyReps()
    assert cmd.get_setting_boolean('cartoon_smooth_loops', '1oky')
    assert cmd.get_setting_boolean('cartoon_fancy_helices', '1oky')


def testPublicationGreen():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.publication_green('all')
    _assertPrettyReps()
    assert cmd.get_setting_boolean('cartoon_fancy_helices', '1oky')
    stored.colors = set()
    cmd.iterate('guide', 'stored.colors.add(color)')
    assert len(stored.colors) > 10  # shades, not one color
    for color in stored.colors:  # every one a green
        r, g, b = cmd.get_color_tuple(color)
        assert g > r and g > b, (r, g, b)


def testPretty():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.pretty('all')
    _assertPrettyReps()
    assert not cmd.get_setting_boolean('cartoon_smooth_loops', '1oky')
    assert not cmd.get_setting_boolean('cartoon_fancy_helices', '1oky')


def testLigands():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.ligands('all')
    assert cmd.count_atoms('rep cartoon') > 0
    assert cmd.count_atoms('rep ribbon') == 0
    # the ligand as balls and thin sticks
    # 34c: ball_and_stick; no sphere or stick is shown, no setting written
    assert cmd.count_atoms('rep ball_and_stick') == cmd.count_atoms(preset.lig_sele)
    assert cmd.count_atoms('rep spheres') == 0
    assert cmd.count_atoms('rep sticks & organic') == 0
    stored.scales = set()
    cmd.iterate('organic', 'stored.scales.add(s.sphere_scale)')
    assert stored.scales == {1.0}
    solvent_nb_count = cmd.count_atoms('rep nonbonded & solvent')
    assert solvent_nb_count > 0
    assert solvent_nb_count < cmd.count_atoms('solvent')
    assert cmd.count_atoms('rep lines & polymer') > 0
    assert cmd.count_atoms('(polymer be. 10 of hetatm) and rep lines') == 0
    assert '1oky_pol_conts' in cmd.get_names('all')
    # the next preset undoes the balls
    preset.pretty('all')
    assert cmd.count_atoms('rep spheres') == 0
    assert cmd.count_atoms('rep ball_and_stick & organic') == cmd.count_atoms('organic')


def testDefault():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.color("yellow", "1oky") # color index 6
    preset.default('1oky')
    assert cmd.count_atoms('rep cartoon') == 0
    assert cmd.count_atoms('rep ribbon') == 0
    assert cmd.count_atoms('rep sticks') == 0
    assert cmd.count_atoms('rep spheres') == 0
    assert cmd.count_atoms('rep lines') == cmd.count_atoms()
    assert cmd.count_atoms('rep nonbonded & solvent') == cmd.count_atoms('solvent')
    # 30d: the carbons keep the color they have, the rest is by element
    color_set = set()
    cmd.iterate('elem C', 'color_set.add(color)', space=locals())
    assert sorted(color_set) == sorted([6])
    assert len(_colors('not elem C')) > 2
    cmd.color('blue', 'elem C and resi 100-120')  # not the object's color
    preset.default('1oky')
    assert _colors('elem C and resi 100-120') == {cmd.get_color_index('blue')}


def testGlass():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.glass('all')
    # 30d: no white; the color of the carbons, also over the oxygens
    assert cmd.get('surface_color', '1oky') == 'default'
    carbons = _colors('polymer & elem C')
    assert len(carbons) == 1 and _surfaceColors('polymer & elem O') == carbons
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.count_atoms('rep ball_and_stick & organic') == cmd.count_atoms('organic')
    assert cmd.get_setting_float('ray_transparency_oblique') == 1
    # the next preset undoes all of it
    preset.simple('all')
    assert cmd.count_atoms('rep surface') == 0
    assert cmd.get_setting_float('ray_transparency_oblique') == 0
    assert cmd.get('surface_color', '1oky') == 'default'


def testEffects(request):
    """15e: balls in glass, cylinders, and the shade of the soft look."""
    request.addfinalizer(lambda: preset.look('default'))
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.balls_in_glass('all')
    assert cmd.count_atoms('rep ball_and_stick') == cmd.count_atoms()
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.get_setting_float('ray_transparency_oblique_power') == 20
    assert cmd.get('surface_color', '1oky') == 'default'  # no recoloring
    preset.cylinders('all')
    assert cmd.count_atoms('rep surface') == 0
    assert cmd.get_setting_float('ray_transparency_oblique_power') == 4
    assert cmd.get_setting_int('cartoon_cylindrical_helices', '1oky') == 1
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    # the soft look shades the pockets of a surface, but not a glass one
    preset.look('soft')
    assert cmd.get_setting_int('ambient_occlusion_mode') == 1
    preset.glass('all')
    assert cmd.get_setting_int('cartoon_cylindrical_helices', '1oky') == 0
    assert cmd.get_setting_int('ambient_occlusion_mode', '1oky') == 0
    preset.pretty('all')  # an opaque surface shown afterwards is shaded
    assert cmd.get_setting_int('ambient_occlusion_mode', '1oky') == 1
    preset.look('default')
    assert cmd.get_setting_int('ambient_occlusion_mode') == 0
    assert cmd.get_setting_float('ambient_occlusion_scale') == 25
    # fog on top of a look that has none
    preset.look('figure')
    assert not cmd.get_setting_int('depth_cue')
    preset.depth_fog(1)
    assert cmd.get_setting_int('depth_cue')
    assert cmd.get_setting_int('ray_trace_mode') == 1


def testSurfaceLooks(request):
    """25b: the rows "surface look" show the protein as a surface in one
    material. The next preset takes all of it back; a row of the light
    menu replaces the light and leaves the surface."""
    from pymol import menu
    request.addfinalizer(cmd.reinitialize)  # the light
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.set('transparency', 0.2)  # the user's, of the whole scene: it stays
    rows = dict(_menuRows(menu.presets(cmd, '1oky')))
    names = [label[15:] for label in rows if label.startswith('surface look > ')]
    assert names == list(preset.SURFACES) == ['glossy', 'candy glass', 'frosted', 'clay']

    def see_through():  # of the atoms, else that of the scene
        stored.found = set()
        cmd.iterate('polymer', 'stored.found.add(round(s.transparency, 2))')
        return stored.found

    for name in names:
        cmd.do(rows['surface look > ' + name], echo=0)
        light, shape, transparency = preset.SURFACES[name]
        assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer'), name
        assert cmd.count_atoms('rep cartoon') == 0, name
        assert cmd.count_atoms('rep ball_and_stick & organic') == cmd.count_atoms('organic')
        for key, value in light.items():
            assert cmd.get_setting_float(key) == pytest.approx(value), (name, key)
        # round is the grid surface with a large probe, on the object only
        round_ = name != 'glossy'
        assert cmd.get_setting_int('surface_type', '1oky') == (7 if round_ else 0), name
        assert cmd.get_setting_float('solvent_radius', '1oky') == pytest.approx(
            3.0 if round_ else 1.4), name
        assert cmd.get_setting_int('surface_type') == 0
        assert see_through() == {transparency or 0.2}, name
        assert cmd.get_setting_int('ray_transparency_oblique') == bool(transparency)
        assert cmd.get_setting_float('transparency') == pytest.approx(0.2)
    assert cmd.get_setting_int('ambient_occlusion_mode') == 1  # clay, the last

    preset.look('studio')  # another light on the same clay
    assert cmd.get_setting_int('ambient_occlusion_mode') == 0
    assert cmd.get_setting_int('light_count') == 4
    assert cmd.get_setting_int('surface_type', '1oky') == 7
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')

    preset.surface('1oky', 'candy glass')
    preset.pretty('1oky')  # the next preset: nothing of it is left
    assert cmd.count_atoms('rep surface') == 0 and see_through() == {0.2}
    assert cmd.get_setting_int('surface_type', '1oky') == 0
    assert cmd.get_setting_float('solvent_radius', '1oky') == pytest.approx(1.4)
    assert cmd.get_setting_float('spec_reflect') == -1  # the default light
    assert cmd.get_setting_int('two_sided_lighting') == 0
    assert cmd.get_setting_int('ray_transparency_oblique') == 0
    assert cmd.get_setting_float('transparency') == pytest.approx(0.2)


def testReferenceRecipes(request):
    """15m: space filling, illustrated atoms, licorice and bond shell, and
    "contour cartoon", the row that runs "illustration". They keep colors,
    camera and background and leave a hidden object alone; the next preset
    takes all of it back; a scene and Undo bring the picture before."""
    from pymol import menu
    request.addfinalizer(cmd.reinitialize)  # the light, the steps of undo
    cmd.load(testing.datafile('1oky.pdb.gz'), 'm')
    cmd.fab('ACDEFG', 'hidden')
    cmd.disable('hidden')
    cmd.bg_color('grey30')
    cmd.set('sphere_scale', 0.8, 'm')  # the user's sizes stay
    rows = dict(_menuRows(menu.presets(cmd, 'enabled')))
    assert 'preset.from_menu("illustration"' in rows['contour cartoon']
    assert 'illustration' not in rows
    count = cmd.count_atoms
    n, lig, polymer = count('m & !solvent'), count('m & organic'), count('m & polymer')

    def state():
        return (_colors('all'), cmd.get_view(), cmd.get('bg_rgb'),
                count('hidden & rep lines'), count('hidden & !rep lines & visible'),
                cmd.get_setting_float('sphere_scale', 'm'))

    before, spheres = state(), count('m & rep spheres')
    cmd.scene('start', 'store')
    reps = {  # what is drawn, and of how many atoms
        'space filling': {'spheres': n},
        'illustrated atoms': {'spheres': n},
        'licorice': {'sticks': n},
        'bond shell': {'lines': polymer, 'surface': polymer, 'ball_and_stick': lig,
                       'sticks': count('m & inorganic')},  # the sulfates
    }
    for label, shown in reps.items():
        cmd.do(rows[label], echo=0)
        for rep in ('spheres', 'sticks', 'lines', 'surface', 'ball_and_stick', 'cartoon'):
            assert count('m & rep ' + rep) == shown.get(rep, 0), (label, rep)
        assert count('m & solvent & visible') == 0, label
        assert state() == before, label
        # only "illustrated atoms" picks a light: flat colors in outlines
        flat = label == 'illustrated atoms'
        assert cmd.get_setting_int('ray_trace_mode') == flat, label
        assert cmd.get_setting_float('ambient') == pytest.approx(1 if flat else 0.14), label
    stored.seen = set()
    cmd.iterate('m & polymer', 'stored.seen.add(round(s.transparency, 2))')
    assert stored.seen == {0.5}  # of the shell, on its atoms

    # illustrated atoms -> pretty -> default: light and spheres are gone
    cmd.do(rows['illustrated atoms'], echo=0)
    cmd.do(rows['pretty'], echo=0)
    assert cmd.get_setting_int('ray_trace_mode') == 0 and count('rep spheres') == 0
    cmd.do(rows['default'], echo=0)
    assert count('m & rep lines') == count('m')
    # a light picked by hand stays through the recipes that pick none
    cmd.do(rows['light > studio'], echo=0)
    cmd.do(rows['space filling'], echo=0)
    assert cmd.get_setting_int('light_count') == 4
    # the light of the surface look "glossy" alone: nothing is shown or hidden
    cmd.do(rows['light > glossy (light only)'], echo=0)
    assert cmd.get_setting_float('spec_power') == 300
    assert count('m & rep spheres') == n and count('rep surface') == 0

    # one step of Undo per row, and the scene of the start
    cmd.do(rows['bond shell'], echo=0)
    cmd.undo()
    assert count('m & rep spheres') == n and count('rep surface') == 0
    cmd.scene('start', 'recall', animate=0)
    assert count('m & rep spheres') == spheres and state() == before
    assert cmd.get_setting_float('spec_power') == -1


def testWire():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.wire('all')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.get_setting_int('cartoon_debug') == 3
    preset.pretty('all')  # the next preset makes the cartoon solid again
    assert cmd.get_setting_int('cartoon_debug') == 0


def testSpring():
    cmd.fab('ACDEFGHIK', 'm1', ss=1)
    cmd.fab('ACDEFGHIK', 'm2', ss=1)
    preset.spring('all')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    stored.types = set()
    cmd.iterate('guide', 'stored.types.add(cartoon)')
    assert stored.types == {4}  # tube
    for name in ('m1', 'm2'):
        assert cmd.get_setting_float('cartoon_tube_radius', name) == pytest.approx(0.8)
    preset.pretty('all')  # the next preset undoes it
    stored.types = set()
    cmd.iterate('guide', 'stored.types.add(cartoon)')
    assert 4 not in stored.types
    assert cmd.get_setting_float('cartoon_tube_radius', 'm1') == pytest.approx(0.5)


def testIllustration(request):
    cmd.load(testing.datafile('1oky.pdb.gz'))
    request.addfinalizer(lambda: preset.look('default'))
    preset.illustration('all')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    # it picks the look flat: true colors, outlines on transparent things
    assert cmd.get_setting_int('ray_trace_mode') == 1
    assert cmd.get_setting_float('ray_trace_trans_cutoff') == 1
    preset.look('default')
    assert cmd.get_setting_float('ray_trace_trans_cutoff') == pytest.approx(0.05, abs=5e-8)


def testIllustrationLight(request):
    # the flat light of "illustration" ends with the next preset; a
    # look that was picked as such stays
    cmd.fab('ACDEFG', 'm1')
    request.addfinalizer(lambda: preset.look('default'))
    preset.illustration('m1')
    assert cmd.get_setting_float('ambient') == 1
    preset.pretty('m1')
    assert cmd.get_setting_float('ambient') == pytest.approx(0.14, abs=5e-8)
    assert cmd.get_setting_int('ray_trace_mode') == 0
    preset.illustration('m1')
    preset.look('flat')
    preset.pretty('m1')
    assert cmd.get_setting_float('ambient') == 1


def testMenuSolvent(request):
    # one solvent row in the menu instead of "(with solvent)" twins
    cmd.load(testing.datafile('1oky.pdb.gz'))
    request.addfinalizer(lambda: setattr(preset, 'solvent', False))
    n_solvent = cmd.count_atoms('solvent')
    for name in ('simple', 'technical', 'ball_and_stick', 'b_factor_putty',
                 'pretty_solv', 'pub_solv', 'glass', 'wire', 'ligands',
                 'ligand_sites', 'ligand_cartoon', 'interface', 'classified'):
        preset.from_menu(name, 'all')
        assert cmd.count_atoms('solvent & visible') == 0, name
        assert cmd.count_atoms('visible') > 0, name
    assert '_p_tmp' not in cmd.get_names('all')
    preset.from_menu('default', 'all')
    assert cmd.count_atoms('solvent & visible') == n_solvent
    preset.from_menu('pretty_solv', 'all')
    preset.show_solvent(1, 'all')
    assert cmd.count_atoms('solvent & rep nb_spheres') == n_solvent
    for name in ('simple', 'pretty_solv', 'pub_solv'):
        preset.from_menu(name, 'all')
        assert cmd.count_atoms('solvent & visible') == n_solvent, name
    preset.show_solvent(0, 'all')
    assert cmd.count_atoms('solvent & visible') == 0


def testLook(request):
    # 15g: no look touches the background or its transparency
    cmd.bg_color('grey50')
    cmd.set('ray_opaque_background', 0)
    request.addfinalizer(cmd.reinitialize)
    for name in preset.LOOKS:  # every key is a setting
        preset.look(name)
        assert cmd.get('bg_rgb') == 'grey50', name
        assert cmd.get_setting_int('ray_opaque_background') == 0, name
        # the outline contrasts with whatever the background is
        assert cmd.get('ray_trace_color') == 'front', name
    preset.look('figure')
    assert cmd.get_setting_int('ray_trace_mode') == 1
    preset.look('comic')
    assert cmd.get_setting_int('ray_trace_mode') == 3
    preset.look('sketch')
    assert cmd.get_setting_int('ray_trace_mode') == 2
    assert cmd.get_setting_int('antialias') == 2
    preset.look('x-ray')  # a look replaces the one before it
    assert cmd.get_setting_int('ray_trace_mode') == 0
    assert cmd.get_setting_float('ambient') == 1
    preset.look('default')
    assert cmd.get_setting_float('ambient') == pytest.approx(0.14, abs=5e-8)
    assert cmd.get_setting_int('light_count') == 2


def test_themes(request):
    """A theme colors protein and ligand carbons and sets a two-color
    background; representations and the light stay."""
    saved = [cmd.get(k) for k in ("bg_rgb", "bg_rgb_top", "bg_rgb_bottom", "bg_gradient")]
    request.addfinalizer(lambda: [cmd.set(k, v) for k, v in zip(("bg_rgb", "bg_rgb_top", "bg_rgb_bottom", "bg_gradient"), saved)])
    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.fragment("ala", "other")
    reps = cmd.count_atoms("rep lines")
    light = cmd.get("ambient")
    other = cmd.get_color_tuple(cmd.get_object_color_index("other"))

    def color_of(selection):
        found = set()
        cmd.iterate(selection, "found.add(color)", space={"found": found})
        return {tuple(round(c * 255) for c in cmd.get_color_tuple(i)) for i in found}

    for name, (protein, ligand, top, bottom) in preset.THEMES.items():
        preset.theme(name, "m")
        rgb = lambda text: tuple(int(text[i:i + 2], 16) for i in (2, 4, 6))
        assert color_of("m and polymer") == {rgb(protein)}
        assert color_of("m and organic and elem C") == {rgb(ligand)}
        assert len(color_of("m and resn STU and not elem C")) > 1  # N and O keep theirs
        assert cmd.get_setting_int("bg_gradient") == 1
        assert tuple(round(c * 255) for c in cmd.get_color_tuple(cmd.get("bg_rgb_bottom"))) == rgb(bottom)
    assert cmd.get_color_tuple(cmd.get_object_color_index("other")) == other  # not in the selection
    assert cmd.count_atoms("rep lines") == reps and cmd.get("ambient") == light


LIGAND_PRESETS = (
    'technical', 'pretty', 'pretty_solv', 'publication', 'pub_solv',
    'publication_green', 'glass', 'wire', 'spring', 'illustration',
    'ligands', 'ligand_sites', 'ligand_sites_hq', 'ligand_sites_trans',
    'ligand_sites_trans_hq', 'ligand_sites_mesh', 'ligand_sites_dots',
    'ligand_cartoon', 'classified', 'interaction', 'surface', 'bond_shell',
)


def _complex():
    """A protein with a ligand, water and an ion, and sphere and stick
    settings of the user's on the ligand."""
    cmd.load(testing.datafile('1oky.pdb.gz'), 'm')
    cmd.pseudoatom('m', pos=[20, 20, 20], elem='Zn', name='ZN', resn='ZN',
                   resi='900', chain='A', hetatm=1)
    cmd.set('sphere_scale', 0.77, 'organic')
    cmd.set_bond('stick_radius', 0.33, 'organic')
    cmd.set_bond('stick_color', 'red', 'organic')


def _user_settings():
    stored.scales = set()
    cmd.iterate('organic', 'stored.scales.add(round(s.sphere_scale, 2))')
    radii = {round(v, 2) for _, bonds in cmd.get_bond('stick_radius', 'organic', quiet=1)
             for _, _, v in bonds}
    colors = {v for _, bonds in cmd.get_bond('stick_color', 'organic', quiet=1)
              for _, _, v in bonds}
    return stored.scales, radii, colors


@pytest.mark.parametrize('name', LIGAND_PRESETS)
def testLigandsAreBallAndStick(name):
    """34c: every preset that draws ligands draws them as ball_and_stick,
    writes no sphere or stick setting and keeps the user's, leaves the ion
    and the water to their own representations and the protein its colors."""
    _complex()
    user = _user_settings()
    assert user[0] == {0.77} and user[1] == {0.33} and len(user[2]) == 1
    carbons = _colors('polymer & guide')
    getattr(preset, name)('m')
    n_organic = cmd.count_atoms('organic')
    assert n_organic and cmd.count_atoms('organic & rep ball_and_stick') == n_organic
    assert cmd.count_atoms('organic & (rep sticks | rep spheres)') == 0
    # (a modified residue, SEP here, counts as a ligand, as it did for sticks)
    assert cmd.count_atoms('(resn ZN | solvent | (polymer & !hetatm)) & rep ball_and_stick') == 0
    assert _user_settings() == user
    if name != 'publication_green':  # that one colors the chains
        assert _colors('polymer & guide') == carbons
    # nothing of the new representation is styled by a preset
    stored.own = set()
    cmd.iterate('all', 'stored.own.add((s.ball_and_stick_scale, s.ball_and_stick_color, '
                's.ball_and_stick_bond_radius))')
    assert len(stored.own) == 1
    assert not {s[0] for s in cmd.get_object_settings('m') or ()} & {
        'ball_and_stick_scale', 'ball_and_stick_color', 'ball_and_stick_bond_radius',
        'sphere_scale', 'stick_radius', 'stick_color'}


def testBallAndStickPreset():
    """The preset "ball and stick" uses the representation; its modes."""
    _complex()
    user = _user_settings()
    preset.ball_and_stick('m')  # mode 1: the colors of the atoms
    assert cmd.count_atoms('rep ball_and_stick') == cmd.count_atoms('m')
    assert cmd.count_atoms('rep sticks | rep spheres') == 0
    assert _user_settings() == user
    stored.colors = set()
    cmd.iterate('all', 'stored.colors.add(s.ball_and_stick_color)')
    assert stored.colors == {None}
    preset.ball_and_stick('m', mode=2)  # by element, on the atoms
    stored.colors = set()
    cmd.iterate('all', 'stored.colors.add(s.ball_and_stick_color)')
    assert stored.colors == {-4}  # "atomic"
    preset.ball_and_stick('m', 1)  # and back
    stored.colors = set()
    cmd.iterate('all', 'stored.colors.add(s.ball_and_stick_color)')
    assert stored.colors == {None}
    preset.ball_and_stick('m', mode=7)  # no such mode: nothing shown, as before
    assert cmd.count_atoms('visible') == 0


def testSceneBeforeAPreset():
    """A scene stored before a preset brings the old ligand style back."""
    _complex()
    cmd.hide('spheres')  # of the ion
    cmd.show_as('sticks', 'organic')
    cmd.show('spheres', 'organic & elem N')
    cmd.scene('mine', 'store')
    preset.pretty('m')
    assert cmd.count_atoms('organic & rep ball_and_stick') == cmd.count_atoms('organic')
    cmd.scene('mine', 'recall', animate=0)
    assert cmd.count_atoms('organic & rep sticks') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep ball_and_stick') == 0
    assert cmd.count_atoms('rep spheres') == cmd.count_atoms('organic & elem N')
    assert _user_settings() == ({0.77}, {0.33}, _user_settings()[2])
