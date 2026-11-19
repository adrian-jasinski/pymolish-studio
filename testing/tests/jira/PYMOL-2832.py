import pytest
from pymol import cmd, testing


@pytest.mark.parametrize("ribbon_as_cylinders", [1, 0])
def test(ribbon_as_cylinders):
    cmd.set('ribbon_as_cylinders', ribbon_as_cylinders)
    cmd.set('ribbon_width', 8)
    cmd.fab('AG')
    cmd.color('red', 'resn ALA')
    cmd.color('blue', 'resn GLY')
    cmd.show_as('ribbon')
    cmd.orient()

    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.draw(100, 100)
    img = testing.get_imagearray()
    testing.assert_image_has_color('red', img)
    testing.assert_image_has_color('blue', img)
