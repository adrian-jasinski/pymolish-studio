from pymol import cmd, CmdException, testing, stored


def test():
    cmd.pseudoatom('m1')
    cmd.mset('1x1')
    cmd.create('m2', 'm1')
    cmd.ray()
    v = cmd.get_object_matrix('m2')
    testing.assert_array_equal(v, [
        1., 0., 0., 0.,
        0., 1., 0., 0.,
        0., 0., 1., 0.,
        0., 0., 0., 1.,
        ], 0.001, 'object matrix not identity')
