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


@testing.requires("gui")
def test_glow_in_the_viewport(request):
    """15p, an experiment: "glow" lays a halo in the colors of what is
    drawn around it. The background far from the molecule stays, the
    molecule itself stays, and 0 (the default) draws none."""
    request.addfinalizer(cmd.reinitialize)
    assert cmd.get_setting_float("glow") == 0
    cmd.set("use_shaders", 1)
    cmd.fragment("trp", "m")
    cmd.color("red")
    cmd.bg_color("black")
    preset.space_filling("m")
    cmd.orient()
    cmd.zoom("m", 12)  # room for the halo
    preset.look("flat")
    cmd.set("viewport_outline", 0)

    def count(image):
        r, g, b = image.transpose(2, 0, 1)
        red = (r > 240) & (g < 30) & (b < 30)
        halo = (r > 40) & (r <= 240) & (g < 30) & (b < 30)  # dimmer reds
        return int(red.sum()), int(halo.sum()), image[:8, :8].max()

    red, halo, corner = count(_pixels())
    assert red > 2000 and halo < red / 20 and corner == 0
    preset.glow(1)  # the row of Presets > light
    red_glow, halo, corner = count(_pixels())
    assert red_glow == pytest.approx(red, rel=0.06)  # the atoms as they were
    assert halo > red / 2 and corner == 0  # around them, not everywhere
    cmd.set("glow", 0.5)
    assert red / 8 < count(_pixels())[1] < halo
    preset.glow(0)
    assert count(_pixels())[1] < red / 20


def _png_pixels(path, **kwargs):
    from pymol.Qt import QtGui
    import numpy

    cmd.png(str(path), ray=0, quiet=1, **kwargs)
    image = QtGui.QImage(str(path)).convertToFormat(QtGui.QImage.Format.Format_RGB888)
    rows = numpy.frombuffer(image.constBits(), numpy.uint8)
    rows = rows.reshape(image.height(), image.bytesPerLine())[:, : image.width() * 3]
    return rows.reshape(image.height(), image.width(), 3).astype(int)


@testing.requires("gui")
def test_glow_and_outline_in_sized_pictures(request, tmp_path):
    """15q: a picture of another size (Draw (fast), png with a width) gets
    the post-process of the window: the halo, as the same share of the
    picture, and the outline of a look."""
    request.addfinalizer(cmd.reinitialize)
    cmd.set("use_shaders", 1)
    cmd.set("opaque_background", 1)
    cmd.fragment("trp", "m")
    cmd.color("red")
    cmd.bg_color("black")
    preset.space_filling("m")
    cmd.orient()
    cmd.zoom("m", 12)
    preset.look("flat")
    cmd.set("viewport_outline", 0)

    def halo_share(image):
        r, g, b = image.transpose(2, 0, 1)
        return ((r > 40) & (r <= 240) & (g < 30) & (b < 30)).mean()

    window = _pixels()
    height, width = window.shape[:2]
    for antialias in (0, 2):
        cmd.set("antialias", antialias)
        sized = _png_pixels(tmp_path / "plain.png", width=2 * width)
        assert sized.shape[:2] == (2 * height, 2 * width)
        assert halo_share(sized) < 0.002
        preset.glow(1)
        share = halo_share(_pixels())
        sized = _png_pixels(tmp_path / "glow.png", width=2 * width)
        assert share > 0.01
        assert halo_share(sized) == pytest.approx(share, rel=0.1), antialias
        preset.glow(0)

    # the outline of a look, white on black
    cmd.set("viewport_outline", 1)
    sized = _png_pixels(tmp_path / "outline.png", width=2 * width)
    white = (sized.min(axis=2) > 200).sum()
    assert white > 2000, "no outline in a sized picture"
