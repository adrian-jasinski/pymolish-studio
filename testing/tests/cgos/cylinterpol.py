'''
Test ramp color interpolation along a cylinder
'''

from pymol import cmd, testing, stored


def test():
    cmd.viewport(200, 100)

    cmd.fragment('ethylene', 'm1')
    cmd.remove('hydro')
    cmd.pseudoatom('p1', 'index 1')
    cmd.disable('p1')
    cmd.ramp_new('r1', 'p1', [0.1, 1.2], ['red', 'blue'])
    cmd.disable('r1')
    cmd.color('r1')
    cmd.show_as('sticks', 'm1')

    cmd.orient('m1')
    cmd.move('z', 11)

    testing.ambient_only()

    img = testing.get_imagearray()

    testing.assert_image_has_color('red', img)
    testing.assert_image_has_color('blue', img)
    testing.assert_image_has_color([.5, .0, .5], img, delta=1)
