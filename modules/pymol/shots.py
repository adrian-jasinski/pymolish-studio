"""
Shot list: a movie as a list of steps. ``build`` turns the list into the
movie of the core with the commands that exist (mset, mview, mdo), so what
plays and what a session file stores is an ordinary PyMOL movie. The
timeline panel (pmg_qt/timeline.py) edits such a list; the list itself is
not stored anywhere (docs/plans/19-movie-timeline.md).

A shot is a dict:

    kind     scene, view, zoom, turn, rock, nutate, states or hold
    target   scene name (scene) or selection (zoom)
    seconds  how long the shot lasts
    start    smooth (slow in and out), linear, or cut (no camera flight)
    effect   one of EFFECTS, or ""
    view     the camera, for kind "view" (cmd.get_view)
    angle    degrees, for turn (360), rock (30) and nutate (15)
    axis     x, y or z, for turn and rock
"""

import math
import os
import tempfile
import time

cmd = __import__("sys").modules["pymol.cmd"]
from . import movie  # noqa: E402

KINDS = ("scene", "view", "zoom", "turn", "rock", "nutate", "states", "hold")
STARTS = ("smooth", "linear", "cut")
# name -> (global setting, value at the first frame, value at the last)
EFFECTS = {
    "fade in surface": ("transparency", 1.0, 0.0),
    "fade out surface": ("transparency", 0.0, 1.0),
    "fade in cartoon": ("cartoon_transparency", 1.0, 0.0),
    "fade out cartoon": ("cartoon_transparency", 0.0, 1.0),
}
FLIGHT = 2.0  # seconds the camera takes to reach a scene, view or selection
DEFAULT_SECONDS = {"turn": 8, "rock": 8, "nutate": 8, "states": 6, "hold": 2}


def shot(kind, target="", seconds=None, _self=cmd, **more):
    """A shot with the defaults filled in. A "view" takes the camera of now."""
    assert kind in KINDS, kind
    result = dict(
        kind=kind,
        target=target,
        seconds=float(seconds or DEFAULT_SECONDS.get(kind, 4)),
        start="smooth",
        effect="",
    )
    if kind == "view":
        result["view"] = _self.get_view()
    result.update(more)
    return result


def n_frames(shot, fps):
    return max(1, int(round(float(shot["seconds"]) * fps)))


def build(shots, _self=cmd):
    """
    Replace the movie by the shots. Returns the first frame of each shot.
    An empty list clears the movie.
    """
    cmd = _self
    fps = movie.get_movie_fps(cmd)
    counts = [n_frames(s, fps) for s in shots]
    cmd.mset()  # clears frames, keyframes and frame commands
    if not counts:
        return []
    cmd.mset("1 x%d" % sum(counts), freeze=1)
    starts = []
    first = 1
    for item, count in zip(shots, counts):
        starts.append(first)
        _apply(cmd, item, first, first + count - 1, fps)
        first += count
    cmd.mview("interpolate")
    cmd.frame(1)
    return starts


def _apply(cmd, shot, first, last, fps):
    kind = shot["kind"]
    target = shot.get("target", "")
    count = last - first + 1
    # power 1: constant speed through the keyframe; 0: slow in and out
    power = 1.0 if shot.get("start") == "linear" else 0.0

    def key(frame, **kw):
        cmd.mview("store", int(frame), power=kw.pop("power", power), freeze=1, **kw)

    # the frame at which the camera has arrived: the first one for a cut and
    # for the shot that opens the movie, else after the flight
    arrive = first
    if first > 1 and shot.get("start") != "cut":
        arrive = first + min(int(round(fps * FLIGHT)), (count - 1) // 2)

    if kind == "scene":
        cmd.scene(target, "recall", animate=0)
        key(arrive, scene=target)
        if last > arrive:
            key(last, scene=target)
    elif kind in ("view", "zoom"):
        if kind == "view":
            cmd.set_view(shot["view"])
        else:
            cmd.zoom(target or "all", animate=0)
        key(arrive)
        if last > arrive:
            key(last)
    elif kind == "hold":
        key(last)
    elif kind == "turn":
        angle = float(shot.get("angle", 360))
        axis = shot.get("axis", "y")
        steps = max(1, int(math.ceil(abs(angle) / 90.0)))
        key(first, power=1)
        for i in range(1, steps + 1):
            cmd.turn(axis, angle / steps)
            key(first + (i * (count - 1)) // steps, power=1)
    elif kind in ("rock", "nutate"):
        angle = float(shot.get("angle", 30 if kind == "rock" else 15)) / 2
        axis = shot.get("axis", "y")
        if kind == "rock":
            points = ((0.25, angle, 0), (0.75, -angle, 0), (1.0, 0, 0))
        else:  # a circle around the resting view
            points = (
                (0.2, angle, 0),
                (0.4, 0, angle),
                (0.6, -angle, 0),
                (0.8, 0, -angle),
                (1.0, 0, 0),
            )
        cycles = max(1, int(round(float(shot["seconds"]) / 4.0)))
        rest = cmd.get_view()
        key(first)
        for cycle in range(cycles):
            for part, a, b in points:
                cmd.set_view(rest)
                if kind == "rock":
                    cmd.turn(axis, a)
                else:
                    cmd.turn("x", a)
                    cmd.turn("y", b)
                key(first + ((cycle + part) * (count - 1)) / cycles)
        cmd.set_view(rest)
    elif kind == "states":
        key(first, state=1, power=1)
        key(last, state=max(1, cmd.count_states()), power=1)

    effect = EFFECTS.get(shot.get("effect"))
    if effect:
        setting, a, b = effect
        for frame in range(first, last + 1):
            t = (frame - first) / float(max(1, last - first))
            cmd.mdo(frame, "set %s, %.3f" % (setting, a + (b - a) * t))


def tour(what, _self=cmd):
    """
    Shots that visit places: "scenes" (one shot per scene), or "ligands",
    "chains" or "selections" (fly to each, then one turn around it).
    """
    cmd = _self
    if what == "scenes":
        return [shot("scene", name, _self=cmd) for name in cmd.get_scene_list()]
    if what == "ligands":
        seen = []
        cmd.iterate(
            "organic",
            'seen.append("/%s/%s/%s/%s`%s" % (model, segi, chain, resn, resi))',
            space={"seen": seen},
        )
        targets = list(dict.fromkeys(seen))
    elif what == "chains":
        targets = [
            "/%s//%s" % (model, chain)
            for model in cmd.get_object_list("polymer")
            for chain in cmd.get_chains("%s & polymer" % model)
        ]
    elif what == "selections":
        targets = cmd.get_names("public_selections")
    else:
        raise ValueError(what)
    shots = []
    for target in targets:
        shots.append(shot("zoom", target, 4, _self=cmd))
        shots.append(shot("turn", "", 6, _self=cmd))
    return shots


def describe(shots, _self=cmd):
    """A Python snippet that builds the same movie, for a script."""
    lines = ["from pymol import shots", "shots.build(["]
    lines += ["    %r," % (item,) for item in shots]
    lines.append("])")
    return "\n".join(lines)


def estimate(width=0, height=0, ray=0, _self=cmd):
    """
    What rendering the movie as PNG frames costs, measured on the frame
    shown now: (frames, seconds for all, bytes for all). Seconds and bytes
    are None when the frame could not be written here (no drawing context).
    """
    cmd = _self
    frames = cmd.count_frames()
    with tempfile.TemporaryDirectory() as folder:
        name = os.path.join(folder, "frame.png")
        start = time.time()
        try:
            cmd.png(name, width, height, ray=int(ray), quiet=1)
        except Exception:  # CmdException without a context
            return frames, None, None
        if not os.path.exists(name):
            return frames, None, None
        return frames, (time.time() - start) * frames, os.path.getsize(name) * frames
