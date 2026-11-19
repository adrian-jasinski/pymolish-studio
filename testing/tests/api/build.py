"""
Testing PyQt Fab & Builder
"""
from pymol import cmd, testing


def testCanInit():
    assert cmd.fnab("A") == None


def testSingleDNAFASTA():
    dna = "ATGC"
    cmd.fnab(input=dna, mode="DNA", form="B", dbl_helix=-1)
    fasta_str = cmd.get_fastastr().splitlines()
    assert dna == fasta_str[1]


def testSingleRNAFASTA():
    rna = "AUGC"
    cmd.fnab(input=rna, mode="RNA")
    fasta_str = cmd.get_fastastr().splitlines()
    assert rna == fasta_str[1]


def testDoubleDNAFASTA():
    dna = "ATCCCCG"
    revcomp = "CGGGGAT"
    cmd.fnab(input=dna, dbl_helix=1)
    fasta_str = cmd.get_fastastr().splitlines()
    fasta_raw = (fasta_str[1], fasta_str[3])
    sense_strand = fasta_raw[0]
    antisense_strand = fasta_raw[1]
    assert dna == sense_strand
    assert revcomp == antisense_strand
    cmd.delete('all')
    cmd.fnab(input=dna)
    fasta_str = cmd.get_fastastr().splitlines()
    fasta_raw = (fasta_str[1], fasta_str[3])
    sense_strand = fasta_raw[0]
    antisense_strand = fasta_raw[1]
    assert dna == sense_strand
    assert revcomp == antisense_strand


def testDoubleRNAFASTA():
    rna = "AUUUUUUUCG"
    cmd.fnab(input=rna, mode="RNA", form="B", dbl_helix=1)

    fasta_str = cmd.get_fastastr().splitlines()
    assert len(fasta_str) == 2        
    sense_strand = fasta_str[1]
    assert rna == sense_strand


def testMixedCase():
    dna = "AtG"
    revcomp = "CAT"
    cmd.fnab(input=dna)

    fasta_str = cmd.get_fastastr().splitlines()
    fasta_raw = (fasta_str[1], fasta_str[3])
    sense_strand = fasta_raw[0]
    antisense_strand = fasta_raw[1]
    assert dna.upper() == sense_strand
    assert revcomp == antisense_strand
