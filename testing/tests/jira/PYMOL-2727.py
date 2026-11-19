'''
missing residues
'''

import pytest
from pymol import cmd, CmdException, testing, stored


def _get_seq(selection):
    from pymol.exporting import _resn_to_aa as one_letter
    prev_resi = [None]
    seq = []
    def callback(resi, resn):
        if resi == prev_resi[0]:
            return
        prev_resi[0] = resi
        seq.append(one_letter[resn])
    cmd.iterate(selection, 'callback(resi, resn)', space=locals())
    return ''.join(seq)


@pytest.mark.parametrize("use_auth", (0, 1))
@pytest.mark.parametrize("filename", ('1hbb_pdbx_seq_one_letter_code.cif', '1hbb_entity_poly_seq.cif'))
def testMissingRes(use_auth, filename):
    cmd.set('cif_use_auth', use_auth)
    cmd.load(testing.datafile(filename), '1hbb')

    seq = _get_seq('segi A')
    assert seq == 'VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR'

    seq = _get_seq('segi B')
    assert seq == 'VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH'
    


def testMissingResIns():
    # label_seq_id 10-19 can't be inserted (without insertion codes)
    cmd.load(testing.datafile('1hbb_pdbx_seq_one_letter_code-ins.cif'), '1hbb')

    seq = _get_seq('segi A')
    assert seq == 'VLSPADKTNHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR'


def testMissingResInsScheme():
    # With _pdbx_poly_seq_scheme, missing residues with insertion codes
    # should be inserted correctly (GH #303)
    cmd.set('cif_use_auth', 1)
    cmd.load(testing.datafile('1hbb_pdbx_seq_one_letter_code-ins-scheme.cif'), '1hbb')

    seq = _get_seq('segi A')
    assert seq == 'VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR'
