import pytest
from pymol import cmd, testing, stored
from chempy import cpv


def testAlign():
    cmd.load(testing.datafile("1oky-frag.pdb"), "m1")
    cmd.load(testing.datafile("1t46-frag.pdb"), "m2")
    cycles = 2
    r = cmd.align("m1", "m2", object="aln", cycles=cycles, transform=0)
    assert r[0] == pytest.approx(1.52563, abs=1e-4)
    assert r[1] == 177
    assert r[1] == cmd.count_atoms("aln") / 2
    assert r[2] == cycles


def testAlignto():
    cmd.fragment("gly", "m1")
    cmd.copy("m2", "m1")
    cmd.alignto(method="fit", mobile_state=1, target_state=1)


def testCealign():
    cmd.load(testing.datafile("1oky-frag.pdb"), "m1")
    cmd.load(testing.datafile("1t46-frag.pdb"), "m2")
    r = cmd.cealign("m2", "m1", object="aln")
    assert r["RMSD"] == pytest.approx(1.90375, abs=1e-4)
    alen = r["alignment_length"]
    assert alen == 40
    assert alen == cmd.count_atoms("aln") / 2


def testFit():
    cmd.fragment("gly", "m1")
    cmd.create("m2", "m1")
    rms = cmd.fit("m1", "m2")
    assert rms == 0.0
    rms = cmd.rms("m1", "m2")
    assert rms == 0.0
    rms = cmd.rms_cur("m1", "m2")
    assert rms == 0.0


def testIntraFit():
    cmd.fragment("gly", "m1")
    cmd.create("m1", "m1", 1, 2)
    rms_list = cmd.intra_fit("m1")
    testing.assert_array_equal(rms_list, [-1.0, 0.0])
    rms_list = cmd.intra_rms("m1")
    testing.assert_array_equal(rms_list, [-1.0, 0.0])
    rms_list = cmd.intra_rms_cur("m1")
    testing.assert_array_equal(rms_list, [-1.0, 0.0])


def testIntraRms():
    # see intra_fit
    pass


def testIntraRmsCur():
    # see intra_fit
    pass


def testPairFit():
    cmd.fragment('trp')
    cmd.fragment('his')

    # 1 atom
    sele = ('trp and guide', 'his and guide')
    pos = list(map(cmd.get_atom_coords, sele))
    vec = cpv.sub(*pos)
    mat_ref = [
        1.0, 0.0, 0.0, -vec[0],
        0.0, 1.0, 0.0, -vec[1],
        0.0, 0.0, 1.0, -vec[2],
        0.0, 0.0, 0.0, 1.0]
    rms = cmd.pair_fit(*sele)
    assert rms == 0.0
    mat = cmd.get_object_matrix('trp')
    testing.assert_array_equal(mat, mat_ref, 1e-4)

    # 2 atoms
    sele += ('trp & name CB', 'his & name CB')
    rms = cmd.pair_fit(*sele)
    assert rms == pytest.approx(0.0082, abs=1e-4)

    # 4 atoms
    sele += ('trp & name CG', 'his & name CG',
             'trp & name CD1', 'his & name CD2')
    rms = cmd.pair_fit(*sele)
    assert rms == pytest.approx(0.0713, abs=1e-4)


def testRms():
    # see fit
    pass


def testRmsCur():
    # see fit
    pass


def testSuper():
    cmd.load(testing.datafile("1oky-frag.pdb"), "m1")
    cmd.load(testing.datafile("1t46-frag.pdb"), "m2")
    r = cmd.super("m1", "m2", object="aln")
    assert r[0] == pytest.approx(0.9667, abs=1e-4)
    assert r[1] == 172
    assert r[1] == cmd.count_atoms("aln") / 2

