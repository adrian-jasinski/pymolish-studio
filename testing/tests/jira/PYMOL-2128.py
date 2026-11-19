'''
background during stereo doesn't change
'''

import os
from pymol import cmd, CmdException, testing, stored

pytestmark = testing.requires('gui')


def test():
    cmd.set('bg_rgb', 'red')
    cmd.stereo('anaglyph')
    testing.assert_image_has_color('red')
