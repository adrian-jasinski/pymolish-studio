# Ray-traced pictures for the galleries of docs/index.html, made headless:
#   PYMOLISH_CAPTURE=<an empty folder> pymolish -ckq $PWD/docs/media/capture/gallery.py [-- id ...]
# Each look is set by the call its menu row makes (preset.from_menu,
# preset.look, preset.theme, stage, palette, glow). Writes out/gallery/<id>.webp
# (RECIPES, 1200 x 900) and out/presets/<id>.webp (PRESETS, 800 x 600).
import os
import sys
import time

import numpy
from PIL import Image
from pymol import cmd, preset, util

B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"
os.makedirs(B + "work", exist_ok=True)
cmd.cd(B + "work")
SIZE = (1200, 900)  # every picture is 4:3; the presets are smaller
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
BLACK, WHITE, DARK = "0x000000", "0xffffff", "0x111620"

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

# One picture per row of the Presets menu: hemoglobin in the pastel palette
# on the dark of the web page, so that only the preset changes. The binding
# rows use the kinase with its ligand.
H = ("4hhb", "pretty_solv", "pastel", DARK, None, 0, None, None)
K = ("1oky",) + H[1:]
PRESETS = {
    "cartoon-pretty":         H,
    "cartoon-publication":    H[:1] + ("pub_solv",) + H[2:],
    "cartoon-technical":      H[:1] + ("technical",) + H[2:],
    "cartoon-b-factor-putty": H[:1] + ("b_factor_putty",) + H[2:],
    "cartoon-wire":           H[:1] + ("wire",) + H[2:],
    "cartoon-spring":         H[:1] + ("spring",) + H[2:],
    "cartoon-cylinders":      H[:1] + ("cylinders",) + H[2:],
    "cartoon-contour":        H[:1] + ("illustration",) + H[2:],
    "atoms-space-filling":    H[:1] + ("space_filling",) + H[2:],
    "atoms-illustrated":      H[:1] + ("illustrated_atoms",) + H[2:],
    "atoms-ball-and-stick":   H[:1] + ("ball_and_stick",) + H[2:],
    "atoms-licorice":         H[:1] + ("licorice",) + H[2:],
    "surface-glossy":         H[:1] + (("surface", "glossy"),) + H[2:],
    "surface-candy-glass":    H[:1] + (("surface", "candy glass"),) + H[2:],
    "surface-frosted":        H[:1] + (("surface", "frosted"),) + H[2:],
    "surface-clay":           H[:1] + (("surface", "clay"),) + H[2:],
    "surface-glass":          H[:1] + ("glass",) + H[2:],
    "surface-balls-in-glass": H[:1] + ("balls_in_glass",) + H[2:],
    "surface-bond-shell":     H[:1] + ("bond_shell",) + H[2:],
    "binding-ligands":        K[:1] + ("ligands",) + K[2:],
    "binding-site-solid":     K[:1] + ("ligand_sites",) + K[2:],
    "binding-site-transparent": K[:1] + ("ligand_sites_trans",) + K[2:],
    "binding-site-mesh":      K[:1] + ("ligand_sites_mesh",) + K[2:],
    "binding-site-dots":      K[:1] + ("ligand_sites_dots",) + K[2:],
    "binding-interface":      H[:1] + ("interface",) + H[2:],
    "binding-interaction":    H[:1] + ("interaction",) + H[2:],
    "light-figure":           H[:4] + ("figure",) + H[5:],
    "light-soft":             H[:4] + ("soft",) + H[5:],
    "light-flat":             H[:4] + ("flat",) + H[5:],
    "light-comic":            H[:4] + ("comic",) + H[5:],
    "light-sketch":           H[:3] + (WHITE, "sketch") + H[5:],
    "light-x-ray":            H[:4] + ("x-ray",) + H[5:],
    "light-studio":           H[:4] + ("studio",) + H[5:],
    "light-glossy":           H[:4] + ("glossy",) + H[5:],
    "light-glow":             H[:5] + (1,) + H[6:],
    "theme-clay":             H[:2] + (None, None, None, 0, "clay", None),
    "theme-blue":             H[:2] + (None, None, None, 0, "blue", None),
    "theme-sage":             H[:2] + (None, None, None, 0, "sage", None),
    "theme-mint":             H[:2] + (None, None, None, 0, "mint", None),
    "theme-night":            H[:2] + (None, None, None, 0, "night", None),
    "floor-floor":            H[:3] + (WHITE, "top light", 0, None, "floor"),
    "floor-mirror":           H[:3] + (WHITE, None, 0, None, "mirror"),
}
# fmt: on
POCKET_VIEW = {"kinase-frosted-blue", "kinase-pocket-night"}


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


def render(name, out, size, pdb, row, palette, bg, light, glow, theme, floor):
    t = time.time()
    os.makedirs(out, exist_ok=True)
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
    if theme:  # again: presets color the ligands by chain
        preset.theme(theme, pdb, _self=cmd)
    if light:
        preset.look(light, _self=cmd)
    cmd.set("opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("glow", glow)
    if name in POCKET_VIEW:
        cmd.set_view(POCKET)
    elif pdb == "1oky" and name.startswith("binding"):  # the site, not the protein
        cmd.set_view(POCKET)
        cmd.zoom("resn STU", 8)
    else:  # the nucleosome by its DNA: the histone tails reach far out
        fit(
            pdb + (" and polymer.nucleic" if pdb == "1kx5" else ""),
            1.5 if floor else 1.06,
        )  # room for the floor the tilt shows
    if floor:
        cmd.stage(floor)
    png = out + name + ".png"
    cmd.png(png, width=size[0], height=size[1], ray=1)
    Image.open(png).convert("RGB").save(out + name + ".webp", quality=82, method=6)
    os.remove(png)
    kb = os.path.getsize(out + name + ".webp") // 1024
    print(f"{name:38} {time.time() - t:5.1f} s {kb:4d} KB", flush=True)


JOBS = {name: (B + "out/gallery/", SIZE, *r) for name, r in RECIPES.items()}
JOBS.update({name: (B + "out/presets/", (800, 600), *r) for name, r in PRESETS.items()})
for name in [a for a in sys.argv if a in JOBS] or JOBS:
    render(name, *JOBS[name])
