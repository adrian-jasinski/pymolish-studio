"""
15b: the viewport draws the outline of a look (ray_trace_mode 1 to 3)
while viewport_outline is on, in the color the ray tracer uses: black on a
light background, white on a dark one. Found in the depth of the picture
(fxaa.fs). Needs the GUI:

    pymolish -kqy $PWD/testing/testing.py --run $PWD/testing/tests/api/viewport_outline.py
"""

import pytest

from pymol import cmd, preset, testing


def test_setting():
    assert cmd.get_setting_int("viewport_outline") == 1  # on, with a look
    # every look with an outline says so through ray_trace_mode alone
    for name, settings in preset.LOOKS.items():
        assert "viewport_outline" not in settings, name


def _pixels():
    from .label_render import viewport_pixels

    cmd.turn("z", 1)  # an unchanged scene is not drawn again
    cmd.turn("z", -1)
    return viewport_pixels().astype(int)


@testing.requires("gui")
def test_outline_in_the_viewport(request):
    request.addfinalizer(cmd.reinitialize)
    cmd.set("use_shaders", 1)
    cmd.set("antialias_shader", 0)
    cmd.fragment("trp", "m")
    cmd.color("red")
    cmd.bg_color("white")
    preset.space_filling("m")
    cmd.orient()
    preset.look("flat")  # plain colors: every other tone is a line

    def count(image):
        r, g, b = image.transpose(2, 0, 1)
        red = ((r > 240) & (g < 30) & (b < 30)).sum()
        black = ((r < 60) & (g < 60) & (b < 60)).sum()
        white = ((r > 240) & (g > 240) & (b > 240)).sum()
        return int(red), int(black), int(white)

    red, black, white = count(_pixels())
    assert red > 5000 and white > 5000
    assert black > 500, "no outline in the viewport"
    cmd.set("viewport_outline", 0)
    assert count(_pixels())[1] == 0
    preset.look("default")  # no look: no outline, whatever the switch
    plain = _pixels()
    cmd.set("viewport_outline", 1)
    changed = (abs(_pixels() - plain) > 40).any(axis=2).mean()
    assert changed < 0.001, changed  # (two frames differ in a few pixels)

    # a line drawing: nothing but lines on the background
    preset.look("sketch")
    red, black, white = count(_pixels())
    assert red == 0 and black > 500 and white > 5000
    # on a dark background the line is light
    preset.look("flat")
    cmd.bg_color("black")
    red, black, white = count(_pixels())
    assert red > 5000 and white > 500 and black > 5000

    # with smoothed edges too, and a label gets no frame
    cmd.bg_color("white")
    cmd.set("antialias_shader", 1)
    assert count(_pixels())[1] > 500
    cmd.set("antialias_shader", 0)
    before = count(_pixels())[1]
    cmd.set("label_size", 30)
    cmd.set("label_color", "red")
    cmd.pseudoatom("far", pos=[30, 0, 0], label="HIH")  # beside the atoms
    cmd.hide("everything", "far")
    cmd.show("labels", "far")
    cmd.zoom("m | far")
    count(_pixels())  # the first frame can come before the glyph texture
    red_only = count(_pixels())
    cmd.hide("labels")
    assert red_only[1] == pytest.approx(count(_pixels())[1], abs=20)
    assert before > 0
