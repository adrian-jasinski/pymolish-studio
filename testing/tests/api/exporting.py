'''
unit tests for pymol.exporting
'''

import pytest
import os
import shutil
import sys
import tempfile
import Image

import pymol.exporting
from pymol import cmd, testing, stored


def testCache():
    for action in pymol.exporting.cache_action_dict:
        cmd.cache(action)


def testCopyImage():
    cmd.copy_image
    pytest.skip("TODO")


def testGetFastastr():
    seq, name = 'ACD', 'm1'
    cmd.fab(seq, name)
    s = cmd.get_fastastr()
    lines = s.split()
    assert (lines[0] in (
        '>' + name,
        '>' + name + '_',
    ))
    assert lines[1:] == [seq]


def testGetPdbstr():
    cmd.pseudoatom()
    lines = cmd.get_pdbstr().splitlines()
    assert lines[0].startswith('HETATM')
    assert lines[1].startswith('END')


def testGetSession():
    cmd.fragment('ala')
    x = cmd.count_atoms()
    s = cmd.get_session()
    cmd.reinitialize()
    cmd.set_session(s)
    assert ['ala'] == cmd.get_names()
    assert x == cmd.count_atoms()


def testGetSession25():
    cmd.set('pse_binary_dump', 0)
    cmd.set('pse_export_version', 0)
    s = cmd.get_session(binary=-1, version=-1)
    assert cmd.get_setting_int('pse_binary_dump') == 0
    assert cmd.get_setting_float('pse_export_version') == 0.0
    cmd.set_session(s)
    assert cmd.get_setting_int('pse_binary_dump') == 0
    assert cmd.get_setting_float('pse_export_version') == 0.0
    s = cmd.get_session(binary=True, version=1.2)
    assert cmd.get_setting_int('pse_binary_dump') == 0
    assert cmd.get_setting_float('pse_export_version') == 0.0
    cmd.set_session(s)
    assert cmd.get_setting_int('pse_binary_dump') == 1
    assert cmd.get_setting_float('pse_export_version') == 1.2


def testMultisave():
    names = ['ala', 'gly', 'his', 'arg']

    for name in names:
        cmd.fragment(name)

    sym1 = (1.2, 3.4, 5.6, 60.0, 70.0, 80.0)
    sym2 = (2.3, 4.5, 6.7, 90.0, 90.0, 90.0)
    sym3 = (3.4, 5.6, 7.8, 70.0, 70.0, 70.0)
    cmd.set_symmetry("gly", *sym1)
    cmd.set_symmetry("his", *sym2)
    cmd.set_symmetry("arg", *sym3)

    with testing.mktemp('.pdb') as filename:
        cmd.multisave(filename, names[0])                       # new
        cmd.multisave(filename, names[1])                       # new (overwrite)
        cmd.multisave(filename, ' '.join(names[2:]), append=1)  # append
        cmd.delete('*')
        cmd.load(filename)

    assert cmd.get_object_list() == names[1:]

    testing.assert_array_equal(cmd.get_symmetry("gly")[:6], sym1, delta=1e-4)
    testing.assert_array_equal(cmd.get_symmetry("his")[:6], sym2, delta=1e-4)
    testing.assert_array_equal(cmd.get_symmetry("arg")[:6], sym3, delta=1e-4)


def testMultifilesave():
    import glob

    for name in ['ala', 'gly', 'his', 'arg']:
        cmd.fragment(name)

    # multistate
    for i in range(2, 11):
        cmd.create('ala', 'ala', 1, i)

    for fmt in ['{}-{:02}.cif', '{}-{state}.cif']:
        with testing.mkdtemp() as dirname:
            cmd.multifilesave(os.path.join(dirname, fmt), 'ala', 0)
            filenames = [os.path.basename(p) for p in glob.glob(os.path.join(dirname, '*.cif'))]
            assert len(filenames) == 10
            assert 'ala-03.cif' in filenames

    with testing.mkdtemp() as dirname:
        cmd.multifilesave(os.path.join(dirname, '{}.pdb'), 'a* g*')
        filenames_full = sorted(glob.glob(os.path.join(dirname, '*.pdb')))
        filenames = [os.path.basename(p) for p in filenames_full]
        assert filenames == ['ala.pdb', 'arg.pdb', 'gly.pdb']

        cmd.delete('*')
        cmd.load(filenames_full[0])
        assert cmd.count_atoms() == 10

        cmd.delete('*')
        cmd.load(filenames_full[1])
        assert cmd.count_atoms() == 24


@pytest.mark.parametrize("w,h,dpi,size", [
    ('0.5in', '0.25in', 200, (100, 50)),   # inch
    ('2.54cm', '1.27cm', 100, (100, 50)),  # centimeter
    (100, 0, -1, (100, 75)),               # px, only width
    (0, 75, -1, (100, 75)),                # px, only height
])
@testing.requires('no_edu') # ray
def testPng(w, h, dpi, size):
    with testing.mktemp('.png') as filename:
        cmd.png(filename, w, h, dpi, ray=1)
        assert size == Image.open(filename).size


def testPngNoFile():
    testing.ambient_only()
    cmd.fragment('gly')
    cmd.show_as('spheres')
    cmd.color('yellow')
    cmd.zoom(complete=1)

    cmd.refresh()  # TODO should not be necessary, see also PYMOL-3328

    ncol, nrow = 120, 80
    buf = cmd.png(None, ncol, nrow)
    assert buf.startswith(b'\x89PNG')
    import io
    img = testing.get_imagearray(Image.open(io.BytesIO(buf)))
    assert img.shape[:2] == (nrow, ncol)
    testing.assert_image_has_color('yellow', img)


def testPngPPM():
    cmd.fragment('gly')
    with testing.mktemp('.ppm') as filename:
        cmd.png(filename, 20, 10, ray=1, format=1)
        with open(filename, 'rb') as handle:
            data = handle.read()
    header = b'P6\n20 10\n255\n'
    assert data.startswith(header)
    assert len(data) == len(header) + 20 * 10 * 3


def testLoadPngDataUrl():
    import base64
    import io
    cmd.fragment('gly')
    buf = cmd.png(None, 40, 30, ray=1)
    cmd.png(None, 20, 10, ray=1)
    cmd.load_png('data:image/png;base64,' + base64.b64encode(buf).decode())
    assert Image.open(io.BytesIO(cmd.png(None))).size == (40, 30)


# not supported in older versions: xyz (no ref)
@pytest.mark.parametrize("format", ['pdb', 'sdf', 'mol', 'mol2'])
def testSaveRef(format):
    # for rms_cur (not all formats save all identifiers)
    m = -1
    cmd.set('retain_order')

    cmd.fragment('ala', 'm1')
    cmd.copy('m2', 'm1')
    cmd.copy('m3', 'm1')

    cmd.rotate('y', 90, 'm2')
    cmd.align('m3', 'm2')

    # with ref=m3
    with testing.mktemp('.' + format) as filename:
        cmd.save(filename, 'm2', ref='m3')
        cmd.load(filename, 'm4')
        assert cmd.rms_cur('m4', 'm1', matchmaker=m) == pytest.approx(0.00, abs=1e-2)
        assert cmd.rms_cur('m4', 'm2', matchmaker=m) == pytest.approx(1.87, abs=1e-2)

    # without ref
    with testing.mktemp('.' + format) as filename:
        cmd.save(filename, 'm2')
        cmd.load(filename, 'm5')
        assert cmd.rms_cur('m5', 'm2', matchmaker=m) == pytest.approx(0.00, abs=1e-2)
        assert cmd.rms_cur('m5', 'm1', matchmaker=m) == pytest.approx(1.87, abs=1e-2)


@pytest.mark.parametrize("format,pymol_version", [
        ('pdb',  1.2),
        ('sdf',  1.7),
        ('mol2', 1.7),
        ('xyz',  1.8),
        ('mol',  1.831),
        ('cif',  1.8),
])
def testSaveState(format, pymol_version):
    if pymol_version > testing.PYMOL_VERSION[1]:
        pytest.skip("version %f" % (pymol_version))

    # for rms_cur (not all formats save all identifiers)
    m = -1
    cmd.set('retain_order')

    # create a multistate object
    cmd.fragment('ala', 'm1')
    cmd.create('m1', 'm1', 1, 2)
    cmd.create('m1', 'm1', 1, 3)
    cmd.translate([5, 0, 0], 'm1', state=2)
    cmd.translate([0, 5, 0], 'm1', state=3)
    n_states = cmd.count_states('m1')

    with testing.mktemp('.' + format) as filename:
        # explicit
        for state in range(1, n_states + 1):
            cmd.delete('m2')
            cmd.save(filename, 'm1', state=state)
            cmd.load(filename, 'm2', format=format)
            rms = cmd.rms_cur('m1', 'm2', state, 1, matchmaker=m)
            assert rms == pytest.approx(0.00, abs=1e-2)

        # current state
        for state in range(1, n_states + 1):
            cmd.frame(state)
            cmd.delete('m2')
            cmd.save(filename, 'm1')
            cmd.load(filename, 'm2', 1, format=format)
            rms = cmd.rms_cur('m1', 'm2', state, 1, matchmaker=m)
            assert rms == pytest.approx(0.00, abs=1e-2)

        if format in ('mol',):
            # no multi support
            return

        # all states
        cmd.delete('m2')
        cmd.save(filename, 'm1', state=0)
        cmd.load(filename, 'm2', 1, discrete=1, multiplex=0)
        assert cmd.count_states('m2') == n_states
        for state in range(1, n_states + 1):
            rms = cmd.rms_cur('m1', 'm2 and state %d' % state,
                    state, state, matchmaker=m)
            assert rms == pytest.approx(0.00, abs=1e-2)


@pytest.mark.parametrize("format,pymol_version", [
        ('pdb',  1.2),
        ('sdf',  1.7),
        ('mol2', 1.7),
        ('xyz',  1.7),
        ('mol',  1.7),
        ('cif',  1.8),
])
def testSaveSelection(format, pymol_version):
    if pymol_version > testing.PYMOL_VERSION[1]:
        pytest.skip("version %f" % (pymol_version))

    cmd.fragment('trp', 'm1')
    cmd.fragment('glu', 'm2')

    n_O = cmd.count_atoms('elem O')
    n_N = cmd.count_atoms('elem N')

    with testing.mktemp('.' + format) as filename:
        if testing.PYMOL_VERSION_TUPLE < (1, 8):
            cmd.set('raise_exceptions', 0) # 1.7.6 save xyz doesn't set r=DEFAULT_SUCCESS
        cmd.save(filename, 'elem O+N')
        if testing.PYMOL_VERSION_TUPLE < (1, 8):
            cmd.set('raise_exceptions', 1)

        cmd.delete('*')
        cmd.load(filename, 'm2', discrete=1, format=format) # avoid merging of atoms

    assert n_O == cmd.count_atoms('elem O')
    assert n_N == cmd.count_atoms('elem N')
    assert n_O + n_N == cmd.count_atoms()


@pytest.mark.parametrize("format", ['pdb', 'cif'])
def testSave_symmetry(format):
    sym1 = (1.2, 3.4, 5.6, 60.0, 70.0, 80.0, "P 3")
    cmd.fragment("gly", "m1")
    cmd.set_symmetry("m1", *sym1)

    with testing.mktemp('.' + format) as filename:
        cmd.save(filename)
        cmd.delete('*')
        cmd.load(filename, "m2")

    sym = cmd.get_symmetry("m2")
    testing.assert_array_equal(sym[:6], sym1[:6], delta=1e-4)
    assert sym[6] == sym1[6]


# cmp_atom : compares all fields in Atom (see chempy/__init__.py)
#            except the id (which is unique to the instance)
def cmp_atom(selfobj,other):
    cmp = lambda a, b: a != b # py3k
    return \
                cmp(type(selfobj), type(other)) or \
                cmp(selfobj.segi, other.segi) or \
                cmp(selfobj.chain, other.chain) or \
                cmp(selfobj.resi_number, other.resi_number) or \
                cmp(selfobj.resi, other.resi) or \
                cmp(selfobj.resn, other.resn) or \
                cmp(selfobj.symbol, other.symbol) or \
                cmp(selfobj.name, other.name)


# cmp_bond : compares all fields in Bond (see chempy/__init__.py)
def cmp_bond(selfobj,other):
    cmp = lambda a, b: a != b # py3k
    return \
                cmp(selfobj.order, other.order) or \
                cmp(selfobj.index, other.index)


def assertModelsAreSame(m1, m2):
    assert len(m1.atom) == len(m2.atom)
    idx = 0
    for m1atomidx in m1.atom:
        assert cmp_atom(m1atomidx, m2.atom[idx]) == 0
        idx = idx + 1
    idx = 0
    for m1bondidx in m1.bond:
        assert cmp_bond(m1bondidx, m2.bond[idx]) == 0
        idx = idx + 1


def testPSEBulkImport():
    cmd.load(testing.datafile('1rx1_1766_bulk.pse.gz'))
    m1 = cmd.get_model()
    cmd.load(testing.datafile('1rx1_176.pse.gz'))
    m2 = cmd.get_model()
    assertModelsAreSame(m1, m2)


@pytest.mark.parametrize("pse_export_version", (0, 1.7, 1.76, 1.8, 1.82, 1.9))
@pytest.mark.parametrize("pse_binary_dump", (0, 1))
def testPSEBulkExportImport(pse_export_version, pse_binary_dump):
    with testing.mktemp('.pse') as filename:
        cmd.load(testing.datafile("1oky-frag.pdb"))
        m1 = cmd.get_model()
        cmd.set("pse_export_version", pse_export_version)
        cmd.set("pse_binary_dump", pse_binary_dump)
        cmd.save(filename)
        cmd.reinitialize()
        cmd.load(filename)
        m2 = cmd.get_model()
        assertModelsAreSame(m1, m2)


def testGetModelObjectName():
    cmd.load(testing.datafile("1oky-frag.pdb"))
    cmd.load(testing.datafile('1rna.cif'))

    m1 = cmd.get_model()
    cnt = cmd.count_atoms('%1oky-frag')

    assert m1.atom[0].model == '1oky-frag'
    assert m1.atom[-1].model == '1rna'
    assert m1.atom[cnt].model == '1rna'


@pytest.mark.skipif('gltf' not in pymol.get_capabilities(),
                    reason='no native glTF support')
def testglTF():
    '''glTF export'''
    cmd.fragment('gly')

    with testing.mktemp('.gltf') as filename:
        assert cmd.save(filename) is None
        cmd.delete('*')


def testSaveAln():
    cmd.fab('ACDEFGH', 'm1')
    cmd.fab('ACDFGH', 'm2')
    cmd.align('m1', 'm2', cycles=0, object='aln')
    with testing.mktemp('.aln') as filename:
        cmd.save(filename)
        with open(filename) as handle:
            lines = list(handle)
    assert lines[0].split() == ['CLUSTAL']
    assert lines[1].split() == []
    assert lines[2].split() == ['m1', 'ACDEFGH']
    assert lines[3].split() == ['m2', 'ACD-FGH']


def testSaveAlnNucleic():
    cmd.load(testing.datafile('1rna.cif'))
    cmd.create('m1', 'chain A and not resi 6-7')
    cmd.create('m2', 'chain B')
    cmd.alter('m1 and resi 1', 'resn = "DT"') # mimic DNA
    cmd.alter('m2 and resi 20', 'resn = "UNK"') # mimic nonstd residue
    cmd.align('m1', 'm2', cycles=0, object='aln')
    with testing.mktemp('.aln') as filename:
        cmd.save(filename)
        with open(filename) as handle:
            lines = list(handle)
    assert lines[0].split() == ['CLUSTAL']
    assert lines[1].split() == []
    assert lines[2].split() == ['m1', 'TUAUA--UAUAUAA']
    assert lines[3].split() == ['m2', 'UUAUA?AUAUAUAA']


def testAssingAtomTypes():
    cmd.fragment('his')
    cmd.alter('all', 'text_type = "none"')
    mytypes = {}
    cmd.iterate('all', 'mytypes[name] = text_type', space=locals())
    assert mytypes['NE2'] == 'none'
    pymol.exporting.assign_atom_types('all', 'mol2')
    cmd.iterate('all', 'mytypes[name] = text_type', space=locals())
    assert mytypes['NE2'] == 'N.pl3'
    assert mytypes['N'] == 'N.3'
    assert mytypes['CG'] == 'C.2'
