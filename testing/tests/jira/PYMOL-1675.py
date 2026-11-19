'''
anaglyph draw
'''

import os
from pymol import cmd, CmdException, testing, stored

pytestmark = testing.requires('gui')


def test():
    cmd.set('suspend_updates')
    cmd.set('depth_cue', 0)
    cmd.set('ambient', 1)
    cmd.set('specular', 0)
    cmd.set('stereo_angle', 10)
    cmd.pseudoatom()
    cmd.show_as('sphere')
    cmd.zoom()
    cmd.stereo('anaglyph')
    cmd.set('suspend_updates', 0)

    wh = (40, 40)
    cmd.draw(*wh, antialias=0)
    cmd.sync()

    img = testing.get_imagearray(prior=1)
    assert wh == img.shape[:2]

    # ray tracing and shaders in PyMOL 1.7.6+:
    # 0xe50000
    # 0x00e5e5
    # -> delta=26 (0x1a)

    testing.assert_image_has_color('0xff0000', img, delta=0x1a)
    testing.assert_image_has_color('0x00ffff', img, delta=0x1a)
