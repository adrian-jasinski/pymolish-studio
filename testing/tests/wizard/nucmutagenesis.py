'''
unit tests for pymol.wizard.nucmutagenesis
'''

import pytest
import os
import sys
import tempfile

from pymol import cmd, testing


def test_CanGetSourceSequence():
    cmd.load(testing.datafile("1rna.cif"))
    seq = cmd.get_fastastr('/1rna/A/A').splitlines()[1]
    assert seq == "UUAUAUAUAUAUAA"


def test_CanGetFragment():
    cmd.fragment("gtp")
    numAtoms = cmd.count_atoms("gtp")
    assert numAtoms == 48


def test_CanInit():
    cmd.wizard("nucmutagenesis")
    assert cmd.get_wizard() != None


def test_CorrectChiDihedral():
    cmd.load(testing.datafile("1rna.cif"))
    src_dihedral = cmd.get_dihedral("/1rna/A/A/14 & name O4'",
                                    "/1rna/A/A/14 & name C1'",
                                    "/1rna/A/A/14 & name N9",
                                    "/1rna/A/A/14 & name C4'")
    cmd.wizard("nucmutagenesis")
    cmd.select("/1rna/A/A/14")
    cmd.get_wizard().mode = "Guanine"
    cmd.get_wizard().do_select("sele")
    cmd.get_wizard().apply()
    des_dihedral = cmd.get_dihedral("/1rna/A/A/14 & name O4'",
                                    "/1rna/A/A/14 & name C1'",
                                    "/1rna/A/A/14 & name N9",
                                    "/1rna/A/A/14 & name C4'")
    assert src_dihedral == pytest.approx(des_dihedral, abs=2.0)


def test_CanGetNewRNASequence():
    cmd.load(testing.datafile("1rna.cif"))
    cmd.wizard("nucmutagenesis")
    cmd.select("/1rna/A/A/14")
    cmd.get_wizard().mode = "Guanine"
    cmd.get_wizard().do_select("sele")
    cmd.get_wizard().apply()
    seq = cmd.get_fastastr("/1rna/A/A").splitlines()[1]
    assert seq == "UUAUAUAUAUAUAG"


def test_CanGetNewDNASequence():
    cmd.load(testing.datafile("1bna.cif"))
    cmd.wizard("nucmutagenesis")
    cmd.select("/1bna/A/A/1")
    cmd.get_wizard().mode = "Adenine"
    cmd.get_wizard().do_select("sele")
    cmd.get_wizard().apply()
    seq = cmd.get_fastastr("/1bna/A/A").splitlines()[1]
    assert seq == "AGCGAATTCGCG"


def test_CanMutateNonCanonicalNucleo():
    cmd.load(testing.datafile("1k5e.cif"))
    cmd.wizard("nucmutagenesis")
    cmd.select("/1k5e/A/A/6")
    cmd.get_wizard().mode = "Adenine"
    cmd.get_wizard().do_select("sele")
    cmd.get_wizard().apply()
    seq = cmd.get_fastastr("/1k5e/A/A").splitlines()[1]
    assert seq == "CGGACAAGAAG"
