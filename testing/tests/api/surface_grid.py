"""
The grid surface (surface_type 7, plan 1b; "Solid (grid)" in Setting >
Surface): the molecular surface from two distance grids and marching cubes.
It must lie where the surface of triangulated dots lies, with the settings
of a surface too.
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


def test_carving_and_the_solvent_surface_follow_the_dots(peptide):
    whole, triangles = vertices(7)
    cmd.select("site", "resi 3")
    cmd.set("surface_carve_selection", "site")
    cmd.set("surface_carve_cutoff", 5.0)
    dots, grid = vertices(0)[0], vertices(7)
    assert 0 < grid[1] < triangles / 2  # only what lies near residue 3
    assert apart(grid[0], dots).max() < 1.5 and apart(dots, grid[0]).max() < 1.5
    cmd.set("surface_carve_cutoff", 0)

    cmd.set("surface_solvent", 1)  # where the center of the probe gets to
    dots, grid = vertices(0)[0], vertices(7)[0]
    assert apart(grid, dots).max() < 1.5 and apart(dots, grid).max() < 1.5
    gap = apart(grid, whole)
    assert 1.0 < gap.mean() < 1.8, gap.mean()  # a probe radius farther out


@pytest.fixture
def shell():
    """A hollow ball of 70 atoms: a closed cavity of about 180 A3."""
    turn = numpy.pi * (3 - 5**0.5)
    for i in range(70):
        z = 1 - 2 * (i + 0.5) / 70
        r = (1 - z * z) ** 0.5
        place = 5.5 * numpy.array([r * numpy.cos(i * turn), r * numpy.sin(i * turn), z])
        cmd.pseudoatom("m", pos=place.tolist(), vdw=2.0)
    cmd.set("surface_mode", 1)  # pseudoatoms count
    cmd.hide("everything")
    cmd.show("surface")
    cmd.orient()


def test_closed_cavities_are_culled_or_shown_alone(shell):
    cmd.set("cavity_cull", 0)
    both, triangles = vertices(7)  # the ball and the cavity in it
    cmd.set("cavity_cull", 10)  # 25 A3: this cavity is larger and stays
    assert vertices(7)[1] == triangles
    cmd.set("cavity_cull", 100)  # 250 A3: it goes
    ball, ball_triangles = vertices(7)
    cavity_triangles = triangles - ball_triangles
    assert 0.05 * triangles < cavity_triangles < 0.3 * triangles
    assert numpy.all(apart(ball, both) == 0)  # the ball itself is untouched

    cmd.set("cavity_cull", 0)
    cmd.set("surface_cavity_cutoff", -2)
    cmd.set("surface_cavity_mode", 1)  # cavities and pockets only
    cavity, found = vertices(7)
    assert found == cavity_triangles
    assert apart(cavity, ball).min() > 3  # the other side of a wall of 4 A
    dots = vertices(0)[0]
    assert apart(cavity, dots).max() < 1.5 and apart(dots, cavity).max() < 1.5
    cmd.set("surface_cavity_mode", 2)  # the same, culled
    assert vertices(7)[1] == found
    cmd.set("cavity_cull", 100)
    assert vertices(7)[1] == 0
