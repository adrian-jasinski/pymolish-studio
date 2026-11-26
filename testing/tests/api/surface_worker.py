"""
1b: a large surface that the window asks for is built on a thread of its
own ("async_surface", on): frames are drawn while it is built, and it is
there when it is ready. Whatever needs the whole scene, a ray-traced
picture for one, waits for it. Without a window nothing changes. The
window part needs the GUI:

    pymolish -kqy $PWD/testing/testing.py --run $PWD/testing/tests/api/surface_worker.py
"""

import time

from pymol import cmd, testing


def _large():
    """About 16,000 atoms: above the 5000 from which a build is its own
    thread, and a second or two to build."""
    cmd.load(testing.datafile("1aon.pdb.gz"), "m")
    cmd.remove("not chain A+B")
    cmd.hide("everything")
    assert cmd.count_atoms("m") > 5000


def _triangles():
    return cmd.get_povray()[1].count("mesh2")


def test_without_a_window_it_waits():
    assert cmd.get_setting_int("async_surface") == 1
    _large()
    cmd.show("surface")
    assert _triangles() > 10000  # (get_povray is the ray tracer's scene)


def _surface_pixels():
    """How much of the middle row of the viewport is drawn on."""
    from .label_render import viewport_pixels

    image = viewport_pixels().astype(int)
    row = image[image.shape[0] // 2]
    return int((row.sum(axis=1) > 60).sum())


@testing.requires("gui")
def test_window_draws_while_the_surface_is_built(request):
    request.addfinalizer(cmd.reinitialize)
    cmd.bg_color("black")
    _large()
    cmd.orient()
    assert _surface_pixels() == 0

    # the frames that follow "show" come at once and have no surface yet
    cmd.show("surface")
    start = time.time()
    assert _surface_pixels() == 0
    first_frame = time.time() - start
    frames = 1
    while _surface_pixels() == 0 and time.time() - start < 60:
        frames += 1
        time.sleep(0.05)
    built = time.time() - start
    assert _surface_pixels() > 50, "the surface never came"
    assert frames >= 3 and first_frame < built / 2, (frames, first_frame, built)

    # a ray-traced picture asked for while it is built waits for it
    cmd.set("surface_quality", -1)  # built again
    assert _surface_pixels() == 0  # a frame: the new build is running
    assert _triangles() > 5000
    assert _surface_pixels() > 50  # and the window has it too

    # an object deleted while its surface is built
    cmd.set("surface_quality", 0)
    assert _surface_pixels() == 0
    cmd.delete("m")
    time.sleep(3)  # the build ends and its result is dropped
    assert _surface_pixels() == 0 and cmd.get_names() == []

    # switched off: the frame after "show" has the surface, as before
    cmd.set("async_surface", 0)
    _large()
    cmd.orient()
    cmd.show("surface")
    assert _surface_pixels() > 50
