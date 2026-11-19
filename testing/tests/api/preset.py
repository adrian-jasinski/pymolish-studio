
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
    assert cmd.count_atoms('rep sticks & organic') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep nonbonded') == 0
    assert cmd.count_atoms('rep nonbonded') == 0


def testSimple():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.simple('all')
    _assertSimpleReps()


def _guideColors():
    stored.colors = set()
    cmd.iterate('guide', 'stored.colors.add(color)')
    return stored.colors


def testKeepsProteinColors():
    # 15h: the working presets leave the cartoon color alone
    cmd.load(testing.datafile('1oky.pdb.gz'))
    cmd.color('yellow', 'polymer & elem C')
    for name in ('technical', 'ligands', 'ligand_sites', 'ligand_cartoon',
                 'ball_and_stick', 'classified'):
        getattr(preset, name)('all')
        assert _guideColors() == {6}, name
    preset.pretty('all')  # a picture preset still colors
    assert len(_guideColors()) > 10


def testInteraction():
    # two chains in two objects, built on top of each other: all touch
    cmd.fab('ACDEFGHIK', 'one', chain='A')
    cmd.fab('LMNPQRSTV', 'two', chain='A')
    preset.interaction('all')
    assert cmd.count_atoms('rep cartoon') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep sticks') > 0
    # one color per chain and object, the same for its surface
    colors = {name: _colors(name + ' & guide') for name in ('one', 'two')}
    assert [len(c) for c in colors.values()] == [1, 1]
    assert colors['one'] != colors['two']
    stored.surface = set()
    cmd.iterate('one', 'stored.surface.add(s.surface_color)')
    assert stored.surface == colors['one']
    assert 'polar_contacts' in cmd.get_names('all')
    assert '_p_tmp' not in cmd.get_names('all')
    # the next preset undoes surface, sticks and the surface colors
    preset.pretty('all')
    assert cmd.count_atoms('rep surface | rep sticks') == 0
    stored.surface = set()
    cmd.iterate('one', 'stored.surface.add(s.surface_color)')
    assert stored.surface == {None}


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
    preset.antibody('all')
    assert _colors('m & guide') == {index('skyblue')}
    assert _colors('m2 & guide') == {index('lightblue')}
    # the antigen: a surface, sand with the epitope in orange
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('ag')
    assert cmd.count_atoms('rep cartoon') == cmd.count_atoms('m | m2')
    assert _colors('ag') <= {index('wheat'), index('orange')}
    assert index('orange') in _colors('ag')
    assert cmd.count_atoms('rep sticks & (m | m2)') > 0

    # without the motif: the chains named H and L
    cmd.delete('all')
    cmd.fab('ACDEFGHIK', 'h', chain='H')
    cmd.fab('ACDEFGHIK', 'l', chain='L')
    cmd.fab('ACDEFGHIK', 'ag', chain='A')
    preset.antibody('all')
    assert _colors('h & guide') == {index('skyblue')}
    assert _colors('l & guide') == {index('lightblue')}
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
    request.addfinalizer(lambda: preset.look('default'))
    request.addfinalizer(lambda: setattr(preset, 'solvent', False))  # the solvent row
    for row in menu.presets(cmd, 'enabled'):
        if row[0] == 1 and isinstance(row[2], str):
            cmd.do(row[2], echo=0)
            assert reps('hidden') == before, row[1]
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
    assert cmd.count_atoms('rep sticks & organic') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep spheres & organic') == cmd.count_atoms('organic')
    assert cmd.count_atoms('rep spheres') == cmd.count_atoms(preset.lig_sele)
    stored.scales = set()
    cmd.iterate('organic', 'stored.scales.add(round(s.sphere_scale, 2))')
    assert stored.scales == {0.18}
    solvent_nb_count = cmd.count_atoms('rep nonbonded & solvent')
    assert solvent_nb_count > 0
    assert solvent_nb_count < cmd.count_atoms('solvent')
    assert cmd.count_atoms('rep lines & polymer') > 0
    assert cmd.count_atoms('(polymer be. 10 of hetatm) and rep lines') == 0
    assert '1oky_pol_conts' in cmd.get_names('all')
    # the next preset undoes the balls
    preset.pretty('all')
    assert cmd.count_atoms('rep spheres') == 0
    stored.scales = set()
    cmd.iterate('organic', 'stored.scales.add(s.sphere_scale)')
    assert stored.scales == {1.0}


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
    # object color must be preserved for carbons
    color_set = set()
    cmd.iterate('elem C', 'color_set.add(color)', space=locals())
    assert sorted(color_set) == sorted([6])


def testGlass():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.glass('all')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.count_atoms('rep sticks & organic') == cmd.count_atoms('organic')
    assert cmd.get_setting_float('ray_transparency_oblique') == 1
    # the next preset undoes all of it
    preset.simple('all')
    assert cmd.count_atoms('rep surface') == 0
    assert cmd.get_setting_float('ray_transparency_oblique') == 0
    assert cmd.get('surface_color', '1oky') == 'default'


def testWire():
    cmd.load(testing.datafile('1oky.pdb.gz'))
    preset.wire('all')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    assert cmd.get_setting_int('cartoon_debug') == 3
    preset.pretty('all')  # the next preset makes the cartoon solid again
    assert cmd.get_setting_int('cartoon_debug') == 0


def testIllustration(request):
    cmd.load(testing.datafile('1oky.pdb.gz'))
    request.addfinalizer(lambda: preset.look('default'))
    preset.illustration('all')
    assert cmd.count_atoms('rep surface') == cmd.count_atoms('polymer')
    assert cmd.count_atoms('rep cartoon & guide') == cmd.count_atoms('guide')
    stored.colors = set()
    cmd.iterate('guide', 'stored.colors.add(color)')
    assert len(stored.colors) > 10  # shades of one color
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
