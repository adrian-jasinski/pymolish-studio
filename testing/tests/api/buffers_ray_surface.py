"""
Paths of the ray tracer, the surface, the mesh and the maps whose scratch
buffers got an automatic owner (step 8c) and that no other test entered.
"""

import numpy
import pytest

from pymol import cmd, testing


def _red_ball():
    cmd.pseudoatom("m", vdw=3.0)
    cmd.show_as("spheres")
    cmd.color("red")
    cmd.orient()
    cmd.set("bg_rgb", "white")
    cmd.set("opaque_background", 1)
    testing.ambient_only()


@pytest.mark.parametrize("antialias", [0, 1, 2, 3, 4])
def test_ray_antialias(antialias):
    """From 2 on the picture is traced larger and folded down by threads."""
    _red_ball()
    cmd.set("antialias", antialias)
    img = testing.get_imagearray(width=40, height=30, ray=1)
    assert img.shape[:2] == (30, 40)
    testing.assert_image_has_color("red", img)
    testing.assert_image_has_color("white", img)


@pytest.mark.parametrize("mode", [1, 2, 3])
def test_ray_trace_mode_outline(mode):
    """The outline is found in a buffer of depth slopes: it is black."""
    _red_ball()
    cmd.set("ray_trace_mode", mode)
    img = testing.get_imagearray(width=40, height=30, ray=1)
    testing.assert_image_has_color("black", img, delta=40)


def test_mesh_rep():
    cmd.fragment("gly", "m")
    cmd.show_as("mesh")
    assert "cylinder" in cmd.get_povray()[1]
    cmd.set("cavity_cull", 0)
    assert "cylinder" in cmd.get_povray()[1]


def test_mesh_without_solvent_dots():
    """No atom takes part: the cavity pass has no dot to start from."""
    cmd.fragment("gly", "m")
    cmd.flag("ignore", "all")
    cmd.show_as("mesh")
    assert "cylinder" not in cmd.get_povray()[1]


def test_surface_as_ray_traced_mesh():
    """surface_type 2: every edge of the triangles once."""
    cmd.fragment("gly", "m")
    cmd.show_as("surface")
    solid = cmd.get_povray()[1]
    cmd.set("surface_type", 2)
    mesh = cmd.get_povray()[1]
    edges, triangles = mesh.count("cylinder"), solid.count("vertex_vectors")
    # a closed surface has 1.5 edges per triangle
    assert triangles and edges == pytest.approx(1.5 * triangles, rel=0.05)


@pytest.mark.parametrize("mode", [1, 2, 3])
def test_surface_ambient_occlusion_recolor(mode):
    """Occluded parts of the surface get darker; mode 3 counts per atom."""
    cmd.fragment("gly", "m")
    cmd.orient()
    cmd.show_as("surface")
    cmd.color("red")
    testing.ambient_only()
    plain = testing.get_imagearray(width=40, height=30, ray=1)
    cmd.set("ambient_occlusion_mode", mode)
    shaded = testing.get_imagearray(width=40, height=30, ray=1)
    assert plain[..., 0].max() == 255
    assert 200 < shaded[..., 0].max() < 255
    assert (shaded[..., 1:3] == 0).all()


def test_map_set_from_a_moved_map():
    """The points are taken back through the matrix of the source map."""
    cmd.fragment("gly", "m")
    cmd.set("gaussian_b_floor", 30)
    cmd.map_new("src", "gaussian", 1.0, "m", 4.0)
    cmd.map_new("dst", "gaussian", 1.0, "m", 4.0)
    still = numpy.array(cmd.get_volume_field("src", copy=1))
    # two grid steps along x
    cmd.transform_object("src", [1, 0, 0, 2, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
    cmd.map_set("dst", "copy", "src")
    moved = numpy.array(cmd.get_volume_field("dst", copy=1))
    assert still.max() > 1
    assert numpy.allclose(moved[2:], still[:-2], atol=1e-4)
    assert not numpy.allclose(moved, still, atol=1e-4)
