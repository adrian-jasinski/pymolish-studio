'''
PYMOL-1233 Unable to color isomesh or isodot
'''

from pymol import cmd, testing

pytestmark = testing.requires('gui','shaders')


def _check_colors(*colors):
    for ray, shaders, cylinders in [
            (0,0,0),
            (0,1,0),
            (0,1,1),
            (1,1,1)]:
        cmd.set('use_shaders', shaders)
        cmd.set('mesh_as_cylinders', cylinders)
        img_array = testing.get_imagearray(ray=1)
        for color in colors:
            testing.assert_image_has_color(color, img_array)


def test():
    cmd.viewport(100,100)

    cmd.set('gaussian_b_floor', 20)
    cmd.set('ambient', 1)
    cmd.set('specular', 0)
    cmd.set('mesh_color', 'blue')
    cmd.set('dot_color', 'green')

    cmd.fragment('gly')
    cmd.map_new('map1')
    cmd.disable('*')

    cmd.isomesh('o1', 'map1')
    cmd.color('red', 'o1')
    cmd.show('cell')
    _check_colors('red', 'blue')
    cmd.delete('o1')
 
    cmd.isodot('o1', 'map1')
    cmd.color('red', 'o1')
    _check_colors('green')
    cmd.delete('o1')

    cmd.gradient('o1', 'map1')
    cmd.color('yellow', 'o1')
    _check_colors('yellow')
    cmd.delete('o1')
