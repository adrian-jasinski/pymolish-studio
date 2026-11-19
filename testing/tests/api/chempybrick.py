import pytest
from chempy import cpv
from pymol import cmd, testing, stored


def test():
    try:
        import numpy
    except ImportError:
        pytest.skip('requires numpy')

    from chempy.brick import Brick

    spacing = (.5, .5, .5)
    origin = (3., 4., 5.)
    shape = (10, 10, 10)
    range_ =  [a * (b - 1) for (a, b) in zip (spacing, shape)]

    data = numpy.zeros(shape, float)

    brick = Brick.from_numpy(data, spacing, origin)
    testing.assert_array_equal(brick.range, range_)

    cmd.load_brick(brick, 'map')

    extent = cmd.get_extent('map')
    testing.assert_array_equal(extent, [origin, cpv.add(origin, range_)])
