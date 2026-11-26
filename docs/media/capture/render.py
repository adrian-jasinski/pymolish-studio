# Rendered (ray-traced) pictures for docs/appearance.md, made headless:
#   PYMOLISH_CAPTURE=<an empty folder> pymolish -ckq $PWD/docs/media/capture/render.py
# Every look is set by the call its menu row makes.
import os
from pymol import cmd, preset
from PIL import Image

B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
OUT = B + "out/"
os.makedirs(B + "work", exist_ok=True)
os.makedirs(OUT, exist_ok=True)
cmd.cd(B + "work")
SIZE = (640, 480)
# the ligand seen through the opening of its pocket (found by trying 60 views)
VIEW = (
    -0.4173,
    0.9038,
    0.0948,
    0.0234,
    -0.0936,
    0.9953,
    0.9084,
    0.4176,
    0.0179,
    0.0,
    0.0,
    -173.1179,
    81.868,
    19.0457,
    2.1404,
    136.4874,
    209.7483,
    -20.0,
)


def start():
    cmd.reinitialize()
    cmd.fetch("1oky")
    cmd.remove("solvent or inorganic or resn GOL")
    cmd.color("skyblue", "polymer and elem C")
    cmd.bg_color("white")
    cmd.set("opaque_background", 1)
    cmd.stage("off")  # a floor of the run before: see the note in ../README.md
    cmd.set_view(VIEW)


def snap(name):
    cmd.png(OUT + name + ".png", width=SIZE[0], height=SIZE[1], ray=1)
    return OUT + name + ".png"


def montage(files, name, columns=None):
    images = [Image.open(f).convert("RGB") for f in files]
    columns = columns or len(images)
    rows = -(-len(images) // columns)
    sheet = Image.new("RGB", (SIZE[0] * columns, SIZE[1] * rows), "white")
    for i, image in enumerate(images):
        sheet.paste(image, (SIZE[0] * (i % columns), SIZE[1] * (i // columns)))
    sheet.save(OUT + name, optimize=True)
    print(name, sheet.size, os.path.getsize(OUT + name))


files = []
for look in ("glossy", "candy glass", "frosted", "clay"):
    start()
    preset.from_menu("surface", "1oky", look, _self=cmd)
    files.append(snap("look-" + look.replace(" ", "-")))
montage(files, "appearance-surface-looks.png", 2)

files = []
for value in (0, 0.25, 0.5, 0.75):
    start()
    preset.from_menu("surface", "1oky", "glossy", _self=cmd)
    preset.transparency("surface", value, "1oky", _self=cmd)
    files.append(snap("transparency-%d" % (value * 100)))
montage(files, "appearance-transparency.png", 2)

files = []
for mode in ("floor", "mirror"):
    start()
    preset.from_menu("pub_solv", "1oky", _self=cmd)
    cmd.stage(mode)
    preset.look("top light", _self=cmd)
    files.append(snap("floor-" + mode))
montage(files, "appearance-floor.png")
