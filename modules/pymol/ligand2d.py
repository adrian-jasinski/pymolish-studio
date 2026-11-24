"""
A ligand drawn flat with the residues around it and the contacts between
them: "ligand_2d". The ligand's 2D coordinates and the picture come from
rdkit (optional dependency, extra "chem"); the contacts are found here.
The window shows the picture in pmg_qt/ligand_panel.py.

The layout follows PandaMap (MIT, Pritam Kumar Panda): each residue stands
on a ring around the ligand, at the angle of the ligand atoms it touches,
and neighbors are pushed apart until none overlap.
"""

import math

import pymol

from . import smiles

cmd = __import__("sys").modules["pymol.cmd"]

# Distances in Angstrom, as PLIP publishes them (plip/basic/config.py); the
# hydrogen bond is donor to acceptor, since most structures have no hydrogens.
CUTOFF = 4.0  # any heavy atom: the residue is "near"
HBOND = 3.5
SALT = 5.5
STACK = 5.5  # ring center to ring center
CATION = 6.0  # charged atom to ring center
METAL = 3.0  # ligand atom to metal
PROBE = 1.4  # water, for the atoms open to the solvent
EXPOSED = 0.3  # share of an atom's open surface the protein leaves open

KINDS = {  # residue name -> kind; anything else is "other"
    **dict.fromkeys("ALA VAL LEU ILE MET PHE TRP TYR PRO CYS".split(), "hydrophobic"),
    **dict.fromkeys("SER THR ASN GLN HIS".split(), "polar"),
    **dict.fromkeys("ASP GLU".split(), "negative"),
    **dict.fromkeys("LYS ARG".split(), "positive"),
    "GLY": "glycine",
}
COLORS = {  # kind -> fill
    "hydrophobic": (0.65, 0.85, 0.29),
    "polar": (0.56, 0.85, 0.94),
    "negative": (0.94, 0.54, 0.36),
    "positive": (0.60, 0.60, 0.96),
    "glycine": (0.95, 0.95, 0.85),
    "other": (0.82, 0.82, 0.82),
}
LINES = {  # contact -> (color, dashed)
    "hydrogen bond": ((0.69, 0.19, 0.88), True),
    "salt bridge": ((0.90, 0.20, 0.20), False),
    "ring stacking": ((0.10, 0.60, 0.20), False),
    "cation-ring": ((0.85, 0.45, 0.10), False),
    "metal": ((0.50, 0.50, 0.50), False),
}
POSITIVE = {"LYS": ("NZ",), "ARG": ("NE", "NH1", "NH2"), "HIS": ("ND1", "NE2")}
NEGATIVE = {"ASP": ("OD1", "OD2"), "GLU": ("OE1", "OE2")}
_SIX = ("CG", "CD1", "CD2", "CE1", "CE2", "CZ")
RINGS = {
    "PHE": (_SIX,),
    "TYR": (_SIX,),
    "TRP": (
        ("CD2", "CE2", "CE3", "CZ2", "CZ3", "CH2"),
        ("CG", "CD1", "NE1", "CE2", "CD2"),
    ),
    "HIS": (("CG", "ND1", "CD2", "CE1", "NE2"),),
}
# charged groups of a ligand as SMARTS: amines that are no amide and not on
# a ring atom of an aromatic ring, amidines and guanidines; acids
LIGAND_POSITIVE = (
    "[NX3;!$(N-C=[O,N,S]);!$(N-a);!$(N-S=O)]",
    "[NX4+]",
    "[NX3]-C(=[NX2,NX3+])",
)
LIGAND_NEGATIVE = ("[OX1,OX2H1,OX1-]-,=[C,P,S]=O", "[O-]")
SIZE = 52  # a residue's circle, across, in pixels
FONT = 14  # the names in the circles
LEGEND = (16, 28, 20, 32)  # the legend: font, height of a row, circle, line
SCALE = 20  # pixels per unit of rdkit's 2D coordinates: a bond is 1.5 long
GROUP = "ligand_2d"  # the dashes of "Show in 3D"


def ligands(selection="enabled", *, _self=cmd):
    """The small molecules in `selection` with at least six heavy atoms, as
    (label, selection). The one with the most protein atoms around it comes
    first: the ligand in its pocket, before lipids, sugars and buffer on the
    surface."""
    found = {}
    _self.iterate(
        "(%s) and organic and not polymer and not hydro" % selection,
        "found[model, segi, chain, resn, resi] = found.get((model, segi, chain, resn, resi), 0) + 1",
        space={"found": found},
    )
    rows = []
    for key, count in found.items():
        if count >= 6:
            sele = "/%s/%s/%s/%s`%s/" % key
            near = _self.count_atoms(
                "polymer and not hydro within %f of (%s)" % (CUTOFF, sele)
            )
            rows.append((-near, -count, "%s %s%s" % (key[3], key[2], key[4]), sele))
    return [(label, sele) for _, _, label, sele in sorted(rows)]


def _center(points):
    return [sum(p[i] for p in points) / len(points) for i in range(len(points[0]))]


def _exposed(xyz, radii, protein, points=64):
    """The ligand atoms the protein leaves open to the solvent: of the
    points on an atom's surface that the ligand itself leaves open, more
    than EXPOSED are not inside a protein atom either (Shrake and Rupley,
    with a water of PROBE)."""
    import numpy

    k = numpy.arange(points) + 0.5
    phi, theta = numpy.arccos(1 - 2 * k / points), numpy.pi * (1 + 5**0.5) * k
    sphere = numpy.stack(
        [
            numpy.cos(theta) * numpy.sin(phi),
            numpy.sin(theta) * numpy.sin(phi),
            numpy.cos(phi),
        ],
        1,
    )
    own = numpy.asarray(xyz, float)
    reach = numpy.asarray(radii, float) + PROBE
    other = numpy.asarray([a.coord for a in protein], float).reshape(-1, 3)
    other_reach = numpy.asarray([a.vdw for a in protein], float) + PROBE
    found = set()
    for i in range(len(own)):
        surface = own[i] + sphere * reach[i]
        inside = numpy.linalg.norm(surface[:, None] - own[None], axis=2) < reach[None]
        inside[:, i] = False
        alone = ~inside.any(1)
        if len(other):
            covered = (
                numpy.linalg.norm(surface[:, None] - other[None], axis=2)
                < other_reach[None]
            )
            free = alone & ~covered.any(1)
        else:
            free = alone
        if alone.sum() >= 4 and free.sum() > EXPOSED * alone.sum():
            found.add(i)
    return found


def analyze(ligand, cutoff=CUTOFF, *, _self=cmd):
    """The ligand as an rdkit molecule with 2D coordinates, and the residues
    in contact with it: a list of dicts with "label", "kind", "sele",
    "atoms" (indices of the ligand atoms it is near), "contacts", pairs
    of a contact name and the ligand atoms it goes to, "pairs", the same
    as (name, ligand selection, residue selection, distance), and
    "nearest", the shortest distance between the two. Ligand atoms open
    to the solvent carry the rdkit property "exposed"."""
    Chem, AllChem = smiles.rdkit()
    heavy = "(%s) and not hydro" % ligand
    atoms = _self.get_model(heavy).atom
    if not atoms:
        raise pymol.CmdException("no atoms in '%s'" % ligand)
    mol = Chem.MolFromMolBlock(_self.get_str("mol", heavy), removeHs=True)
    if mol is None:  # odd valences in a deposited ligand
        mol = Chem.MolFromMolBlock(_self.get_str("mol", heavy), sanitize=False)
        if mol is not None:
            mol.UpdatePropertyCache(strict=False)
            Chem.FastFindRings(mol)
    if mol is None or mol.GetNumAtoms() != len(atoms):
        raise pymol.CmdException("rdkit cannot read the ligand '%s'" % ligand)
    AllChem.Compute2DCoords(mol)
    xyz = [a.coord for a in atoms]

    def matches(patterns):
        hits = set()
        for pattern in patterns:
            for match in mol.GetSubstructMatches(Chem.MolFromSmarts(pattern)):
                hits.add(match[0])
        return hits

    plus, minus = matches(LIGAND_POSITIVE), matches(LIGAND_NEGATIVE)
    plus -= minus
    rings = [
        ring
        for ring in mol.GetRingInfo().AtomRings()
        if all(mol.GetAtomWithIdx(i).GetIsAromatic() for i in ring)
    ]

    # everything of the protein that can matter, by residue
    reach = max(cutoff, CATION) + 3.0
    around = (
        "byres ((%s) around %f) and not hydro and not (%s)"
        " and (polymer or inorganic or metals)"
        % (
            ligand,
            reach,
            ligand,
        )
    )
    residues = {}
    protein = _self.get_model(around).atom
    for atom in protein:
        # by object too: the protein may be another object than the ligand
        key = (atom.model, atom.segi, atom.chain, atom.resn, atom.resi)
        residues.setdefault(key, []).append(atom)
    metals = {
        (a.model, a.index) for a in _self.get_model("(%s) and metals" % around).atom
    }
    model = atoms[0].model if hasattr(atoms[0], "model") else ""
    objects = _self.get_object_list(ligand)
    obj = objects[0] if objects else model

    def own(group):  # ligand atoms as a selection
        return "%s and index %s" % (obj, "+".join(str(atoms[i].index) for i in group))

    for i in _exposed(xyz, [a.vdw for a in atoms], protein):
        mol.GetAtomWithIdx(i).SetBoolProp("exposed", True)
    result = []
    for key, members in residues.items():
        sele = "/%s/%s/%s/%s`%s/" % key
        resn, resi = key[3:]
        near, contacts, pairs = set(), [], []
        nearest = min(math.dist(a, m.coord) for a in xyz for m in members)
        for i, a in enumerate(xyz):
            if any(math.dist(a, m.coord) <= cutoff for m in members):
                near.add(i)
        named = {m.name: m.coord for m in members}

        def add(name, group, partner, point):
            """A contact of `group` (ligand atoms) to `partner` (atom names of
            the residue); the distance is between their centers."""
            contacts.append((name, tuple(group)))
            mid = _center([xyz[i] for i in group])
            pairs.append(
                (
                    name,
                    own(group),
                    "(%s) and name %s" % (sele, "+".join(partner)),
                    math.dist(mid, point),
                )
            )

        def charged(names, i):  # the residue's charged atom nearest to i
            name = min(
                (n for n in names if n in named),
                key=lambda n: math.dist(named[n], xyz[i]),
            )
            return (name,), named[name]

        def close(names, targets, limit):
            return sorted(
                i
                for i in targets
                if any(
                    n in named and math.dist(xyz[i], named[n]) <= limit for n in names
                )
            )

        if resn in NEGATIVE and (hit := close(NEGATIVE[resn], plus, SALT)):
            add("salt bridge", hit[:1], *charged(NEGATIVE[resn], hit[0]))
        if resn in POSITIVE and (hit := close(POSITIVE[resn], minus, SALT)):
            add("salt bridge", hit[:1], *charged(POSITIVE[resn], hit[0]))
        for names in RINGS.get(resn, ()):
            if all(n in named for n in names):
                center = _center([named[n] for n in names])
                for ring in rings:
                    if math.dist(center, _center([xyz[i] for i in ring])) <= STACK:
                        add("ring stacking", ring, names, center)
                for i in plus:
                    if math.dist(center, xyz[i]) <= CATION:
                        add("cation-ring", (i,), names, center)
        for name in {"LYS": ("NZ",), "ARG": ("CZ",)}.get(resn, ()):
            for ring in rings:
                if (
                    name in named
                    and math.dist(named[name], _center([xyz[i] for i in ring]))
                    <= CATION
                ):
                    add("cation-ring", ring, (name,), named[name])
        for m in members:
            if (m.model, m.index) in metals:
                i = min(range(len(xyz)), key=lambda i: math.dist(xyz[i], m.coord))
                if math.dist(xyz[i], m.coord) <= METAL:
                    add("metal", (i,), (m.name,), m.coord)
        if near or contacts:
            result.append(
                {
                    "label": (resn, resi),
                    "kind": KINDS.get(resn, "other"),
                    "sele": sele,
                    "atoms": near or {i for _, group in contacts for i in group},
                    "contacts": contacts,
                    "pairs": pairs,
                    "nearest": nearest,
                    "members": {(m.model, m.index): (m.name, m.coord) for m in members},
                }
            )
    # hydrogen bonds from the core: distance and angle
    index = {(a.model, a.index): i for i, a in enumerate(atoms)}
    owner = {i: r for r in result for i in r["members"]}
    pairs = _self.find_pairs(
        "(%s) and (donor or acceptor)" % heavy,
        "(%s) and (donor or acceptor) and not metals" % around,
        mode=1,
        cutoff=HBOND,
        angle=55,
    )
    seen = set()
    for a, b in pairs:
        residue = owner.get(b)
        if residue is not None and a in index and (id(residue), index[a]) not in seen:
            seen.add((id(residue), index[a]))
            name, coord = residue["members"][b]
            residue["contacts"].append(("hydrogen bond", (index[a],)))
            residue["pairs"].append(
                (
                    "hydrogen bond",
                    own((index[a],)),
                    "(%s) and name %s" % (residue["sele"], name),
                    math.dist(xyz[index[a]], coord),
                )
            )
    for residue in result:
        del residue["members"]
        # one line per kind of contact and ligand atom group
        residue["contacts"] = sorted(set(residue["contacts"]))
        residue["pairs"] = sorted(set(residue["pairs"]), key=lambda p: (p[0], p[3]))
    return mol, result


def layout(points, anchors, size=SIZE, gap=6):
    """Where the residues go: `points` are the ligand atoms in pixels,
    `anchors` the ligand atoms each residue is near. Each residue stands on
    a ring around the ligand at the angle of its atoms; neighbors are pushed
    apart until the circles are `gap` pixels apart, and the ring grows when
    they do not fit. Returns the centers and the ring's radius."""
    if not anchors:
        return [], 0.0
    cx, cy = _center(points)
    reach = max(math.dist((cx, cy), p) for p in points)
    step = size + gap  # along the ring
    radius = max(reach + size * 0.9, len(anchors) * step / (2 * math.pi))
    need = step / radius
    angles = []
    for group in anchors:
        ax, ay = _center([points[i] for i in group])
        angles.append(math.atan2(ay - cy, ax - cx))
    order = sorted(range(len(angles)), key=angles.__getitem__)
    spread = [angles[i] for i in order]
    count = len(spread)
    # Cut the ring at its widest gap, so the angles lie on a line; push each
    # one clockwise until it is `need` after the one before; then turn the
    # whole row back by the mean push, which keeps the gaps.
    gaps = [(spread[(k + 1) % count] - spread[k]) % (2 * math.pi) for k in range(count)]
    start = (gaps.index(max(gaps)) + 1) % count if count > 1 else 0
    order = order[start:] + order[:start]
    line = [
        (spread[(start + k) % count] - spread[start]) % (2 * math.pi)
        for k in range(count)
    ]
    pushed = line[:]
    for k in range(1, count):
        pushed[k] = max(pushed[k], pushed[k - 1] + need)
    if count > 1 and pushed[-1] - pushed[0] > 2 * math.pi - need:  # a full ring
        pushed = [k * 2 * math.pi / count for k in range(count)]
    turn = sum(p - q for p, q in zip(pushed, line)) / count
    spread = [spread[start] + p - turn for p in pushed]
    places = [None] * len(anchors)
    for rank, i in enumerate(order):
        places[i] = (
            cx + radius * math.cos(spread[rank]),
            cy + radius * math.sin(spread[rank]),
        )
    return places, radius


def _turn(angle):
    """An angle brought to -pi..pi."""
    return (angle + math.pi) % (2 * math.pi) - math.pi


def contour(points, places, kinds, radius, steps=120):
    """The pocket's outline: for each of `steps` directions around the
    ligand's center a point halfway between the ligand and the residues'
    circles, and the kind of the residue nearest that direction, or None
    where no residue is near (the pocket is open there)."""
    if not places:
        return []
    cx, cy = _center(points)
    angles = [math.atan2(y - cy, x - cx) for x, y in points]
    reach = []
    for k in range(steps):
        toward = 2 * math.pi * k / steps
        reach.append(
            max(
                (
                    math.dist((cx, cy), p)
                    for p, a in zip(points, angles)
                    if abs(_turn(a - toward)) < 0.5
                ),
                default=0.0,
            )
        )
    for _ in range(4):  # smooth, around the circle
        reach = [
            (reach[k - 1] + reach[k] + reach[(k + 1) % steps]) / 3 for k in range(steps)
        ]
    sides = [math.atan2(y - cy, x - cx) for x, y in places]
    line = []
    for k in range(steps):
        toward = 2 * math.pi * k / steps
        r = (reach[k] + 16 + radius - SIZE / 2) / 2
        off, near = min((abs(_turn(a - toward)), kind) for a, kind in zip(sides, kinds))
        line.append(
            (
                (cx + r * math.cos(toward), cy + r * math.sin(toward)),
                near if off * radius < SIZE * 1.2 else None,
            )
        )
    return line


def _mix(color, other, share):
    return tuple(a + (b - a) * share for a, b in zip(color, other))


def _tones(color, dark):
    """A residue's circle in the color of its kind: the fill at the top and
    at the bottom, the outline, the text. On a dark window deep fills, a
    bright outline and white text; on a light one the other way round."""
    black, white = (0, 0, 0), (1, 1, 1)
    if dark:
        return _mix(color, black, 0.45), _mix(color, black, 0.7), color, white
    return _mix(color, white, 0.6), color, _mix(color, black, 0.45), (0.1, 0.1, 0.1)


def _legend(width):
    """Where the entries of the legend go: (name, x, row) for the kinds,
    then for the contacts from a row of their own, in rows that fit
    `width`; and the number of rows."""
    font, _, dot, dash = LEGEND
    entries, row = [], -1
    for names, mark in ((COLORS, dot), (LINES, dash)):
        x, row = 14, row + 1
        for name in names:
            # ponytail: 0.55 of the font size per letter, measured on
            # rdkit's font; a text measured by the drawer if a name is cut
            wide = mark + 8 + 0.55 * font * len(name) + 16
            if x + wide > width and x > 14:
                x, row = 14, row + 1
            entries.append((name, x, row))
            x += wide
    return entries, row + 1


def draw(
    mol,
    residues,
    svg=True,
    selected=(),
    background=(1, 1, 1),
    ink=(0, 0, 0),
    current=None,
):
    """The picture as SVG text or PNG bytes, its size, and for each residue
    its center in pixels (for clicks). `selected` are indices of residues to
    ring in blue, `current` the one the keyboard is on. `ink` is the color
    of the text beside the shapes: a light one means a dark window, and the
    residues are drawn for that. Under the ligand: a grey halo on its atoms
    open to the solvent and the pocket's outline in the residues' colors."""
    import re

    from rdkit.Chem.Draw import rdMolDraw2D
    from rdkit.Geometry import Point2D

    dark = sum(ink) > 1.5
    conformer = mol.GetConformer()
    flat = [
        (conformer.GetAtomPosition(i).x, conformer.GetAtomPosition(i).y)
        for i in range(mol.GetNumAtoms())
    ]
    center = _center(flat)
    reach = max(math.dist(center, p) for p in flat) * SCALE
    ring = max(reach + SIZE * 0.9, len(residues) * (SIZE + 6) / (2 * math.pi))
    # the circles reach half a circle past the ring; at least as wide as two
    # contacts of the legend side by side
    side = max(344, int(2 * ring + SIZE + 20))
    entries, rows = _legend(side)
    font, high, dot, dash = LEGEND
    legend = rows * high + 12
    size = (side, side + legend)

    def start(dx, dy, under=None):
        drawer = (rdMolDraw2D.MolDraw2DSVG if svg else rdMolDraw2D.MolDraw2DCairo)(
            *size
        )
        options = drawer.drawOptions()
        options.fixedBondLength = SCALE  # per unit, despite its name
        if dark:
            rdMolDraw2D.SetDarkMode(options)
        # the background by hand: rdkit's own moves with the offset below
        # and would leave the strip of the legend bare
        options.clearBackground = False
        drawer.SetFillPolys(True)
        drawer.SetColour(background)
        drawer.DrawRect(Point2D(0, 0), Point2D(*size), True)
        drawer.SetOffset(round(dx), round(dy))
        if under:
            under(drawer)
        drawer.DrawMolecule(mol)
        atoms = range(mol.GetNumAtoms())
        return drawer, [(p.x, p.y) for p in (drawer.GetDrawCoords(i) for i in atoms)]

    # rdkit centers the box around the ligand and its labels; the ring of
    # residues goes around the mean of the atoms. Drawn once to see where
    # that lands, then again with it in the middle of the square above the
    # legend: the ring was cut at one side otherwise (2RH1, carazolol).
    first = start(0, 0)[1]
    cx, cy = _center(first)
    dx, dy = round(side / 2 - cx), round(side / 2 - cy)
    moved = [(x + dx, y + dy) for x, y in first]
    places, radius = layout(moved, [sorted(r["atoms"]) for r in residues])
    exposed = [
        i for i in range(mol.GetNumAtoms()) if mol.GetAtomWithIdx(i).HasProp("exposed")
    ]
    halo = (0.55, 0.55, 0.55) if dark else (0.70, 0.70, 0.70)

    def under(drawer):
        drawer.SetFillPolys(True)
        drawer.SetLineWidth(1)
        for i in exposed:  # three rings, fading out: a soft grey halo
            x, y = moved[i]
            for r, share in ((15, 0.3), (12, 0.6), (9, 0.9)):
                drawer.SetColour(_mix(background, halo, share))
                drawer.DrawEllipse(Point2D(x - r, y - r), Point2D(x + r, y + r), True)
        drawer.SetLineWidth(5)
        outline = contour(moved, places, [r["kind"] for r in residues], radius)
        for (a, kind), (b, after) in zip(outline, outline[1:] + outline[:1]):
            if kind and after:
                color = COLORS[kind]
                drawer.SetColour(color if dark else _mix(color, (0, 0, 0), 0.15))
                drawer.DrawLine(Point2D(*a), Point2D(*b), True)

    drawer, points = start(dx, dy, under)

    def line(a, b, color, dashed, width=2):
        # the contact colors are picked for white: lighter on a dark window
        drawer.SetColour(_mix(color, (1, 1, 1), 0.35) if dark else color)
        drawer.SetLineWidth(width)
        if not dashed:
            drawer.DrawLine(Point2D(*a), Point2D(*b), True)
            return
        length = math.dist(a, b)
        pieces = max(1, int(length // 9))
        for k in range(pieces):  # five pixels on, four off
            t0, t1 = k * 9 / length, min(1, (k * 9 + 5) / length)
            drawer.DrawLine(
                Point2D(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                Point2D(a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1),
                True,
            )

    def circle(x, y, radius, kind, ringed=False):
        """A filled circle and its outline; returns the color for text."""
        top, bottom, edge, text = _tones(COLORS[kind], dark)
        corner = Point2D(x - radius, y - radius), Point2D(x + radius, y + radius)
        drawer.SetFillPolys(True)
        drawer.SetLineWidth(1)  # the fill's own edge stays under the outline
        drawer.SetColour(_mix(top, bottom, 0.5))  # a PNG keeps this one
        drawer.DrawEllipse(*corner, True)
        drawer.SetFillPolys(False)
        drawer.SetLineWidth(4 if ringed else 2)
        blue = (0.35, 0.63, 0.94) if dark else (0.12, 0.31, 0.72)  # the links
        drawer.SetColour(blue if ringed else edge)
        drawer.DrawEllipse(*corner, True)
        return text

    drawer.SetFillPolys(False)
    for residue, place in zip(residues, places):  # the lines under the shapes
        for name, group in residue["contacts"]:
            color, dashed = LINES[name]
            line(place, _center([points[i] for i in group]), color, dashed)
    drawer.SetFontSize(FONT)
    for number, (residue, (x, y)) in enumerate(zip(residues, places)):
        if number == current:  # the keyboard's: a ring around the circle
            drawer.SetFillPolys(False)
            drawer.SetLineWidth(2)
            drawer.SetColour(ink)
            r = SIZE / 2 + 6
            drawer.DrawEllipse(Point2D(x - r, y - r), Point2D(x + r, y + r), True)
        drawer.SetColour(circle(x, y, SIZE / 2, residue["kind"], number in selected))
        drawer.DrawString(
            residue["label"][0], Point2D(x, y - 8), 0, True
        )  # 0: centered
        drawer.DrawString(residue["label"][1], Point2D(x, y + 9), 0, True)
    # legend: the kinds, then the contacts
    drawer.SetFontSize(font)
    for name, x, row in entries:
        y = side + 6 + (row + 0.5) * high
        if name in COLORS:
            circle(x + dot / 2, y, dot / 2, name)
            mark = dot
        else:
            line((x, y), (x + dash, y), *LINES[name], width=3)
            mark = dash
        drawer.SetColour(ink)
        drawer.DrawString(name, Point2D(x + mark + 8, y), 1, True)  # 1: from the left
    drawer.FinishDrawing()
    text = drawer.GetDrawingText()
    if svg:
        # rdkit writes a space in a text as a path without data, and Qt
        # prints a warning for each
        text = re.sub(r"<path d=''[^>]*/>\n?", "", text)
        # rdkit has no gradients: the filled circles come in the order they
        # were drawn, and each gets the gradient of its kind
        # (the halos first: they keep their grey)
        kinds = iter(
            [None] * 3 * len(exposed) + [r["kind"] for r in residues] + list(COLORS)
        )

        def gradient(found):
            kind = next(kinds)
            return (
                found.group(0)
                if kind is None
                else "%surl(#%s)" % (found.group(1), kind)
            )

        text = re.sub(r"(<ellipse[^>]*?fill:)#\w{6}", gradient, text)
        stops = "<stop offset='%d' stop-color='#%02X%02X%02X'/>"
        gradients = "".join(
            "<linearGradient id='%s' x1='0' y1='0' x2='0' y2='1'>%s%s</linearGradient>"
            % (
                kind,
                *(
                    stops % (at, *(round(c * 255) for c in tone))
                    for at, tone in enumerate(_tones(color, dark)[:2])
                ),
            )
            for kind, color in COLORS.items()
        )
        text = text.replace("<!-- END OF HEADER -->", "<defs>%s</defs>" % gradients, 1)
    return text, size, places


def show_contacts(residues, *, _self=cmd):
    """The contacts of `residues` (from analyze) as dashes in 3D, one
    distance object per kind of contact, in the colors of the picture, in
    the group GROUP. Returns the names made, for hide_contacts."""
    made = {}  # object name -> contact name
    for residue in residues:
        for name, own, partner, _ in residue["pairs"]:
            target = "%s_%s" % (GROUP, name.replace(" ", "_").replace("-", "_"))
            if target not in made:
                _self.delete(target)
                made[target] = name
            _self.distance(target, own, partner, mode=4, label=0, quiet=1)
    for target, name in made.items():
        rgb = tuple(round(c * 255) for c in LINES[name][0])
        _self.set("dash_color", "0x%02x%02x%02x" % rgb, target)
    if made:
        _self.group(GROUP, " ".join(made))
    return list(made)


def hide_contacts(names, *, _self=cmd):
    """Delete the dashes show_contacts made, and their group; anything
    else in the group stays, out of it."""
    for name in names:
        _self.delete(name)
    if names and GROUP in _self.get_names("all"):
        _self.group(GROUP, action="excise")


def ligand_2d(ligand="", cutoff=CUTOFF, filename="", quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "ligand_2d" draws a ligand flat, with the residues around it and its
        contacts: hydrogen bonds, salt bridges, ring stacking, cation-ring.
        Residues are colored by kind. Without a file name it lists the
        contacts.

    USAGE

        ligand_2d [ ligand [, cutoff [, filename ]]]

    ARGUMENTS

        ligand = str: selection of one ligand {default: the first small
        molecule of the objects that are switched on}

        cutoff = float: a residue with a heavy atom this close is drawn
        {default: 4.0}

        filename = str: a .svg or .png file to write

    NOTES

        Needs rdkit, which the downloadable builds include; for a pip
        install: pip install 'pymolish[chem]'. Cutoffs: hydrogen bond 3.5 A
        donor to acceptor, salt bridge 5.5 A, ring centers 5.5 A, charge to
        ring center 6.0 A. Water bridges are not looked for.

    EXAMPLE

        fetch 2rh1
        ligand_2d resn CAU, filename=carazolol.svg
    """
    if not ligand:
        found = ligands(_self=_self)
        if not found:
            raise pymol.CmdException("no ligand in the visible objects")
        ligand = found[0][1]
    mol, residues = analyze(ligand, float(cutoff), _self=_self)
    if filename:
        png = filename.lower().endswith(".png")
        data, _, _ = draw(mol, residues, svg=not png)
        with open(_self.exp_path(filename), "wb" if png else "w") as handle:
            handle.write(data)
    if not int(quiet):
        for residue in residues:
            names = sorted({name for name, _ in residue["contacts"]}) or ["near"]
            print(
                " %s %s (%s): %s"
                % (*residue["label"], residue["kind"], ", ".join(names))
            )
    return residues
