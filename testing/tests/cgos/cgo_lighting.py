import pytest
from pymol.cgo import *
import pymol
from pymol import cmd, testing, stored


@pytest.mark.parametrize("has_normal", [(0),(1)])
@testing.requires('gui')
# if normals are set, then object's cgo_lighting should be set
def test_cgo_lighting_setting(has_normal):
    objname = 'simpletri'
    obj = []
    if has_normal:
        obj.extend([NORMAL, 0., 0., 1.])
    obj.extend([
        BEGIN, TRIANGLES,
        COLOR, 1.0, 0., 0.,
        VERTEX, 0.0, 0.0, 0.0,
        VERTEX, 1.0, 0.0, 0.0,
        VERTEX, 0.0, 1.0, 0.0,
        END
        ])
    cmd.load_cgo(obj,objname,1)
    cgo_lighting = cmd.get('cgo_lighting', objname)
    assert int(cgo_lighting) == int(has_normal)


@pytest.mark.parametrize("use_shader", (0,1))
@pytest.mark.parametrize("has_normal", (0,1))
@pytest.mark.parametrize("two_sided_lighting", (0,1))
@pytest.mark.parametrize("backface_cull", (0,1))
@pytest.mark.parametrize("cgo_lighting", (0,1))
@pytest.mark.parametrize("back", (0,1))
@testing.requires('gui')
def testBackfaceLighting(use_shader, has_normal, two_sided_lighting, backface_cull, cgo_lighting, back):
    viewport = (50, 50)
    cmd.viewport(*viewport)

    objname = 'simpletri'
    obj = []
    if has_normal: # specifies a normal
        obj.extend([NORMAL, 0., 0., 1.])
    obj.extend([
        BEGIN, TRIANGLES,
        COLOR, 1.0, 0., 0.,
        VERTEX, 0.0, 0.0, 0.0,
        VERTEX, 1.0, 0.0, 0.0,
        VERTEX, 0.0, 1.0, 0.0,
        END
        ])
    cmd.load_cgo(obj,objname,1)

    cmd.set('use_shader', use_shader)
    cmd.set('two_sided_lighting', two_sided_lighting)
    cmd.set('backface_cull', backface_cull)
    cmd.set('cgo_lighting', cgo_lighting, objname)

    cmd.set('depth_cue', 0)
    cmd.set('antialias', 0)
    cmd.set('light_count', 1)

    if back:
        cmd.turn("y", 180)

    # to see the images
    #        cmd.png("%d__%d_%d_%d_%d_%d_%d_test.png" % (back and backface_cull, use_shader, has_normal, two_sided_lighting, backface_cull, cgo_lighting, back))
    img = testing.get_imagearray(width=viewport[0], height=viewport[1])
    if not two_sided_lighting and not backface_cull and cgo_lighting and back:
        # this is where a shaded back side is rendered
        redmask = (img[:,:,0] > 0)
        assert ((img[:,:,0][redmask] < 255).any() and
                        (img[:,:,1:3][redmask] == 0).all())
    elif back and backface_cull:
        testing.assert_image_has_not_color('red', img=img)
    else:
        testing.assert_image_has_color('red', img=img)

