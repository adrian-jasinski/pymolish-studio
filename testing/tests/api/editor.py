'''
Testing: pymol.editor
'''

import pytest
from pymol import cmd, testing, stored, editor


# fab(input, name=None, mode='peptide', resi=1, chain='', segi='',
# state=-1, dir=1, hydro=-1, ss=0, async=-1, quiet=1)
#
# The only valid mode is 'peptide'.

def testSimple():
    cmd.fab('AA')
    v = cmd.get_object_list()
    assert v == ['obj01']


def testAdvanced():
    cmd.fab('A/123/ ADC B/234/ AFCD')

    v = cmd.get_chains()
    assert v == ['A', 'B']

    cmd.iterate('last chain B', 'stored.v = (resv, resn)')
    assert stored.v == (237, 'ASP')


def testIdentifiers():
    seq = 'ACD'
    segi = 'foo'
    chain = 'F'
    resv = 10
    cmd.fab(seq, 'm1', 'peptide', resv, chain, segi)

    cmd.iterate('first m1', 'stored.v = (segi, chain, resv, resn)')
    assert stored.v == (segi, chain, resv, 'ALA')

    cmd.iterate('last m1', 'stored.v = (segi, chain, resv, resn)')
    assert stored.v == (segi, chain, resv + 2, 'ASP')

    v = cmd.get_fastastr().splitlines()[1]
    assert v == seq


def testDir():
    seq = 'ACD'
    resv = 5
    cmd.fab(seq, 'm1', resi=resv, dir=-1)

    # incentive needs sort, opensource is already sorted
    cmd.sort()

    cmd.iterate('first m1', 'stored.v = (resv, resn)')
    assert stored.v == (resv - 2, 'ASP')


@pytest.mark.parametrize("seq", ['AA', 'A'])
def testHydro(seq):
    cmd.fab(seq, hydro='0')
    v = cmd.count_atoms('hydro')
    assert 0 == v, 'failed to remove hydrogens on ' + seq


@pytest.mark.parametrize("ss", range(5))
def testSS(ss):
    cmd.fab('AAAPAAA', 'm1', ss=ss)

