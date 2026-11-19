import os
import sys
from pymol import cmd, testing, stored


def testLoadAlnMatchingIds():
    cmd.fab('ACDEFGHIKLMNPQRS', 'seq1')
    cmd.fab('ACDIKLMNP', 'seq2')
    cmd.fab('GHIKPQRS', 'seq3')
    cmd.load(testing.datafile('alignment.aln'), 'aln')
    assert cmd.count_atoms('guide & aln & seq1') == 11
    assert cmd.count_atoms('guide & aln & seq2') == 7
    assert cmd.count_atoms('guide & aln & seq3') == 6


def testLoadAlnMappingStr():
    cmd.fab('ACDEFGHIKLMNPQRS', 'm1')
    cmd.fab('ACDIKLMNP', 'm2')

    from pymol.seqalign import load_aln_multi

    load_aln_multi(testing.datafile('alignment.aln'), 'aln', mapping=
        'seq1 m1 '
        'seq2 m2 '
    )

    assert cmd.count_atoms('guide & aln & m1') == 7
    assert cmd.count_atoms('guide & aln & m2') == 7


def testLoadAlnMappingDict():
    cmd.fab('ACDIKLMNP', 'm2')
    cmd.fab('GHIKPQRS', 'm3')

    from pymol.seqalign import load_aln_multi

    load_aln_multi(testing.datafile('alignment.aln'), 'aln', mapping={
        'seq2': 'm2',
        'seq3': 'm3',
    })

    assert cmd.count_atoms('guide & aln & m2') == 2
    assert cmd.count_atoms('guide & aln & m3') == 2
