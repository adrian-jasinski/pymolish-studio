from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import pytest
import pymol
from pymol import cmd, testing, stored

# spectrum produces colors which are wrong in the second digit
get_color_tuple = lambda c, n=1: tuple([round(x, n) for x in cmd.get_color_tuple(c)])


_color_by_area_cache = {}


@pytest.mark.parametrize("mode", ['molecular', 'solvent'])
def test_color_by_area(mode):
    cmd.fragment('tyr')
    cmd.color('white')
    pymol.util.color_by_area('*', mode, palette='blue_white_red')
    stored.colors = set()
    cmd.iterate('*', 'stored.colors.add(color)')
    colors = [get_color_tuple(c) for c in sorted(stored.colors)]
    assert (1., 0., 0.) in colors
    assert (0., 0., 1.) in colors

    # compare with other mode
    _color_by_area_cache[mode] = colors
    colors_mode_other = _color_by_area_cache.get(
            'molecular' if mode == 'solvent' else 'solvent')
    assert colors != colors_mode_other


@pytest.mark.parametrize("mode", ['molecular', 'solvent'])
def test_color_by_area_part(mode):
    # a part of an object is measured in a copy of the atoms around it;
    # the colors are those of a measurement in the whole object
    cmd.load(testing.datafile('1oky-frag.pdb'), 'm')
    part = 'resi 86-95'

    def colors(selection):
        found = []
        cmd.iterate(selection, 'found.append(color)', space={'found': found})
        return found

    pymol.util.color_by_area('m & ' + part, mode)
    cmd.create('whole', 'm')
    cmd.set('dot_solvent', mode == 'solvent', 'whole')
    cmd.set('dot_density', 3, 'whole')
    cmd.get_area('whole & ' + part, load_b=1)
    cmd.spectrum('b', 'rainbow', 'whole & ' + part)
    assert len(set(colors('m & ' + part))) > 10
    assert colors('m & ' + part) == colors('whole & ' + part)


def test_find_surface_residues():
    pymol.util.find_surface_residues
    pytest.skip("TODO")


def test_find_surface_atoms():
    pymol.util.find_surface_atoms
    pytest.skip("TODO")


def test_get_area():
    pymol.util.get_area
    pytest.skip("TODO")


def test_get_sasa():
    pymol.util.get_sasa
    pytest.skip("TODO")


def test_mass_align():
    pymol.util.mass_align
    pytest.skip("TODO")


def test_sum_formal_charges():
    pymol.util.sum_formal_charges
    pytest.skip("TODO")


def test_sum_partial_charges():
    pymol.util.sum_partial_charges
    pytest.skip("TODO")


def test_compute_mass():
    pymol.util.compute_mass
    pytest.skip("TODO")


def test_protein_assign_charges_and_radii():
    pymol.util.protein_assign_charges_and_radii
    pytest.skip("TODO")


def test_protein_vacuum_esp():
    pymol.util.protein_vacuum_esp
    pytest.skip("TODO")


def test_color_carbon():
    pymol.util.color_carbon
    pytest.skip("TODO")


def test_cbss():
    cmd.load(testing.datafile('1oky-frag.pdb'))
    c = [2, 13, 22] # blue orange forest
    pymol.util.cbss('*', *c)
    stored.colors = set()
    cmd.iterate('*', 'stored.colors.add((ss or "L", color))')
    assert stored.colors == set(zip('HSL', c))


def test_shades():
    cmd.load(testing.datafile('1oky-frag.pdb'))
    cmd.alter('resi 92-', 'chain="B"')
    cmd.alter('resi 106-', 'chain="C"')
    assert cmd.get_chains() == ['A', 'B', 'C']

    def colors(selection):
        stored.colors = []
        cmd.iterate(selection + ' & guide', 'stored.colors.append(color)')
        return [get_color_tuple(c) for c in stored.colors]

    # along each chain: from a light tint to a dark shade
    pymol.util.shades('blue', '*')
    for chain in 'ABC':
        c = colors('chain ' + chain)
        assert c[0] == (0.7, 0.7, 1.0)
        assert c[-1][:2] == (0.0, 0.0)
        assert c[-1][2] < 0.7  # spectrum stops short of the end
        assert len(set(c)) > 3
    # one shade per chain, the color itself in the middle
    pymol.util.shades('blue', '*', chains=1)
    assert set(colors('chain A')) == {(0.7, 0.7, 1.0)}
    assert set(colors('chain B')) == {(0.0, 0.0, 1.0)}
    assert set(colors('chain C')) == {(0.0, 0.0, 0.5)}


def _test_cba(fun, expected_color):
    cmd.fragment('gly')
    cmd.color('white')
    fun('*')
    stored.colors = set()
    cmd.iterate('elem C', 'stored.colors.add(color)')
    colors = [get_color_tuple(c, 3) for c in stored.colors]
    assert colors == [expected_color]


def test_cbag():
    _test_cba(pymol.util.cbag, (0.2, 1.0, 0.2))


def test_cbac():
    _test_cba(pymol.util.cbac, (0.0, 1.0, 1.0))


def test_cbam():
    _test_cba(pymol.util.cbam, (1.0, 0.2, 0.8))


def test_cbay():
    _test_cba(pymol.util.cbay, (1.0, 1.0, 0.0))


def test_cbas():
    _test_cba(pymol.util.cbas, (1.0, 0.6, 0.6))


def test_cbaw():
    _test_cba(pymol.util.cbaw, (0.9, 0.9, 0.9))


def test_cbab():
    _test_cba(pymol.util.cbab, (0.5, 0.5, 1.0))


def test_cbao():
    _test_cba(pymol.util.cbao, (1.0, 0.7, 0.2))


def test_cbap():
    _test_cba(pymol.util.cbap, (0.75, 0.0, 0.75))


def test_cbak():
    _test_cba(pymol.util.cbak, (1.0, 0.65, 0.85))


def test_cnc():
    pymol.util.cnc
    pytest.skip("TODO")


def test_cba():
    pymol.util.cba
    pytest.skip("TODO")


def test_cbh():
    pymol.util.cbh
    pytest.skip("TODO")


def test_enable_all_shaders():
    pymol.util.enable_all_shaders()
    # result depends on whether shaders are available or not


def test_modernize_rendering():
    pymol.util.modernize_rendering(1)  # unused mode argument


def test_performance():
    pymol.util.performance(0)
    assert 1 == cmd.get_setting_int('surface_quality')
    assert 1 == cmd.get_setting_int('depth_cue')
    pymol.util.performance(33)
    assert 0 == cmd.get_setting_int('surface_quality')
    assert 1 == cmd.get_setting_int('depth_cue')
    pymol.util.performance(66)
    assert 0 == cmd.get_setting_int('surface_quality')
    assert 0 == cmd.get_setting_int('depth_cue')
    pymol.util.performance(100)
    assert -1 == cmd.get_setting_int('surface_quality')
    assert 0 == cmd.get_setting_int('depth_cue')


def test_label_chains(mode='chain'):
    cmd.load(testing.datafile('4m4b-minimal-w-assembly.cif'))
    if mode == 'chain':
        pymol.util.label_chains()
    else:
        pymol.util.label_segments()
    stored.labels = set()
    cmd.iterate('*', 'stored.labels.add(label)')
    assert stored.labels == set(['', mode + ' A', mode + ' B'])


def test_label_segments():
    test_label_chains('segi')


def test_cbc():
    pymol.util.cbc
    pytest.skip("TODO")


def test_color_objs():
    pymol.util.color_objs
    pytest.skip("TODO")


def test_chainbow():
    # each chain gets the whole rainbow, residue by residue; what is not
    # selected keeps its color
    cmd.fab('ACDEFGHIK', 'm', chain='A')
    cmd.fab('ACDEFGHIK', 'n', chain='B')
    cmd.color('white')
    pymol.util.chainbow('name CA & not (resn GLY | hetatm)')

    def colors(selection):
        found = []
        cmd.iterate(selection, 'found.append(color)', space={'found': found})
        return found

    first = colors('m & name CA')
    assert len(set(first)) == 9  # eight residues and the white glycine
    assert first == colors('n & name CA')
    assert set(colors('resn GLY')) == {cmd.get_color_index('white')}
    assert not [n for n in cmd.get_names('all') if n.startswith('_chainbow')]


def test_ray_shadows():
    pymol.util.ray_shadows
    pytest.skip("TODO")


def test_ff_copy():
    pymol.util.ff_copy
    pytest.skip("TODO")


def test_b2vdw():
    pymol.util.b2vdw
    pytest.skip("TODO")


def test_phipsi():
    pymol.util.phipsi
    pytest.skip("TODO")


def test_rainbow():
    pymol.util.rainbow
    pytest.skip("TODO")


def test_ss():
    pymol.util.ss
    pytest.skip("TODO")


def test_colors():
    cmd.fragment('gly')
    pymol.util.colors("jmol")
    stored.colors = set()
    cmd.iterate('elem C', 'stored.colors.add(color)')
    colors = [get_color_tuple(c, 3) for c in stored.colors]
    assert colors == [(0.567, 0.567, 0.567)]


def test_interchain_distances():
    pymol.util.interchain_distances
    pytest.skip("TODO")


def test_get_sasa_relative():
    cmd.load(testing.datafile('1oky-frag.pdb'))
    r = cmd.get_sasa_relative()
    assert r['1oky-frag', '', 'A', '86'] == pytest.approx(0.708, abs=1e-3)
    r = cmd.get_sasa_relative("resi 86")
    assert r['1oky-frag', '', 'A', '86'] == pytest.approx(0.708, abs=1e-3)


def test_get_sasa_relative_subsele():
    cmd.load(testing.datafile('1oky-frag.pdb'))
    r = cmd.get_sasa_relative(subsele="sidechain")
    assert r['1oky-frag', '', 'A', '86'] == pytest.approx(0.812, abs=1e-3)
    r = cmd.get_sasa_relative("resi 86", subsele="sidechain")
    assert r['1oky-frag', '', 'A', '86'] == pytest.approx(0.812, abs=1e-3)


def test_get_sasa_relative_tripeptides():
    # all residues are measured in one temporary object; the result is
    # that of one object per residue with its bonded neighbors
    cmd.load(testing.datafile('1oky-frag.pdb'), 'm')
    subsele = 'sidechain guide'
    r = cmd.get_sasa_relative('m', subsele=subsele)

    def area(selection):
        total = [0.0]
        cmd.iterate(selection, 'total[0] += b', space={'total': total})
        return total[0]

    cmd.set('dot_solvent')
    keys = sorted(r, key=lambda key: int(key[3]))
    for key in (keys[0], keys[len(keys) // 2], keys[-1]):
        residue = '/%s/%s/%s/`%s' % key
        cmd.get_area('m', load_b=1)
        inside = area('%s & (%s)' % (residue, subsele))
        cmd.create('t', 'byres (%s extend 1)' % residue, zoom=0)
        cmd.get_area('t', load_b=1)
        alone = area('/t/%s/%s/`%s & (%s)' % (key[1:] + (subsele,)))
        cmd.delete('t')
        assert alone > 0
        assert r[key] == pytest.approx(inside / alone, abs=1e-6)


def test_ligand_zoom():
    pymol.util.ligand_zoom
    pytest.skip("TODO")
