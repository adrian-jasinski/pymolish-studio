'''
crash with mesh w/o map
'''

from pymol import cmd, CmdException, testing, stored


def test():
    cmd.viewport(100, 100)

    # make map
    cmd.fragment('gly', 'm1')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.map_new('map')
    cmd.delete('m1')

    # make mesh 
    cmd.isomesh('mesh', 'map')

    # check mesh presence by color
    meshcolor = 'red'
    cmd.color(meshcolor, 'mesh')
    testing.ambient_only()
    testing.assert_image_has_color(meshcolor)

    # continue without map
    cmd.delete('map')

    with testing.mktemp('.pse') as filename:
        cmd.save(filename)

        cmd.delete('*')
        testing.assert_image_has_not_color(meshcolor)

        cmd.load(filename)
        testing.assert_image_has_color(meshcolor)

