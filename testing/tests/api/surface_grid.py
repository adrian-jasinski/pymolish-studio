"""
The grid surface (surface_type 7, an experiment of plan 1b): the molecular
surface from two distance grids and marching cubes. It must lie where the
surface of triangulated dots lies.
"""

import re

import numpy
import pytest

from pymol import cmd


def vertices(kind, probe=1.4):
    """The corners of the surface triangles, each once, in camera space."""
    cmd.set("surface_type", kind)
    cmd.set("solvent_radius", probe)
    text = cmd.get_povray()[1]
    blocks = re.findall(r"vertex_vectors \{ 3,([^}]*)\}", text)
    found = re.findall(r"<([^,>]+),([^,>]+),([^,>]+)>", " ".join(blocks))
    corners, triangles = numpy.array(found, float).reshape(-1, 3), len(blocks)
    assert len(corners) == 3 * triangles
    return numpy.unique(corners.round(3), axis=0), triangles


def facing(kind):
    """+1 or -1 per triangle: does the order of its corners turn about its
    normals? The viewport lights the side that it takes for the front."""
    cmd.set("surface_type", kind)
    text = cmd.get_povray()[1]

    def vectors(name):
        blocks = re.findall(name + r" \{ 3,([^}]*)\}", text)
        found = re.findall(r"<([^,>]+),([^,>]+),([^,>]+)>", " ".join(blocks))
        return numpy.array(found, float).reshape(-1, 3, 3)

    corners, normals = vectors("vertex_vectors"), vectors("normal_vectors")
    turn = numpy.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
    return numpy.sign((turn * normals.sum(1)).sum(1))


def apart(a, b):
    """For each point of a, the distance to the nearest point of b."""
    return numpy.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1).min(1))


@pytest.fixture
def peptide():
    cmd.fab("ACDEFGHIKLMNPQ", "m")
    cmd.hide("everything")
    cmd.show("surface")
    cmd.orient()


def test_lies_on_the_surface_of_dots(peptide):
    dots, dot_triangles = vertices(0)
    grid, grid_triangles = vertices(7)
    # about as many triangles: the cells are two point separations wide
    assert 0.5 < grid_triangles / dot_triangles < 2
    for a, b in ((grid, dots), (dots, grid)):  # nothing missing, nothing more
        gap = apart(a, b)
        assert gap.mean() < 0.4 and gap.max() < 1.5, (gap.mean(), gap.max())
    assert numpy.array_equal(vertices(7)[0], grid)  # the same at every build
    # triangles turn the way those of the dots do: else the viewport draws
    # the surface dark, lit from its inside
    side = facing(0).mean()
    assert abs(side) > 0.95 and facing(7).mean() * side > 0.95


def test_follows_probe_quality_and_what_is_shown(peptide):
    grid, triangles = vertices(7)
    round_, round_triangles = vertices(7, probe=3.0)  # a larger probe: rounder
    assert 0 < round_triangles < triangles
    # the dots of a large probe are far apart, so a point of the grid
    # surface has farther to its nearest dot (0.61 A here) on the same surface
    gap = apart(round_, vertices(0, probe=3.0)[0])
    assert gap.mean() < 1.0 and gap.max() < 2.5, (gap.mean(), gap.max())
    cmd.set("surface_quality", 1)  # cells of half the size
    assert vertices(7)[1] > 3 * triangles
    cmd.set("surface_quality", 0)
    cmd.hide("surface", "resi 1-7")
    part, part_triangles = vertices(7)
    assert 0 < part_triangles < triangles
    # a part of the same surface; the grid starts at the atoms that are
    # shown, so its points are other points of that surface
    assert apart(part, grid).max() < 1.0
    cmd.hide("surface")
    assert vertices(7)[1] == 0
