'''
Bonds to symmetry mates
'''

from pymol import cmd, testing


def test_commands():
    sym = [5, 2, 3, 60, 90, 90, 'P M 1 1']
    cmd.set('orthoscopic')
    cmd.set('stick_ball')
    cmd.set('stick_ball_color', 'blue')
    cmd.pseudoatom('m1', name='A1', pos=(0.5, 0, 0))
    cmd.pseudoatom('m1', name='A2', pos=(2, 2, 0.5))
    cmd.pseudoatom('m1', name='A3', pos=(2, 2, 2.0))
    cmd.set_symmetry('m1', *sym)
    cmd.bond('name A1', 'name A1', symop="2_555")
    cmd.bond('name A2', 'name A3')
    cmd.valence(1, 'name A2', '*', symop="1_564")
    cmd.color('red')
    cmd.color('0x00cc00', 'name A2')
    cmd.color('yellow', 'name A3')
    cmd.show_as('sticks')
    cmd.viewport(200, 200)
    cmd.set_view((0., 1., 0., 0., 0., 1., 1., 0., 0., -0.223610640,
                  -0.169926167, -10.333316803, 1., 1., 1., 6., 13., 20.))
    testing.ambient_only()
    # the reference is from x86 Linux; arm64 macOS ray traces a few edge
    # pixels differently (73 values of 160000), so allow 50 pixels. A
    # missing bond is thousands.
    testing.assert_image_equal("symop-ref/bond_symop.png", count=50)

    m = cmd.get_model()
    assert m.bond[0].symmetry_2 == "2_555"
    assert m.bond[1].symmetry_2 == "1_564"

    # load model
    cmd.delete('*')
    cmd.load_model(m, 'm2', zoom=0)
    cmd.set_symmetry('m2', *sym)
    cmd.color('red')
    cmd.color('0x00cc00', 'name A2')
    cmd.color('yellow', 'name A3')
    cmd.show_as('sticks')
    testing.assert_image_equal("symop-ref/bond_symop.png", count=50)

    # load session
    for binary in (0, 1):
        cmd.set_session(cmd.get_session(binary=binary))
        testing.assert_image_equal("symop-ref/bond_symop.png", count=50)
