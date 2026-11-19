'''
negative b-factor in MAE file.
'''

from pymol import cmd, testing, stored

pytestmark = testing.requires('incentive')


def test():
    cmd.load("PYMOL-1514.mae")
    b_list = []
    cmd.iterate("all", "b_list.append(b)", space=locals())
    testing.assert_array_equal(b_list, [-1.0, -1.0, -2.3, 2.86], 0.001)
