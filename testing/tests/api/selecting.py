
import pytest
from pymol import cmd, testing, stored


def test_error_propagation():
    try:
        cmd.center("(all) and no_such_name")
    except Exception as e:
        assert "Invalid selection name" in e.message
        assert "no_such_name" in e.message
        return
    pytest.fail("did not raise")


def testDeselect():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m1")
    cmd.select("all")
    assert ("sele" in cmd.get_names("all",enabled_only=1)) == True
    cmd.deselect()
    assert ("sele" in cmd.get_names("all",enabled_only=1)) == False


def testIndicate():
    cmd.load(testing.datafile("1oky.pdb.gz"), "m1")
    cmd.indicate("polymer")
    assert cmd.count_atoms("polymer") == cmd.count_atoms("indicate")
    assert cmd.count_atoms("indicate & solvent & organic & inorganic") == 0


def testPop():
    cmd.fragment("ala")
    cmd.select("src", "ala")
    # iterate across the 10 atoms in ala
    cnt = 0
    while cmd.pop("tmp","src"):
        cnt+=1
    assert cnt == 10


def testSelect():
    cmd.fragment("gly", "m1")
    NC = 2

    # auto_number_selections=0
    cmd.select("elem C")
    assert NC == cmd.count_atoms("sele")
    assert 0 == cmd.get_setting_int("sel_counter")

    # auto_number_selections=1
    cmd.set('auto_number_selections', 1)
    cmd.set('sel_counter', 3)
    cmd.select("elem C")
    assert NC == cmd.count_atoms("sel04")
    assert 4 == cmd.get_setting_int("sel_counter")

    cmd.set('auto_number_selections', 1)
    cmd.select(None, "elem C")
    assert NC == cmd.count_atoms("sel05")
    assert 5 == cmd.get_setting_int("sel_counter")

    # name=None always numbers the selection
    cmd.set('auto_number_selections', 0)
    cmd.select(None, "elem C")
    assert NC == cmd.count_atoms("sel06")
    assert 6 == cmd.get_setting_int("sel_counter")

    # default
    cmd.select("foo", "elem C")
    assert NC == cmd.count_atoms("foo")
    assert ["foo"] == cmd.get_names("selections", enabled_only=1)

    # merge with non-existing, enable=0
    cmd.delete('foo')
    cmd.select("foo", "elem C", 0, merge=1)
    assert NC == cmd.count_atoms("foo")
    assert [] == cmd.get_names("selections", enabled_only=1)

    # merge, enable=1
    cmd.select("foo", "elem N", 1)
    assert 1 == cmd.count_atoms("foo")
    assert ["foo"] == cmd.get_names("selections", enabled_only=1)

    cmd.select("foo", "elem C", -1, merge=1)
    assert NC + 1 == cmd.count_atoms("foo")
    assert ["foo"] == cmd.get_names("selections", enabled_only=1)

    cmd.select("foo", "elem O", -1, merge=2)
    assert NC + 2 == cmd.count_atoms("foo")
    assert ["foo"] == cmd.get_names("selections", enabled_only=1)

    # merge, enable=0
    cmd.select("foo", "elem N", 0)
    assert 1 == cmd.count_atoms("foo")
    assert [] == cmd.get_names("selections", enabled_only=1)

    cmd.select("foo", "elem C", -1, merge=1)
    assert NC + 1 == cmd.count_atoms("foo")
    assert [] == cmd.get_names("selections", enabled_only=1)

    cmd.select("foo", "elem O", -1, merge=2)
    assert 1 == cmd.count_atoms("foo")
    assert [] == cmd.get_names("selections", enabled_only=1)

    # state
    cmd.create('m1', 'm1 & elem C', 1, 2)
    assert 7 == cmd.select('present')
    assert 7 == cmd.select('present', state=1)
    assert 2 == cmd.select('present', state=2)
    assert 0 == cmd.select('present', state=3)

    # domain
    cmd.select("foo", "elem C")
    cmd.select("bar", "name CA+N+O", domain="foo")
    assert 1 == cmd.count_atoms("bar")


def testSelectList():
    cmd.fragment('ala', 'm1')
    cmd.alter('m1', 'rank += 10')
    cmd.alter('m1', 'ID += 20')
    cmd.select_list('s1', 'm1', [1, 4], mode='index')
    assert cmd.count_atoms('s1') == 2
    assert cmd.count_atoms('s1 & elem N') == 1
    assert cmd.count_atoms('s1 & elem O') == 1
    cmd.select_list('s1', 'm1', [15, 16, 17, 18, 19], mode='rank')
    assert cmd.count_atoms('s1') == 5
    assert cmd.count_atoms('s1 & elem H') == 5
    cmd.select_list('s1', 'm1', [21, 22, 23], mode='id')
    assert cmd.count_atoms('s1') == 3
    assert cmd.count_atoms('s1 & elem C') == 3

    # empty list (use new selection names to verify that named selection
    # was crated)
    cmd.select_list('s2', 'm1', [], mode='index')
    assert cmd.count_atoms('s2') == 0
    cmd.select_list('s3', 'm1', [], mode='rank')
    assert cmd.count_atoms('s3') == 0
    cmd.select_list('s4', 'm1', [], mode='id')
    assert cmd.count_atoms('s4') == 0


def testSelectList_state():
    cmd.fragment('ala', 'm1')
    cmd.create('m1', 'm1 & elem C', 1, 2)
    cmd.select_list('s1', 'm1', [100] * 100 + [2, 3, 4], state=1, mode='rank')
    assert cmd.count_atoms('s1') == 3
    cmd.select_list('s1', 'm1', [100] * 100 + [2, 3, 4], state=2, mode='rank')
    assert cmd.count_atoms('s1') == 2


# https://github.com/schrodinger/pymol-open-source/issues/109
@pytest.mark.parametrize("mode", ['index', 'rank', 'id'])
def testSelectList_unmatched(mode):
    cmd.fragment('ala', 'm1')
    cmd.select_list('s1', 'm1', [100], mode=mode)
    assert cmd.count_atoms('s1') == 0


def testMacros():
    '''
        Test selection macros: /model/segi/chain/resn`resi/name`alt

        See also tests/jira/PYMOL-2720.py
        '''
    cmd.load(testing.datafile("1oky.pdb.gz"), "m1")
    cmd.alter('*', 'segi="X"')
    cmd.alter('resi 200-238', 'chain="B"')
    cmd.alter('resi 239-360', 'chain="C"')
    cmd.alter('resi 150-220', 'segi="Y"')
    cmd.alter('resi 220-', 'segi="Z"')

    # all atoms
    assert cmd.count_atoms('/') == cmd.count_atoms()
    assert cmd.count_atoms('/////') == cmd.count_atoms()

    # model
    assert cmd.count_atoms('/m1') == cmd.count_atoms('all')
    assert cmd.count_atoms('m1////') == cmd.count_atoms('all')

    # segi
    assert cmd.count_atoms('//Y') == cmd.count_atoms('segi Y')
    assert cmd.count_atoms('//Y+Z') == cmd.count_atoms('segi Y+Z')

    # chains
    assert cmd.count_atoms('///B') == cmd.count_atoms('chain B')
    assert cmd.count_atoms('///A+B') == cmd.count_atoms('chain A+B')

    # resn/resi
    assert cmd.count_atoms('////100') == cmd.count_atoms('resi 100')
    assert cmd.count_atoms('////`100') == cmd.count_atoms('resi 100')
    assert cmd.count_atoms('////100-110') == cmd.count_atoms('resi 100-110')
    assert cmd.count_atoms('////ARG`100') == cmd.count_atoms('resi 100')
    assert cmd.count_atoms('////ALA') == cmd.count_atoms('resn ALA')
    assert cmd.count_atoms('ALA/') == cmd.count_atoms('resn ALA')
    assert cmd.count_atoms('////ALA`') == cmd.count_atoms('resn ALA')
    assert cmd.count_atoms('////ALA+GLU') == cmd.count_atoms('resn ALA+GLU')

    # name/alt
    assert cmd.count_atoms('/////CG') == cmd.count_atoms('name CG')
    assert cmd.count_atoms('*/CG') == cmd.count_atoms('name CG')
    assert cmd.count_atoms('/////CG`B') == cmd.count_atoms('name CG & alt B')
    assert cmd.count_atoms('/////`B') == cmd.count_atoms('alt B')

    # combies
    assert cmd.count_atoms('100/CA') == cmd.count_atoms('resi 100 & name CA')
    assert cmd.count_atoms('A//CA') == cmd.count_atoms('chain A & name CA')
    assert cmd.count_atoms('A//`B') == cmd.count_atoms('chain A & alt B')
    assert cmd.count_atoms('/m1/Y/B/*/CA') == cmd.count_atoms('segi Y & chain B & name CA')

    # or-logic
    ref = cmd.count_atoms('(resi 100 & name CA) (resi 110 & name CB)')
    assert cmd.count_atoms('100/CA|110/CB') == ref
    assert cmd.count_atoms('100/CA or 110/CB') == ref
    assert cmd.count_atoms('100/CA 110/CB') == ref


def test_not_enabled():
    cmd.fragment('ala')
    cmd.fragment('arg')
    cmd.fragment('asp')

    cmd.fragment('gly')
    cmd.fragment('glu')

    cmd.delete('not a*')  # use "not " prefix

    assert cmd.get_names() == ['ala', 'arg', 'asp']

    cmd.disable('arg')
    cmd.delete('!enabled') # use "!" prefix

    assert cmd.get_names() == ['ala', 'asp']

    cmd.disable('asp')
    cmd.delete('enabled')

    assert cmd.get_names() == ['asp']


def test_protein_nucleic():
    npro = 340
    nnuc = 112
    cmd.load(testing.datafile("1oky-frag.pdb"), "1p")
    cmd.load(testing.datafile('1ehz-5.pdb'), "1n")
    assert cmd.count_atoms('polymer') == npro + nnuc
    assert cmd.count_atoms('polymer.protein') == npro
    assert cmd.count_atoms('polymer.nucleic') == nnuc


def test_wildcards():
    cmd.pseudoatom('foo')
    cmd.pseudoatom('foobar')
    cmd.pseudoatom('foo_bar')
    cmd.pseudoatom('foo_bar_bla')
    cmd.pseudoatom('bar')
    cmd.pseudoatom('_bar')
    assert 1 == cmd.count_atoms('foo')
    assert 1 == cmd.count_atoms('*foo')
    assert 4 == cmd.count_atoms('*foo*')
    assert 1 == cmd.count_atoms('bar')
    assert 4 == cmd.count_atoms('*bar')
    assert 5 == cmd.count_atoms('*bar*')
    assert 2 == cmd.count_atoms('foo*bar')
    assert 3 == cmd.count_atoms('*foo*bar*')
    assert 1 == cmd.count_atoms('_*')
    assert 6 == cmd.count_atoms('*')
    assert 6 == cmd.count_atoms('*')
    cmd.alter('*', 'name = "ABCD"')
    cmd.alter('foo', 'name = "ABED"')
    cmd.alter('bar', 'name = "ABEC"')
    assert 6 == cmd.count_atoms('name A*')
    assert 2 == cmd.count_atoms('name ABE*')
    assert 1 == cmd.count_atoms('name ABED*')
    assert 1 == cmd.count_atoms('name AB*C')
    assert 5 == cmd.count_atoms('name AB*C*')
    assert 5 == cmd.count_atoms('name AB*D')
    assert 5 == cmd.count_atoms('name AB*D*')


def test_wildcard_sets_ranges():
    for i in range(10): cmd.pseudoatom('m%d' % i, chain=chr(65 + i))
    cmd.alter('m5', 'chain = "AB"')
    cmd.alter('m6', 'chain = "BA"')
    cmd.alter('m7', 'chain = "CC"')
    cmd.alter('m8', 'chain = "ZA"')
    cmd.alter('m9', 'chain = "ABA"')
    # A patterns
    assert 1 == cmd.count_atoms('chain A')
    assert 3 == cmd.count_atoms('chain A*')
    assert 4 == cmd.count_atoms('chain *A')
    assert 5 == cmd.count_atoms('chain *A*')
    assert 1 == cmd.count_atoms('chain A*A')
    # B patterns
    assert 2 == cmd.count_atoms('chain B*')
    assert 2 == cmd.count_atoms('chain *B')
    assert 4 == cmd.count_atoms('chain *B*')
    # X patterns (no matches)
    assert 0 == cmd.count_atoms('chain X*')
    assert 0 == cmd.count_atoms('chain *X')
    assert 0 == cmd.count_atoms('chain *X*')
    # list with wildcards
    assert 5 == cmd.count_atoms('chain B*+A*')
    assert 3 == cmd.count_atoms('chain B*+A*A')
    assert 3 == cmd.count_atoms('chain B*+A*A+*X')

    # lexicographical alpha ranges, A:C, will match AB (A <= AB <= C) but not CC (C < CC)
    # no wildcards in alpha ranges possible
    assert 6 == cmd.count_atoms('chain A:C')
    assert 6 == cmd.count_atoms('chain A:CA')
    assert 7 == cmd.count_atoms('chain A:CX') # include CC
    assert 6 == cmd.count_atoms('chain A:C+Z')
    assert 7 == cmd.count_atoms('chain A:C+Z*')


def test_sets_ranges():
    cmd.fab('ACDEFGHIKL')
    cmd.alter('resi 9', 'resi="9A"') # insertion code
    assert 3 == cmd.count_atoms('guide & resi 2-4')
    assert 3 == cmd.count_atoms('guide & resi 2:4')
    assert 2 == cmd.count_atoms('guide & resi 2+4')
    assert 4 == cmd.count_atoms('guide & resi 2-4+6')
    assert 6 == cmd.count_atoms('guide & resi 2-4+6-8')
    assert 0 == cmd.count_atoms('guide & resi 9')
    assert 1 == cmd.count_atoms('guide & resi 9A')
    assert 1 == cmd.count_atoms('guide & resi 10')
    assert 0 == cmd.count_atoms('guide & resi 10A')
    assert 2 == cmd.count_atoms('guide & resi 9-10')
    assert 2 == cmd.count_atoms('guide & resi 9A-10A')
    assert 10 + 9 == cmd.count_atoms('name CA+CB')
    assert 10 + 9 == cmd.count_atoms('name CA+CB+XYZ')
    assert 10 == cmd.count_atoms('name C')
    assert 50 == cmd.count_atoms('name C*')
    assert 10 == cmd.count_atoms('name H')
    assert 24 == cmd.count_atoms('name H*')
    assert 10 == cmd.count_atoms('name *H')
    assert 74 == cmd.count_atoms('name *H*')
    assert 20 == cmd.count_atoms('name C+N')
    assert 23 == cmd.count_atoms('name C+N*')
    assert 60 == cmd.count_atoms('name C*+N')
    assert 63 == cmd.count_atoms('name C*+N*')


def test_guide():
    cmd.fragment("gly")
    assert 0 == cmd.count_atoms("organic")
    assert 1 == cmd.count_atoms("guide")
    assert 1 == cmd.count_atoms("organic | guide")


@pytest.mark.parametrize("op", ['origin', 'center'])
def test_dummy_selectors(op):
    assert cmd.count_atoms('all') == 0
    assert cmd.count_atoms(op) == 0
    assert cmd.count_atoms(op + ' around 2') == 0
    cmd.fragment('arg')
    assert cmd.count_atoms('all') == 24
    assert cmd.count_atoms(op) == 0
    assert cmd.count_atoms(op + ' around 2') == 8
    assert cmd.count_atoms(op + ' expand 2') == 8
    assert cmd.count_atoms(op + ' within 2 of arg') == 0
    assert cmd.count_atoms('arg within 2 of ' + op) == 8
    assert cmd.count_atoms('arg near_to 2 of ' + op) == 8
    assert cmd.count_atoms('arg beyond 3 of ' + op) == 13
    assert cmd.count_atoms(op + ' gap 3') == 5


def test_offcenter_origin_selector():
    cmd.fragment('arg')
    cmd.origin('elem O')
    assert cmd.count_atoms('origin around 2') == 2
    assert cmd.count_atoms('origin expand 2') == 2
    assert cmd.count_atoms('arg within 2 of origin') == 2
    assert cmd.count_atoms('arg near_to 2 of origin') == 2
    assert cmd.count_atoms('arg beyond 3 of origin') == 19
    assert cmd.count_atoms('origin gap 3') == 14
    # TODO Also test 'center' selector here. I'd expect that it gives the
    # same result as the test_dummy_selectors test, but numbers are
    # different!


# don't select center/origin with "all" keyword
def test_no_all_dummy_selection():
    cmd.pseudoatom('p1', pos=(-1, 0, 0))
    cmd.pseudoatom('p2', pos=(1, 0, 0))
    assert cmd.count_atoms('center around 1.5') == 2
    assert cmd.count_atoms('(p1|center) around 1.5') == 1
    assert cmd.count_atoms('all within 1.5 of center') == 2
    assert cmd.count_atoms('all within 1.5 of (all within 1.5 of p1)') == 1
    assert cmd.count_atoms('all within 1.5 of (center within 1.5 of p1)') == 2
    assert cmd.count_atoms('all near_to 1.5 of center') == 2
    assert cmd.count_atoms('all near_to 1.5 of (all near_to 1.5 of p1)') == 0
    assert cmd.count_atoms('all near_to 1.5 of (center near_to 1.5 of p1)') == 2
    _test_no_implicit_dummy_selection()


def _test_no_implicit_dummy_selection():
    assert cmd.count_atoms('(p1 around 1.5) around 1.5') == 0
