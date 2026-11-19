from pymol import cmd, testing


# fixed in 1.8.2.4 and 1.8.4.2

pytestmark = testing.requires('incentive')


def test():
    cmd.load(testing.datafile('subblock.mae'))
    assert 5 == cmd.count_atoms()
