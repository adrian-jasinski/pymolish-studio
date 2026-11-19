import os
from pymol import cmd, testing


def _load_example():
    # object in hidden group
    cmd.fragment('ile', 'm1')
    cmd.fragment('his', 'm2')
    cmd.group('g1', 'm1')
    cmd.disable('g1')

    # testable styling
    testing.ambient_only()
    cmd.orient()
    cmd.color('red', 'm1')
    cmd.color('blue', 'm2')
    cmd.show_as('spheres')


def test_scenes():
    _load_example()

    cmd.scene('s1', 'store')
    cmd.enable('g1')
    cmd.scene('s2', 'store')
    cmd.mset('1x4')
    cmd.mview('store', 1, scene='s2')
    cmd.mview('store', 4, scene='s1')

    with testing.mkdtemp() as tempdir:
        # export
        prefix = os.path.join(tempdir, 'frame')
        cmd.mpng(prefix, width=100, height=100)

        img = testing.get_imagearray(prefix + '0002.png')
        testing.assert_image_has_color('red', img)
        testing.assert_image_has_color('blue', img)

        img = testing.get_imagearray(prefix + '0003.png')
        testing.assert_image_has_not_color('red', img)
        testing.assert_image_has_color('blue', img)


def test_mdo():
    _load_example()

    cmd.mset('1x3')
    cmd.mdo(1, 'disable m1')
    cmd.mdo(2, 'enable m1')
    cmd.mdo(3, 'enable g1')

    with testing.mkdtemp() as tempdir:
        # export
        prefix = os.path.join(tempdir, 'frame')
        cmd.mpng(prefix, width=100, height=100)

        img = testing.get_imagearray(prefix + '0001.png')
        testing.assert_image_has_not_color('red', img)
        testing.assert_image_has_color('blue', img)

        img = testing.get_imagearray(prefix + '0002.png')
        testing.assert_image_has_not_color('red', img)
        testing.assert_image_has_color('blue', img)

        img = testing.get_imagearray(prefix + '0003.png')
        testing.assert_image_has_color('red', img)
        testing.assert_image_has_color('blue', img)
