'''
some stick_ball caps missing
'''

import pytest
import pymol
from pymol import cmd, util, testing, stored


def test():
    if not (pymol.invocation.options.no_gui or cmd.get_setting_int('use_shaders')):
        pytest.skip('no ray or shaders')

    testing.ambient_only()
    cmd.set('valence', 0)

    cmd.viewport(350, 200)
    cmd.fragment('ile')
    cmd.remove('hydro')
    cmd.show_as('sticks')
    cmd.orient()

    cmd.set('stick_ball', 0)
    img1 = testing.get_imagearray()

    cmd.set('stick_ball', 1)
    img2 = testing.get_imagearray()

    testing.assert_image_equal(img1, img2, count=10)
