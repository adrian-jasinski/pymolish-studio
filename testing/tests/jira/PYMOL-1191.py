'''
PYMOL-1191
MOE 2012 surfaces
'''

from pymol import cmd, testing, stored

pytestmark = testing.requires('incentive')


def testLoadMOE2012():
    cmd.load(testing.datafile('benzene.moe.gz'))

    v = cmd.get_names()
    assert 'benzene.system' not in v
    assert 'benzene.chain_1' in v
    assert 'benzene.Quick_Surface_Ligand_' in v
