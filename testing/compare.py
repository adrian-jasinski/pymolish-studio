"""
Compare pymolish with upstream PyMOL 3 on the same workloads, same machine.
Run from the repository root:

    pymolish -ckqy testing/compare.py            # headless workloads
    pymolish -ckqy testing/compare.py -- gui     # also GUI frame times

The reference is $PYMOL_REF, default ~/code/pymol-open-source/.venv/bin/pymol.
Each version runs this file as a worker in its own process, without pymolrc,
with the same settings. Prints a markdown table (best of REPEAT runs, ratio
pymolish / pymol3) and ray-traced image differences; the PNGs stay in the
printed output directory for a look. Exit code 1 when a workload gives a
different result (atom count, RMSD, selection size) in the two versions.
For GUI rows under WSLg, set GALLIUM_DRIVER=d3d12 to use the GPU.

Besides the single-object rows (1oky, 1aon, 1aon x4), STRUCTURES are timed
one by one for load, cartoon, surface and a PSE round trip, and all of them
together in one PSE. They are downloaded once from RCSB into CACHE.
Results and the reading of them: docs/benchmark.md.
"""

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time

from pymol import cmd

REPEAT = 3
FRAMES = 60
REPS = ("lines", "sticks", "spheres", "cartoon", "ribbon", "surface", "mesh", "dots")
SMALL = (
    "1rx1.pdb",
    "1oky.pdb.gz",
    "2cas.pdb.gz",
    "1t46-frag.pdb",
    "1bna.cif",
    "1k5e.cif",
    "1rna.cif",
    "1pup.cif",
)
# 327 to 239306 atoms: small proteins, a GPCR, hemoglobin, an antibody, a
# nucleosome (DNA), the spike trimer, GroEL, two ribosomes (RNA)
STRUCTURES = (
    "1crn",
    "1ubq",
    "2rh1",
    "4hhb",
    "1hzh",
    "1aoi",
    "6vxx",
    "1aon",
    "1jj2",
    "4v6x",
)
CACHE = os.path.expanduser("~/.cache/pymolish-compare")
# argv is pymol's own without "--" and the script's after it
SCRIPT = os.path.abspath(next(a for a in sys.argv if a.endswith(".py")))
DATA = os.path.join(os.path.dirname(SCRIPT), "data")


def path(name):
    return os.path.join(DATA, name)


# ---------------------------------------------------------------- worker, CLI


def reset():
    cmd.reinitialize()
    cmd.set("max_threads", os.cpu_count())


def cli_workloads(tmp):
    """(name, setup, run, result, repeat); result is compared between versions."""
    big, huge = path("1aon.pdb.gz"), os.path.join(tmp, "huge.cif")
    many = sorted(
        os.path.join(tmp, "many", f) for f in os.listdir(os.path.join(tmp, "many"))
    )
    pse = os.path.join(tmp, "w.pse")
    atoms = lambda: cmd.count_atoms()
    w: list = [
        (
            "load small 1oky (2475 atoms)",
            None,
            lambda: cmd.load(path("1oky.pdb.gz")),
            atoms,
            REPEAT,
        ),
        ("load big 1aon (58870 atoms)", None, lambda: cmd.load(big), atoms, REPEAT),
        (
            "load huge 4x1aon mmCIF (235480 atoms)",
            None,
            lambda: cmd.load(huge),
            atoms,
            1,
        ),
        (
            f"load {len(many)} files, one object each",
            None,
            lambda: [cmd.load(f) for f in many],
            lambda: (len(cmd.get_names()), atoms()),
            1,
        ),
    ]
    for label, f, repeat in (
        ("small", "1oky.pdb.gz", REPEAT),
        ("big", "1aon.pdb.gz", 1),
    ):
        for rep in REPS:
            # headless PyMOL builds representations lazily; a tiny ray forces it
            w.append(
                (
                    f"build {rep} {label} (+ray 16x16)",
                    lambda f=f: cmd.load(path(f)),
                    lambda rep=rep: (cmd.show_as(rep), cmd.ray(16, 16)),
                    None,
                    repeat,
                )
            )
    for rep in ("lines", "cartoon", "surface"):
        w.append(
            (
                f"build {rep} huge (+ray 16x16)",
                lambda: cmd.load(huge),
                lambda rep=rep: (cmd.show_as(rep), cmd.ray(16, 16)),
                None,
                1,
            )
        )
    w += [
        (
            "ray 800x600 cartoon big",
            lambda: (cmd.load(big), cmd.show_as("cartoon")),
            lambda: cmd.ray(800, 600),
            None,
            REPEAT,
        ),
        (
            "ray 800x600 surface small",
            lambda: (cmd.load(path("1oky.pdb.gz")), cmd.show_as("surface")),
            lambda: cmd.ray(800, 600),
            None,
            REPEAT,
        ),
        (
            "switch 9 objects x3 (cartoon, +ray 64x48)",
            switch_setup,
            switch_run,
            None,
            REPEAT,
        ),
        (
            "trajectory load 2cas + 60-frame DCD",
            lambda: cmd.load(path("2cas.pdb.gz")),
            lambda: cmd.load_traj(path("2cas.dcd"), "2cas"),
            cmd.count_states,
            REPEAT,
        ),
        (
            "trajectory play 60 states (lines, +ray 64x48)",
            traj_setup,
            lambda: [(cmd.frame(i), cmd.ray(64, 48)) for i in range(1, 61)],
            None,
            REPEAT,
        ),
        (
            "select byres within 5 of chain A (big)",
            lambda: cmd.load(big),
            lambda: cmd.select("s", "byres (all within 5 of chain A)"),
            lambda: cmd.count_atoms("s"),
            REPEAT,
        ),
        (
            "align 1aon chain A onto chain H",
            align_setup,
            lambda: cmd.align("a", "h"),
            lambda: round(cmd.align("a", "h")[0], 2),
            REPEAT,
        ),
        (
            "dss (big)",
            lambda: cmd.load(big),
            cmd.dss,
            lambda: cmd.count_atoms("ss H"),
            REPEAT,
        ),
        ("h_add (big)", lambda: cmd.load(big), cmd.h_add, atoms, 1),
        (
            "alter b=b*1 + iterate (big)",
            lambda: cmd.load(big),
            lambda: (cmd.alter("all", "b=b*1"), cmd.iterate("all", "pass")),
            None,
            REPEAT,
        ),
        (
            "get_coords x10 (huge)",
            lambda: cmd.load(huge),
            lambda: [cmd.get_coords() for _ in range(10)],
            None,
            REPEAT,
        ),
        (
            "save mmCIF (big)",
            lambda: cmd.load(big),
            lambda: cmd.save(os.path.join(tmp, "w.cif")),
            None,
            REPEAT,
        ),
        (
            "save PSE (big, cartoon)",
            lambda: (cmd.load(big), cmd.show_as("cartoon")),
            lambda: cmd.save(pse),
            None,
            REPEAT,
        ),
        ("load PSE (big, cartoon)", None, lambda: cmd.load(pse), atoms, REPEAT),
    ]
    for i, pdb in enumerate(STRUCTURES):
        f, pse_i = cached(pdb), os.path.join(tmp, f"{pdb}.pse")
        repeat = REPEAT if i < 6 else 1  # the last four have 24k to 239k atoms
        load = lambda f=f: cmd.load(f)
        w += [
            (f"{pdb}/load", None, load, atoms, repeat),
            (
                f"{pdb}/cartoon",
                load,
                lambda: (cmd.show_as("cartoon"), cmd.ray(16, 16)),
                None,
                repeat,
            ),
            (
                f"{pdb}/surface",
                load,
                lambda: (cmd.show_as("surface"), cmd.ray(16, 16)),
                None,
                repeat,
            ),
            (
                f"{pdb}/save PSE",
                lambda load=load: (load(), cmd.show_as("cartoon")),
                lambda pse_i=pse_i: cmd.save(pse_i),
                None,
                repeat,
            ),
            (
                f"{pdb}/load PSE",
                None,
                lambda pse_i=pse_i: cmd.load(pse_i),
                atoms,
                repeat,
            ),
        ]
    pse_all = os.path.join(tmp, "all.pse")
    load_all = lambda: [cmd.load(cached(p)) for p in STRUCTURES]
    w += [
        (f"all {len(STRUCTURES)}/load", None, load_all, atoms, 1),
        (
            f"all {len(STRUCTURES)}/cartoon",
            load_all,
            lambda: (cmd.show_as("cartoon"), cmd.ray(16, 16)),
            None,
            1,
        ),
        (
            f"all {len(STRUCTURES)}/save PSE",
            lambda: (load_all(), cmd.show_as("cartoon")),
            lambda: cmd.save(pse_all),
            None,
            1,
        ),
        (f"all {len(STRUCTURES)}/load PSE", None, lambda: cmd.load(pse_all), atoms, 1),
    ]
    return w


def cached(pdb):
    return os.path.join(CACHE, f"{pdb}.cif.gz")


def switch_setup():
    for f in SMALL + ("1aon.pdb.gz",):
        cmd.load(path(f))
    cmd.show_as("cartoon")


def switch_run():
    for _ in range(3):
        for name in cmd.get_names():
            cmd.disable("all")
            cmd.enable(name)
            cmd.orient(name)
            cmd.ray(64, 48)


def align_setup():
    cmd.load(path("1aon.pdb.gz"), "m")
    cmd.create("a", "m and chain A")
    cmd.create("h", "m and chain H")


def traj_setup():
    cmd.load(path("2cas.pdb.gz"))
    cmd.load_traj(path("2cas.dcd"), "2cas")
    cmd.show_as("lines")


def run_cli(out):
    tmp = os.path.dirname(out)
    rows = {}
    for name, setup, run, result, repeat in cli_workloads(tmp):
        times = []
        for _ in range(repeat):
            reset()
            if setup:
                setup()
            t0 = time.perf_counter()
            run()
            times.append(time.perf_counter() - t0)
        rows[name] = {"time": min(times), "result": result() if result else None}
        print(f"  {name}: {min(times):.3f} s", file=sys.stderr)
    # images for a visual check: same view, same size, ray-traced
    for rep in REPS:
        reset()
        cmd.load(path("1oky.pdb.gz"))
        cmd.show_as(rep)
        cmd.orient()
        cmd.png(os.path.join(tmp, f"{rep}.png"), 480, 360, ray=1)
    return rows


# ---------------------------------------------------------------- worker, GUI


def run_gui(out):
    import ctypes

    import pymol.gui
    from pymol.Qt import QtCore, QtWidgets

    gl = ctypes.CDLL("libGL.so.1")
    widget = pymol.gui.get_qtwindow().pymolwidget
    rows = {}
    tmp = os.path.dirname(out)

    def frame():
        t0 = time.perf_counter()
        widget.pymol.draw()
        gl.glFinish()
        return time.perf_counter() - t0

    def row(name, t, result=None):
        rows[name] = {"time": t, "result": result}
        print(f"  {name}: {t * 1e3:.1f} ms", file=sys.stderr)

    def reps(label, f, which):
        cmd.reinitialize()
        cmd.load(f, "m")
        for rep in which:
            cmd.show_as(rep)
            row(f"GUI first frame {rep} {label}", frame())
            samples = []
            for _ in range(FRAMES):
                cmd.turn("y", 3)
                samples.append(frame())
            row(f"GUI frame {rep} {label} (median)", statistics.median(samples))

    def measure():
        rows["_viewport"] = {"time": 0, "result": cmd.get_viewport()}
        cmd.set("max_threads", os.cpu_count())
        reps("small", path("1oky.pdb.gz"), REPS)
        reps(
            "big",
            path("1aon.pdb.gz"),
            ("lines", "sticks", "spheres", "cartoon", "surface"),
        )
        reps("huge", os.path.join(tmp, "huge.cif"), ("lines", "spheres", "cartoon"))

        for pdb in STRUCTURES:
            cmd.reinitialize()
            cmd.load(cached(pdb))
            for rep in ("cartoon", "surface"):
                cmd.show_as(rep)
                row(f"{pdb}/{rep} first frame", frame())
            samples = [(cmd.turn("y", 3), frame())[1] for _ in range(FRAMES // 3)]
            row(f"{pdb}/surface frame (median)", statistics.median(samples))

        cmd.reinitialize()
        switch_setup()
        cmd.disable("all")
        names = cmd.get_names()
        passes = []
        for _ in range(3):
            samples = []
            for name in names:
                cmd.disable("all")
                cmd.enable(name)
                cmd.orient(name)
                samples.append(frame())
            passes.append(samples)
        row("GUI switch 9 objects, first pass (sum)", sum(passes[0]))
        row(
            "GUI switch 9 objects, later passes (median)",
            statistics.median(passes[1] + passes[2]),
        )

        cmd.reinitialize()
        many = os.path.join(tmp, "many")
        t0 = time.perf_counter()
        for f in sorted(os.listdir(many)):
            cmd.load(os.path.join(many, f))
        QtWidgets.QApplication.processEvents()
        frame()
        row(
            f"GUI load {len(os.listdir(many))} files + frame",
            time.perf_counter() - t0,
            len(cmd.get_names()),
        )
        samples = [(cmd.turn("y", 3), frame())[1] for _ in range(FRAMES)]
        row(
            f"GUI frame {len(os.listdir(many))} objects lines (median)",
            statistics.median(samples),
        )

    def start():
        cmd._call_with_opengl_context(measure)
        write(out, rows)
        cmd.quit()

    def resized():
        QtCore.QTimer.singleShot(1500, start)

    cmd.viewport(800, 600)
    QtCore.QTimer.singleShot(1500, resized)


def write(out, rows):
    rows["_version"] = {"time": 0, "result": cmd.get_version()[0]}
    with open(out, "w") as f:
        json.dump(rows, f)


# ---------------------------------------------------------------- driver


def make_inputs(tmp):
    """huge.cif: 1aon four times, shifted; many/: 600 copies of 8 small files."""
    cmd.reinitialize()
    for i in range(4):
        cmd.load(path("1aon.pdb.gz"), f"c{i}")
        cmd.alter(f"c{i}", f"chain = chain + '{i}'")
        cmd.translate([200.0 * i, 0, 0], f"c{i}", camera=0)
    cmd.create("huge", "all")
    cmd.save(os.path.join(tmp, "huge.cif"), "huge")
    os.mkdir(os.path.join(tmp, "many"))
    for f in SMALL:
        cmd.reinitialize()
        cmd.load(path(f), "m")
        for i in range(75):
            cmd.save(os.path.join(tmp, "many", f"{f.split('.')[0]}_{i:02}.pdb"), "m")
    cmd.reinitialize()


# pymolish exports its own data paths; the reference must find its own
ENV = {
    k: v
    for k, v in os.environ.items()
    if k not in ("PYMOL_PATH", "PYMOL_DATA", "PYMOL_SCRIPTS", "TUT")
}


def run_worker(exe, mode, tmp):
    os.mkdir(tmp)
    for name in ("huge.cif", "many"):
        os.symlink(os.path.join(os.path.dirname(tmp), name), os.path.join(tmp, name))
    out = os.path.join(tmp, "result.json")
    args = [exe, "-ckq" if mode == "cli" else "-qk", SCRIPT, "--", mode, out]
    with open(os.path.join(tmp, "log.txt"), "w") as log:
        subprocess.run(
            args, stdout=log, stderr=subprocess.STDOUT, timeout=3600, cwd=tmp, env=ENV
        )
    if not os.path.exists(out):
        sys.exit(f"{exe} {mode} failed, see {tmp}/log.txt")
    with open(out) as f:
        return json.load(f)


def image_diff(a, b):
    """Mean absolute difference per channel, 0..255, and share of pixels off by > 32."""
    import numpy
    from pymol.Qt import QtGui

    def pixels(p):
        img = QtGui.QImage(p).convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
        return numpy.frombuffer(img.constBits(), numpy.uint8).reshape(
            img.height(), img.width(), 4
        )

    pa, pb = pixels(a).astype(int), pixels(b).astype(int)
    if pa.shape != pb.shape:
        return float("nan"), 1.0
    d = abs(pa - pb)[..., :3]
    return d.mean(), (d.max(axis=2) > 32).mean()


def table(ref, new, unit):
    bad = []
    print(
        f"| Workload | pymol3 {ref['_version']['result']} | pymolish {new['_version']['result']} | ratio | result |"
    )
    print("| --- | --- | --- | --- | --- |")
    for name, r in ref.items():
        if name.startswith("_") or "/" in name or name not in new:
            continue
        n = new[name]
        same = r["result"] == n["result"]
        if not same:
            bad.append(name)
        result = (
            ""
            if r["result"] is None
            else ("same" if same else f"**DIFF** {r['result']} vs {n['result']}")
        )
        scale = 1e3 if unit == "ms" else 1
        print(
            f"| {name} | {r['time'] * scale:.3f} {unit} | {n['time'] * scale:.3f} {unit} | "
            f"{n['time'] / max(r['time'], 1e-9):.2f} | {result} |"
        )
    return bad


def structure_table(ref, new, unit):
    """One line per structure, one column per workload: pymol3 / pymolish (ratio)."""
    bad = []
    names = [n for n in ref if "/" in n and n in new]
    pdbs = list(dict.fromkeys(n.split("/")[0] for n in names))
    kinds = list(dict.fromkeys(n.split("/")[1] for n in names))
    scale, digits = (1e3, 0) if unit == "ms" else (1, 3)
    print(f"\n{unit}, pymol3 / pymolish (ratio)\n")
    print("| Structure | " + " | ".join(kinds) + " |")
    print("| --- " * (len(kinds) + 1) + "|")
    for pdb in pdbs:
        cells = []
        for kind in kinds:
            r, n = ref.get(f"{pdb}/{kind}"), new.get(f"{pdb}/{kind}")
            if not r or not n:
                cells.append("")
                continue
            if r["result"] != n["result"]:
                bad.append(f"{pdb}/{kind}")
            cells.append(
                f"{r['time'] * scale:.{digits}f} / {n['time'] * scale:.{digits}f}"
                f" ({n['time'] / max(r['time'], 1e-9):.2f})"
                + ("" if r["result"] == n["result"] else " **DIFF**")
            )
        load = ref.get(f"{pdb}/load")
        atoms = f" ({load['result']} atoms)" if load else ""
        print(f"| {pdb}{atoms} | " + " | ".join(cells) + " |")
    return bad


def fetch_structures():
    import urllib.request

    os.makedirs(CACHE, exist_ok=True)
    for pdb in STRUCTURES:
        if not os.path.exists(cached(pdb)):
            print(f"downloading {pdb}", file=sys.stderr)
            urllib.request.urlretrieve(
                f"https://files.rcsb.org/download/{pdb}.cif.gz", cached(pdb)
            )


def startup(exe):
    times = []
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        subprocess.run(
            [exe, "-ckq", "-d", "quit"], check=True, stdout=subprocess.DEVNULL, env=ENV
        )
        times.append(time.perf_counter() - t0)
    return min(times)


def main(gui):
    ref = os.environ.get(
        "PYMOL_REF", os.path.expanduser("~/code/pymol-open-source/.venv/bin/pymol")
    )
    new = os.path.join(os.path.dirname(sys.executable), "pymolish")
    tmp = tempfile.mkdtemp(prefix="pymol-compare-")
    print(f"Inputs and outputs: {tmp}", file=sys.stderr)
    fetch_structures()
    make_inputs(tmp)
    bad = []
    results = {}
    for label, exe in (("pymol3", ref), ("pymolish", new)):
        print(f"{label}: CLI", file=sys.stderr)
        results[label] = run_worker(exe, "cli", os.path.join(tmp, label))
        results[label]["startup -ckq -d quit"] = {"time": startup(exe), "result": None}
    print(f"\n{os.cpu_count()} CPUs, best of {REPEAT} (1 for slow rows), seconds\n")
    bad += table(results["pymol3"], results["pymolish"], "s")
    bad += structure_table(results["pymol3"], results["pymolish"], "s")

    print(
        "\n| Ray-traced 1oky, 480x360 | mean abs diff (0..255) | pixels off by > 32 |"
    )
    print("| --- | --- | --- |")
    for rep in REPS:
        mean, off = image_diff(
            *(os.path.join(tmp, v, f"{rep}.png") for v in ("pymol3", "pymolish"))
        )
        print(f"| {rep} | {mean:.1f} | {off:.1%} |")

    if gui:
        gres = {}
        for label, exe in (("pymol3", ref), ("pymolish", new)):
            print(f"{label}: GUI", file=sys.stderr)
            gres[label] = run_worker(exe, "gui", os.path.join(tmp, label + "-gui"))
        print(
            f"\nGUI, viewport {gres['pymol3']['_viewport']['result']} vs "
            f"{gres['pymolish']['_viewport']['result']}, frame = draw + glFinish, "
            f"{FRAMES} frames per median, ms\n"
        )
        bad += table(gres["pymol3"], gres["pymolish"], "ms")
        bad += structure_table(gres["pymol3"], gres["pymolish"], "ms")

    print(f"\nImages and logs: {tmp}")
    if bad:
        print(f"Different results: {', '.join(bad)}")
        sys.exit(1)


if len(sys.argv) > 2 and sys.argv[1] in ("cli", "gui"):
    if sys.argv[1] == "cli":
        write(sys.argv[2], run_cli(sys.argv[2]))
    else:
        run_gui(sys.argv[2])
else:
    main("gui" in sys.argv[1:])
