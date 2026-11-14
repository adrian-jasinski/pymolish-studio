"""
Atom labels are text in their own color in the OpenGL viewport.

With use_shaders on and a driver without geometry shaders (Mesa), every
character was a solid block in the color of whatever was drawn before it.
Needs the GUI:

    pymolish -kqy $PWD/testing/testing.py --run $PWD/testing/tests/api/label_render.py
"""

import numpy

from pymol import cmd, testing


def viewport_pixels():
    """What the OpenGL widget draws. cmd.png would ray trace instead."""
    import pymol.gui
    from pymol.Qt import QtGui

    widget = pymol.gui.get_qtwindow().pymolwidget
    image = cmd._call_in_gui_thread(widget.grabFramebuffer)
    image = image.convertToFormat(QtGui.QImage.Format.Format_RGB888)
    rows = numpy.frombuffer(image.constBits(), numpy.uint8)
    rows = rows.reshape(image.height(), image.bytesPerLine())
    return rows[:, : image.width() * 3].reshape(image.height(), image.width(), 3)


class TestLabelRender(testing.PyMOLTestCase):
    @testing.requires("gui")
    def test_label_has_its_own_color(self):
        cmd.set("use_shaders", 1)
        cmd.fragment("ala")
        cmd.show_as("lines")
        cmd.color("green")
        cmd.set("label_color", "magenta")
        cmd.set("label_size", 30)
        cmd.label("name CA", "'HIH'")
        cmd.orient()

        for _ in range(3):  # the first frame can come before the glyph texture
            cmd.turn("z", 1)  # an unchanged scene is not drawn again
            r, g, b = viewport_pixels().astype(int).transpose(2, 0, 1)
            magenta = (r > 150) & (b > 150) & (g < 100)
            if magenta.any():
                break
        self.assertGreater(magenta.sum(), 50, "label not drawn in its color")
        rows = magenta.any(axis=1).nonzero()[0]
        cols = magenta.any(axis=0).nonzero()[0]
        box = magenta[rows[0] : rows[-1] + 1, cols[0] : cols[-1] + 1]
        # the strokes of "HIH" cover about a third of its box; blocks nearly all
        self.assertLess(box.mean(), 0.6)
