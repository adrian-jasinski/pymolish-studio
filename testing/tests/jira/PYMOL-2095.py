'''
PYMOL-2095
background in ray tracing not drawn properly

'''

import pytest
import os
from pymol import cmd, CmdException, testing, stored


@pytest.mark.parametrize("bg_gradient,opaque_background,hasColor", [(1,0,False), (1,1,True), (0,1,False)])

def test2095(bg_gradient, opaque_background, hasColor):
    cmd.load(testing.datafile("1oky-frag.pdb"))
    cmd.zoom(buffer=20)
    cmd.set("bg_gradient", bg_gradient)
    cmd.set("bg_rgb_top", "blue")
    cmd.set("bg_rgb_bottom", "blue")
    cmd.set("opaque_background", opaque_background)
    cmd.color("red")
    if hasColor:
        testing.assert_image_has_color('blue', testing.get_imagearray(width=100, height=100, ray=1))
    else:
        testing.assert_image_has_not_color('blue', testing.get_imagearray(width=100, height=100, ray=1))

