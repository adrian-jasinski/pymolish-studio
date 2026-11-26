"""
A floor under the molecule: "stage". The ray tracer casts the molecule's
shadow on it, and with "mirror" a reflected copy of the molecule shows
through it. Plain geometry: a CGO plane and, for the mirror, copies of the
objects. The light comes from the looks of the preset menu ("top light",
"soft shadow", "studio").
"""

import pymol

cmd = __import__("sys").modules["pymol.cmd"]

FLOOR = "_floor"  # a leading underscore keeps a name out of the object list
MIRROR = "_mirror_"  # prefix of the reflected copies
MARGIN = 2.0  # the floor lies this far under the lowest atom
SIZE = 6.0  # its half-width, in sizes of what is shown
TILT = 20.0  # degrees the view is turned down, so the floor is seen
# The far edge of the floor would show as a line. Fog toward the background
# color hides it: the rear clipping plane goes back by the depth of the
# scene and the floor fades out before it gets there.
FOG = {"depth_cue": 1, "ray_trace_fog": 1, "fog_start": 0.5}
_state = {"tilt": 0.0, "clip": 0.0, "settings": {}}  # what "off" puts back


def _floor_color(_self):
    """The background color, a little darker; on a dark background a little
    lighter, so the floor reads as ground in both."""
    rgb = _self.get_color_tuple(_self.get("bg_rgb"))
    if sum(rgb) / 3 < 0.25:
        return [min(1.0, c + 0.10) for c in rgb]
    return [c * 0.94 for c in rgb]


def stage(mode="floor", selection="visible", quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "stage" puts a floor under what is shown. A ray-traced picture has
        the shadow of the molecule on it. With "mirror" a reflected copy of
        the molecule is seen through the floor, also in the viewport.

    USAGE

        stage [ mode [, selection ]]

    ARGUMENTS

        mode = floor, mirror or off {default: floor}

        selection = str: the atoms the floor is put under {default: visible}

    NOTES

        The floor is horizontal for the view of the moment: "down" is the
        bottom of the screen. The view is then tilted by 20 degrees so that
        the floor is seen; "stage off" removes floor and mirror and turns
        the view back. Run "stage" again after turning the molecule a lot
        or changing what is shown: nothing follows by itself. The viewport
        shows no shadow; Draw > Ray does. The floor fades into the
        background with distance (fog), so that its far edge does not show.

        "zoom" and "orient" without arguments count the floor: use the Zoom
        button of the toolbar, or "zoom visible".

    EXAMPLE

        stage
        preset.look("top light")
        ray
        stage mirror
        stage off
    """
    from . import cgo

    mode = str(mode).lower()
    if mode not in ("floor", "mirror", "off"):
        raise pymol.CmdException("stage: mode is floor, mirror or off")
    # always start clean: a second "stage" rebuilds for the new view
    _self.delete(FLOOR)
    _self.delete(MIRROR + "*")
    if _state["tilt"]:
        _self.clip("far", _state["clip"])
        _self.turn("x", -_state["tilt"])
        for key, value in _state["settings"].items():
            _self.set(key, value)
        _state.update(tilt=0.0, clip=0.0, settings={})
    if mode == "off":
        return
    import numpy

    xyz = _self.get_coords(selection)
    if xyz is None:
        raise pymol.CmdException("stage: nothing is shown")
    # the camera's axes in the coordinates of the molecule
    view = _self.get_view()
    right, up, toward = (numpy.array(view[i:9:3]) for i in range(3))
    height = float((xyz @ up).min()) - MARGIN
    center = xyz.mean(0)
    origin = center + (height - center @ up) * up
    half = float((xyz.max(0) - xyz.min(0)).max()) * SIZE
    corners = [
        origin + half * (a * right + b * toward)
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    plane = [cgo.BEGIN, cgo.TRIANGLES, cgo.COLOR, *_floor_color(_self), cgo.NORMAL, *up]
    for i in (0, 1, 2, 0, 2, 3):
        plane += [cgo.VERTEX, *corners[i]]
    plane.append(cgo.END)
    _self.load_cgo(plane, FLOOR, zoom=0)
    if mode == "mirror":
        normal = up
        for name in _self.get_object_list("(%s)" % selection):
            copy = MIRROR + name
            _self.create(copy, "%" + name, zoom=0)
            atoms = _self.get_coords(copy, state=0)
            depth = atoms @ normal - height
            _self.load_coords(atoms - 2 * depth[:, None] * normal[None, :], copy)
        _self.set("cgo_transparency", 0.25, FLOOR)
    _self.turn("x", TILT)
    view = _self.get_view()
    depth = view[16] - view[15]  # between the clipping planes
    _self.clip("far", -depth)
    _state.update(tilt=TILT, clip=depth, settings={k: _self.get(k) for k in FOG})
    for key, value in FOG.items():
        _self.set(key, value)
    if not int(quiet):
        print(" stage: %s under %d atoms; ray trace for the shadow" % (mode, len(xyz)))
