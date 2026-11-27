# Ray-traced pictures for the gallery of docs/index.html, made headless:
#   PYMOLISH_CAPTURE=<an empty folder> pymolish -ckq $PWD/docs/media/capture/gallery.py [-- id ...]
# Each look is set by the call its menu row makes (preset.from_menu,
# preset.look, preset.theme, stage, palette, glow). Writes out/gallery/<id>.webp.
import os
import sys
import time

import numpy
from PIL import Image
from pymol import cmd, preset, util

B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"
OUT = B + "out/gallery/"
os.makedirs(B + "work", exist_ok=True)
os.makedirs(OUT, exist_ok=True)
cmd.cd(B + "work")
SIZE = (1200, 900)
# 1oky: the ligand seen through the opening of its pocket (from render.py)
POCKET = (
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
BLACK, WHITE = "0x000000", "0xffffff"

# id: (pdb, preset row, palette, background, light, glow, theme, floor)
# preset row: a from_menu name, or ("surface", material)
# fmt: off
RECIPES = {
    "nucleosome-neon-glow":              ("1kx5", "pretty_solv", "neon", BLACK, None, 1, None, None),
    "nucleosome-neon":                   ("1kx5", "pretty_solv", "neon", BLACK, None, 0, None, None),
    "groel-spheres-neon-glow":           ("1aon", "space_filling", "neon", BLACK, "glossy", 1, None, None),
    "groel-illustrated-pastel":          ("1aon", "illustrated_atoms", "pastel", "0x1b2338", None, 0, None, None),
    "hemoglobin-spring-neon-glow":       ("4hhb", "spring", "neon", BLACK, "studio", 1, None, None),
    "hemoglobin-candy-glass-glow":       ("4hhb", ("surface", "candy glass"), "neon", BLACK, None, 1, None, None),
    "spike-glossy-dracula":              ("6vxx", ("surface", "glossy"), "dracula", "0x282a36", None, 0, None, None),
    "antibody-cylinders-catppuccin-glow": ("1hzh", "cylinders", "catppuccin", "0x1e1e2e", None, 1, None, None),
    "nucleosome-glass-pastel":           ("1kx5", "glass", "pastel", BLACK, None, 0, None, None),
    "antibody-frosted-nord":             ("1hzh", ("surface", "frosted"), "nord", "0x2e3440", None, 0, None, None),
    "groel-xray-neon-glow":              ("1aon", "pretty_solv", "neon", BLACK, "x-ray", 1, None, None),
    "kinase-pocket-night":               ("1oky", "ligand_sites_trans", None, None, None, 0, "night", None),
    "groel-clay":                        ("1aon", ("surface", "clay"), None, None, None, 0, "clay", None),
    "kinase-frosted-blue":               ("1oky", ("surface", "frosted"), None, None, None, 0, "blue", None),
    "kinase-floor-sage":                 ("1oky", "pub_solv", None, None, "top light", 0, "sage", "floor"),
    "hemoglobin-contour-pastel":         ("4hhb", "illustration", "pastel", WHITE, None, 0, None, None),
    "nucleosome-comic-pastel":           ("1kx5", "pretty_solv", "pastel", WHITE, "comic", 0, None, None),
    "spike-illustrated-pastel":          ("6vxx", "illustrated_atoms", "pastel", WHITE, None, 0, None, None),
    "antibody-clay-soft":                ("1hzh", ("surface", "clay"), "soft", WHITE, None, 0, None, None),
    "groel-mirror-chimerax":             ("1aon", ("surface", "glossy"), "chimerax", WHITE, None, 0, None, "mirror"),
    "hemoglobin-figure-colorblind-glow": ("4hhb", "pub_solv", "colorblind", WHITE, "figure", 1, None, None),
    "hemoglobin-sketch":                 ("4hhb", "pretty_solv", "deep", WHITE, "sketch", 0, None, None),
}
# fmt: on


def fit(selection, margin=1.06):
    """Orient, then put the camera as close as the 4:3 frame allows."""
    cmd.orient(selection)
    v = list(cmd.get_view())
    xyz = cmd.get_coords(selection) - numpy.array(v[12:15])
    cam = xyz @ numpy.array(v[:9]).reshape(3, 3)  # x right, y up, z to the eye
    center = (cam[:, :2].max(0) + cam[:, :2].min(0)) / 2
    cam[:, :2] -= center
    t = numpy.tan(numpy.radians(cmd.get_setting_float("field_of_view")) / 2)
    need = numpy.maximum(abs(cam[:, 0]) / (t * SIZE[0] / SIZE[1]), abs(cam[:, 1]) / t)
    d = float((cam[:, 2] + need * margin).max())
    v[9], v[10], v[11] = -center[0], -center[1], -d
    v[15], v[16] = d - cam[:, 2].max() - 5, d - cam[:, 2].min() + 5
    cmd.set_view(v)


def render(name, pdb, row, palette, bg, light, glow, theme, floor):
    t = time.time()
    cmd.reinitialize()
    cmd.stage("off")  # the floor of the recipe before: see ../README.md
    cmd.fetch(pdb, type="cif")
    cmd.remove("solvent or inorganic or resn GOL+EDO+SO4+PO4")
    if palette:
        cmd.palette(palette)
        util.cbc("all", _self=cmd)
        util.cnc("organic", _self=cmd)  # element colors on the ligands only
    # theme first: a surface preset copies the carbon colors, a theme after
    # it leaves the other atoms' patches in the old color
    if theme:
        preset.theme(theme, pdb, _self=cmd)
    else:
        cmd.set("bg_rgb", bg)
    if isinstance(row, tuple):
        preset.from_menu(row[0], pdb, row[1], _self=cmd)
    else:
        preset.from_menu(row, pdb, _self=cmd)
    if light:
        preset.look(light, _self=cmd)
    cmd.set("opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("glow", glow)
    if name in ("kinase-frosted-blue", "kinase-pocket-night"):
        cmd.set_view(POCKET)
    else:  # the nucleosome by its DNA: the histone tails reach far out
        fit(
            pdb + (" and polymer.nucleic" if pdb == "1kx5" else ""),
            1.5 if floor else 1.06,
        )  # room for the floor the tilt shows
    if floor:
        cmd.stage(floor)
    png = OUT + name + ".png"
    cmd.png(png, width=SIZE[0], height=SIZE[1], ray=1)
    Image.open(png).convert("RGB").save(OUT + name + ".webp", quality=82, method=6)
    os.remove(png)
    size = os.path.getsize(OUT + name + ".webp") // 1024
    print(f"{name:38} {time.time() - t:5.1f} s {size:4d} KB", flush=True)


for name in [a for a in sys.argv if a in RECIPES] or RECIPES:
    render(name, *RECIPES[name])
