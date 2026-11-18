
from pymol import cmd, testing, stored, preset

class TestPreset(testing.PyMOLTestCase):

    def _assertSimpleReps(self):
        self.assertEqual(cmd.count_atoms('rep cartoon'), 0)
        self.assertEqual(cmd.count_atoms('rep ribbon & guide'), cmd.count_atoms('guide'))
        self.assertEqual(cmd.count_atoms('rep sticks & organic'), cmd.count_atoms('organic'))
        self.assertEqual(cmd.count_atoms('rep nonbonded & solvent'), cmd.count_atoms('solvent'))

    def _assertPrettyReps(self):
        self.assertEqual(cmd.count_atoms('rep cartoon & guide'), cmd.count_atoms('guide'))
        self.assertEqual(cmd.count_atoms('rep ribbon'), 0)
        self.assertEqual(cmd.count_atoms('rep sticks & organic'), cmd.count_atoms('organic'))
        self.assertEqual(cmd.count_atoms('rep nonbonded'), 0)
        self.assertEqual(cmd.count_atoms('rep nonbonded'), 0)

    def testSimple(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.simple('all')
        self._assertSimpleReps()

    def _guideColors(self):
        stored.colors = set()
        cmd.iterate('guide', 'stored.colors.add(color)')
        return stored.colors

    def testKeepsProteinColors(self):
        # 15h: the working presets leave the cartoon color alone
        cmd.load(self.datafile('1oky.pdb.gz'))
        cmd.color('yellow', 'polymer & elem C')
        for name in ('technical', 'ligands', 'ligand_sites', 'ligand_cartoon',
                     'ball_and_stick', 'classified'):
            getattr(preset, name)('all')
            self.assertEqual(self._guideColors(), {6}, name)
        preset.pretty('all')  # a picture preset still colors
        self.assertGreater(len(self._guideColors()), 10)

    def testInteraction(self):
        # two chains in two objects, built on top of each other: all touch
        cmd.fab('ACDEFGHIK', 'one', chain='A')
        cmd.fab('LMNPQRSTV', 'two', chain='A')
        preset.interaction('all')
        self.assertEqual(cmd.count_atoms('rep cartoon'), cmd.count_atoms('polymer'))
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('polymer'))
        self.assertGreater(cmd.count_atoms('rep sticks'), 0)
        # one color per chain and object, the same for its surface
        colors = {name: self._colors(name + ' & guide') for name in ('one', 'two')}
        self.assertEqual([len(c) for c in colors.values()], [1, 1])
        self.assertNotEqual(colors['one'], colors['two'])
        stored.surface = set()
        cmd.iterate('one', 'stored.surface.add(s.surface_color)')
        self.assertEqual(stored.surface, colors['one'])
        self.assertIn('polar_contacts', cmd.get_names('all'))
        self.assertNotIn('_p_tmp', cmd.get_names('all'))
        # the next preset undoes surface, sticks and the surface colors
        preset.pretty('all')
        self.assertEqual(cmd.count_atoms('rep surface | rep sticks'), 0)
        stored.surface = set()
        cmd.iterate('one', 'stored.surface.add(s.surface_color)')
        self.assertEqual(stored.surface, {None})

    def _colors(self, selection):
        stored.colors = set()
        cmd.iterate(selection, 'stored.colors.add(color)')
        return stored.colors

    def testAntibody(self):
        index = cmd.get_color_index
        # found by the start of framework 2, whatever the chains are called
        cmd.fab('AAWVRQAPGKGLEW', 'm', chain='X')
        cmd.fab('AAWYQQKPGKAPKL', 'm2', chain='Y')
        cmd.fab('ACDEFGHIKLMNPQ', 'ag', chain='Z')
        preset.antibody('all')
        self.assertEqual(self._colors('m & guide'), {index('skyblue')})
        self.assertEqual(self._colors('m2 & guide'), {index('lightblue')})
        # the antigen: a surface, sand with the epitope in orange
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('ag'))
        self.assertEqual(cmd.count_atoms('rep cartoon'), cmd.count_atoms('m | m2'))
        self.assertTrue(self._colors('ag') <= {index('wheat'), index('orange')})
        self.assertIn(index('orange'), self._colors('ag'))
        self.assertGreater(cmd.count_atoms('rep sticks & (m | m2)'), 0)

        # without the motif: the chains named H and L
        cmd.delete('all')
        cmd.fab('ACDEFGHIK', 'h', chain='H')
        cmd.fab('ACDEFGHIK', 'l', chain='L')
        cmd.fab('ACDEFGHIK', 'ag', chain='A')
        preset.antibody('all')
        self.assertEqual(self._colors('h & guide'), {index('skyblue')})
        self.assertEqual(self._colors('l & guide'), {index('lightblue')})
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('ag'))

        # no antibody at all: the interaction picture
        cmd.delete('all')
        cmd.fab('ACDEFGHIK', 'pa', chain='A')
        cmd.fab('ACDEFGHIK', 'pb', chain='B')
        preset.antibody('all')
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('all'))
        self.assertNotIn('_p_tmp', cmd.get_names('all'))

    def testEnabledOnly(self):
        # the toolbar applies a preset to "enabled": a hidden object is left
        from pymol import menu
        cmd.fab('ACDEFGHIK', 'shown')
        cmd.fab('ACDEFGHIK', 'hidden')
        cmd.disable('hidden')

        def reps(name):
            return [cmd.count_atoms('%s & rep %s' % (name, r))
                    for r in ('lines', 'sticks', 'cartoon', 'surface', 'spheres')]

        before = reps('hidden')
        self.addCleanup(preset.look, 'default')
        self.addCleanup(setattr, preset, 'solvent', False)  # the solvent row
        for row in menu.presets(cmd, 'enabled'):
            if row[0] == 1 and isinstance(row[2], str):
                cmd.do(row[2], echo=0)
                self.assertEqual(reps('hidden'), before, row[1])
        rows = dict((r[1], r[2]) for r in menu.cartoon_transparency(cmd, 'enabled'))
        cmd.do(rows['50%'], echo=0)
        self.assertEqual(cmd.get_setting_float('cartoon_transparency', 'shown'), 0.5)
        self.assertEqual(cmd.get_setting_float('cartoon_transparency', 'hidden'), 0)

    def testTechnical(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.technical('all')
        # cartoon, not ribbon: only "simple" keeps the ribbon
        self.assertEqual(cmd.count_atoms('rep cartoon & guide'), cmd.count_atoms('guide'))
        self.assertEqual(cmd.count_atoms('rep ribbon'), 0)
        self.assertEqual(cmd.count_atoms('rep nonbonded & solvent'), cmd.count_atoms('solvent'))
        self.assertTrue('1oky_pol_conts' in cmd.get_names('all'))

    def testPublication(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.publication('all')
        self._assertPrettyReps()
        self.assertTrue(cmd.get_setting_boolean('cartoon_smooth_loops', '1oky'))
        self.assertTrue(cmd.get_setting_boolean('cartoon_fancy_helices', '1oky'))

    def testPretty(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.pretty('all')
        self._assertPrettyReps()
        self.assertFalse(cmd.get_setting_boolean('cartoon_smooth_loops', '1oky'))
        self.assertFalse(cmd.get_setting_boolean('cartoon_fancy_helices', '1oky'))

    def testLigands(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.ligands('all')
        self.assertGreater(cmd.count_atoms('rep cartoon'), 0)
        self.assertEqual(cmd.count_atoms('rep ribbon'), 0)
        # the ligand as balls and thin sticks
        self.assertEqual(cmd.count_atoms('rep sticks & organic'), cmd.count_atoms('organic'))
        self.assertEqual(cmd.count_atoms('rep spheres & organic'), cmd.count_atoms('organic'))
        self.assertEqual(cmd.count_atoms('rep spheres'), cmd.count_atoms(preset.lig_sele))
        stored.scales = set()
        cmd.iterate('organic', 'stored.scales.add(round(s.sphere_scale, 2))')
        self.assertEqual(stored.scales, {0.18})
        solvent_nb_count = cmd.count_atoms('rep nonbonded & solvent')
        self.assertGreater(solvent_nb_count, 0)
        self.assertLess(solvent_nb_count, cmd.count_atoms('solvent'))
        self.assertGreater(cmd.count_atoms('rep lines & polymer'), 0)
        self.assertEqual(cmd.count_atoms('(polymer be. 10 of hetatm) and rep lines'), 0)
        self.assertTrue('1oky_pol_conts' in cmd.get_names('all'))
        # the next preset undoes the balls
        preset.pretty('all')
        self.assertEqual(cmd.count_atoms('rep spheres'), 0)
        stored.scales = set()
        cmd.iterate('organic', 'stored.scales.add(s.sphere_scale)')
        self.assertEqual(stored.scales, {1.0})

    def testDefault(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        cmd.color("yellow", "1oky") # color index 6
        preset.default('1oky')
        self.assertEqual(cmd.count_atoms('rep cartoon'), 0)
        self.assertEqual(cmd.count_atoms('rep ribbon'), 0)
        self.assertEqual(cmd.count_atoms('rep sticks'), 0)
        self.assertEqual(cmd.count_atoms('rep spheres'), 0)
        self.assertEqual(cmd.count_atoms('rep lines'), cmd.count_atoms())
        self.assertEqual(cmd.count_atoms('rep nonbonded & solvent'), cmd.count_atoms('solvent'))
        # object color must be preserved for carbons
        color_set = set()
        cmd.iterate('elem C', 'color_set.add(color)', space=locals())
        self.assertItemsEqual(color_set, [6])

    def testGlass(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.glass('all')
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('polymer'))
        self.assertEqual(cmd.count_atoms('rep cartoon & guide'), cmd.count_atoms('guide'))
        self.assertEqual(cmd.count_atoms('rep sticks & organic'), cmd.count_atoms('organic'))
        self.assertEqual(cmd.get_setting_float('ray_transparency_oblique'), 1)
        # the next preset undoes all of it
        preset.simple('all')
        self.assertEqual(cmd.count_atoms('rep surface'), 0)
        self.assertEqual(cmd.get_setting_float('ray_transparency_oblique'), 0)
        self.assertEqual(cmd.get('surface_color', '1oky'), 'default')

    def testWire(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        preset.wire('all')
        self.assertEqual(cmd.count_atoms('rep cartoon & guide'), cmd.count_atoms('guide'))
        self.assertEqual(cmd.get_setting_int('cartoon_debug'), 3)
        preset.pretty('all')  # the next preset makes the cartoon solid again
        self.assertEqual(cmd.get_setting_int('cartoon_debug'), 0)

    def testIllustration(self):
        cmd.load(self.datafile('1oky.pdb.gz'))
        self.addCleanup(preset.look, 'default')
        preset.illustration('all')
        self.assertEqual(cmd.count_atoms('rep surface'), cmd.count_atoms('polymer'))
        self.assertEqual(cmd.count_atoms('rep cartoon & guide'), cmd.count_atoms('guide'))
        stored.colors = set()
        cmd.iterate('guide', 'stored.colors.add(color)')
        self.assertGreater(len(stored.colors), 10)  # shades of one color
        # it picks the look flat: true colors, outlines on transparent things
        self.assertEqual(cmd.get_setting_int('ray_trace_mode'), 1)
        self.assertEqual(cmd.get_setting_float('ray_trace_trans_cutoff'), 1)
        preset.look('default')
        self.assertAlmostEqual(cmd.get_setting_float('ray_trace_trans_cutoff'), 0.05)

    def testMenuSolvent(self):
        # one solvent row in the menu instead of "(with solvent)" twins
        cmd.load(self.datafile('1oky.pdb.gz'))
        self.addCleanup(setattr, preset, 'solvent', False)
        n_solvent = cmd.count_atoms('solvent')
        for name in ('simple', 'technical', 'ball_and_stick', 'b_factor_putty',
                     'pretty_solv', 'pub_solv', 'glass', 'wire', 'ligands',
                     'ligand_sites', 'ligand_cartoon', 'interface', 'classified'):
            preset.from_menu(name, 'all')
            self.assertEqual(cmd.count_atoms('solvent & visible'), 0, name)
            self.assertGreater(cmd.count_atoms('visible'), 0, name)
        self.assertNotIn('_p_tmp', cmd.get_names('all'))
        preset.from_menu('default', 'all')
        self.assertEqual(cmd.count_atoms('solvent & visible'), n_solvent)
        preset.from_menu('pretty_solv', 'all')
        preset.show_solvent(1, 'all')
        self.assertEqual(cmd.count_atoms('solvent & rep nb_spheres'), n_solvent)
        for name in ('simple', 'pretty_solv', 'pub_solv'):
            preset.from_menu(name, 'all')
            self.assertEqual(cmd.count_atoms('solvent & visible'), n_solvent, name)
        preset.show_solvent(0, 'all')
        self.assertEqual(cmd.count_atoms('solvent & visible'), 0)

    def testLook(self):
        # 15g: no look touches the background or its transparency
        cmd.bg_color('grey50')
        cmd.set('ray_opaque_background', 0)
        self.addCleanup(cmd.reinitialize)
        for name in preset.LOOKS:  # every key is a setting
            preset.look(name)
            self.assertEqual(cmd.get('bg_rgb'), 'grey50', name)
            self.assertEqual(cmd.get_setting_int('ray_opaque_background'), 0, name)
            # the outline contrasts with whatever the background is
            self.assertEqual(cmd.get('ray_trace_color'), 'front', name)
        preset.look('figure')
        self.assertEqual(cmd.get_setting_int('ray_trace_mode'), 1)
        preset.look('comic')
        self.assertEqual(cmd.get_setting_int('ray_trace_mode'), 3)
        preset.look('sketch')
        self.assertEqual(cmd.get_setting_int('ray_trace_mode'), 2)
        self.assertEqual(cmd.get_setting_int('antialias'), 2)
        preset.look('x-ray')  # a look replaces the one before it
        self.assertEqual(cmd.get_setting_int('ray_trace_mode'), 0)
        self.assertEqual(cmd.get_setting_float('ambient'), 1)
        preset.look('default')
        self.assertAlmostEqual(cmd.get_setting_float('ambient'), 0.14)
        self.assertEqual(cmd.get_setting_int('light_count'), 2)
