"""
GUI frame-time baseline. Needs a display and a real OpenGL context. Run with
an absolute path and without pymolrc:

    pymolish -qk $PWD/testing/bench_gui.py

For each representation of 1aon: the first frame after "show" (representation
build + upload), then FRAMES warm frames while rotating. A frame is one
PyMOL draw (CPU submission) followed by glFinish (GPU completion); it is
drawn outside Qt's paint cycle, so display synchronization is not included.
Then IDLE seconds of doing nothing: CPU use, timer wakeups, repaints.
Prints a markdown table and quits.
"""

import os
import statistics
import subprocess
import sys
import time

import pymol.gui
from pymol import cmd
from pymol.Qt import QtCore

FRAMES = 300
IDLE = 5
# pymol execs scripts in its own namespace, so __file__ is not this file
HERE = os.path.dirname(os.path.abspath(sys.argv[-1]))
widget = pymol.gui.get_qtwindow().pymolwidget
rows = []
info = {}
idle = {"wakeups": 0, "repaints": 0, "cpu": 0.0}


def frame(gl):
    t0 = time.perf_counter()
    widget.pymol.draw()
    t1 = time.perf_counter()
    gl.glFinish()
    return time.perf_counter() - t0, t1 - t0


def measure():
    gl = widget.context().functions()
    info["renderer"] = gl.glGetString(0x1F01)  # GL_RENDERER
    scale = widget.devicePixelRatio()
    info["size"] = f"{int(widget.width() * scale)}x{int(widget.height() * scale)}"
    cmd.load(os.path.join(HERE, "data", "1aon.pdb.gz"), "m")
    for rep in ("lines", "sticks", "spheres", "cartoon", "surface"):
        cmd.show_as(rep)
        first = frame(gl)[0]
        samples = []
        for _ in range(FRAMES):
            cmd.turn("y", 3)
            samples.append(frame(gl))
        total = sorted(s[0] for s in samples)
        cut = statistics.quantiles(total, n=100)
        rows.append(
            (
                rep,
                first,
                statistics.median(total),
                cut[94],
                cut[98],
                total[-1],
                statistics.median(s[1] for s in samples),
            )
        )
        print(f"  {rep}: {statistics.median(total) * 1e3:.1f} ms", file=sys.stderr)
    cmd.show_as("cartoon")


def start():
    cmd._call_with_opengl_context(measure)
    widget._timer.timeout.connect(
        lambda: idle.__setitem__("wakeups", idle["wakeups"] + 1)
    )
    widget.frameSwapped.connect(
        lambda: idle.__setitem__("repaints", idle["repaints"] + 1)
    )
    # let the redraws caused by the measurement settle before counting
    QtCore.QTimer.singleShot(2000, idle_begin)


def idle_begin():
    idle.update(wakeups=0, repaints=0, cpu=time.process_time())
    QtCore.QTimer.singleShot(IDLE * 1000, finish)


def finish():
    cpu = (time.process_time() - idle["cpu"]) / IDLE * 100
    commit = subprocess.run(
        ["git", "-C", HERE, "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    print(
        f"\nCommit {commit}, PyMOL {cmd.get_version()[0]}, {info['renderer']}, "
        f"viewport {info['size']} px, 1aon (58870 atoms), {FRAMES} frames per row\n"
    )
    print(
        "| Representation | first frame | median | p95 | p99 | max | draw calls (median) |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for rep, first, *times in rows:
        print(
            f"| {rep} | {first:.2f} s | "
            + " | ".join(f"{t * 1e3:.1f} ms" for t in times)
            + " |"
        )
    print(
        f"\nIdle, cartoon shown, {IDLE} s: {cpu:.1f} % of one core, "
        f"{idle['wakeups'] / IDLE:.0f} timer wakeups/s, {idle['repaints'] / IDLE:.1f} repaints/s"
    )
    cmd.quit()


QtCore.QTimer.singleShot(1000, start)
