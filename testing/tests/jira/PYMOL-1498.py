'''
MAE sticks representation
'''

from pymol import cmd, testing, stored

pytestmark = testing.requires('incentive')


def test():
    cmd.load(testing.datafile("repr.mae"))

    assert 60 == cmd.count_atoms('repr.x_lines and rep lines')
    assert 60 == cmd.count_atoms('repr.x_sticks and rep sticks')
    
    assert 60 == cmd.count_atoms('repr.x_cartoon and rep cartoon')
    assert 60 == cmd.count_atoms('repr.x_cart_lines and rep cartoon')
    assert 60 == cmd.count_atoms('repr.x_cart_lines and rep lines')

    assert 60 == cmd.count_atoms('repr.x_spheres and rep spheres')
    assert 60 == cmd.count_atoms('repr.x_thinsticks and rep sticks')
    
    assert 60 == cmd.count_atoms('repr.x_ballstick and rep sticks')
