"""
ligand_next: go to the next ligand, show it as ball_and_stick with the
polar contacts to its protein and zoom on the site. The ligands are those
of the 2D panel (ligand2d.ligands). What a visit turns on (the contacts,
sticks of the site, the balls) the next visit takes back; what was shown
before stays. The state of the walk is kept with the session
(session_extra), so a new or loaded session starts its own.
"""

import pymol

from . import ligand2d, session_extra

cmd = __import__("sys").modules["pymol.cmd"]

CONTACTS = "ligand_contacts"  # the dashes
SITE = 4.0  # A around the ligand: the residues shown as sticks and zoomed on
# atoms whose sticks, or balls, a visit turned on
OWNED = {"sticks": "_ligand_next_sticks", "ball_and_stick": "_ligand_next_balls"}


def _state():
    return session_extra.entries.setdefault(
        "ligand_next", {"current": None, "contacts": None}
    )


def current():
    """The ligand ligand_next went to last, as a selection; None before."""
    return session_extra.entries.get("ligand_next", {}).get("current")


def _clear(_self):
    """Take back what the last visit turned on."""
    state = _state()
    names = _self.get_names("all")
    for rep, name in OWNED.items():
        if name in names:
            _self.hide(rep, name)
            _self.delete(name)
    if state["contacts"] and state["contacts"] in names:
        _self.delete(state["contacts"])
    state["contacts"] = None


def ligand_next(selection="enabled", step=1, quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "ligand_next" goes to the next ligand: it is shown as
        ball_and_stick, the residues of its protein within 4 A as sticks,
        the polar contacts between the two as dashes (the object
        "ligand_contacts"), and the view zooms on the site. The next call
        takes back what this one turned on and goes on; after the last
        ligand comes the first.

        The contacts are found by geometry (distance, mode 2): they are
        candidates for hydrogen bonds, not measured ones. They are made
        with the protein of the ligand's own object, in its current state.

    USAGE

        ligand_next [ selection [, step ]]

    ARGUMENTS

        selection = str: where to look for ligands: small molecules of at
        least six heavy atoms; given explicitly, its protein atoms are the
        partner of the contacts, also in another object, and when it holds
        no such molecule, its residues are the ligands {default: enabled}

        step = int: 1 for the next, -1 for the previous one, 0 to take the
        contacts and what was turned on away {default: 1}

    EXAMPLE

        ligand_next
        ligand_next enabled, -1
        ligand_next chain A or resn STU
        ligand_next step=0

    SEE ALSO

        ligand_2d, distance, util.ligand_zoom (Ctrl-L: zoom only)
    """
    step, quiet = int(step), int(quiet)
    state = _state()
    if step == 0:
        _clear(_self)
        state["current"] = None
        return None
    default = selection.strip().strip("()") == "enabled"
    rows = ligand2d.ligands(selection, _self=_self)
    if not rows and not default:
        # asked for by name: a peptide or a cofactor the rule above leaves out
        found = set()
        _self.iterate(
            "(%s) and not solvent" % selection,
            "found.add((model, segi, chain, resn, resi))",
            space={"found": found},
        )
        rows = [
            ("%s %s%s" % (k[3], k[2], k[4]), "/%s/%s/%s/%s`%s/" % k)
            for k in sorted(found)
        ]
    if not rows:
        print(" ligand_next: no ligand in '%s'." % selection)
        return None
    ligands = [sele for _, sele in rows]
    if state["current"] in ligands:
        index = ligands.index(state["current"])
    else:
        index = -1 if step > 0 else 0
    index = (index + step) % len(rows)
    label, ligand = rows[index]

    _clear(_self)
    model = _self.get_object_list(ligand)[0]
    host = "polymer and %" + model
    if not default and _self.count_atoms("(%s) and polymer" % selection):
        host = "(%s) and polymer" % selection
    site = "byres ((%s) within %f of (%s))" % (host, SITE, ligand)
    for rep, target in (("ball_and_stick", ligand), ("sticks", site)):
        # only what this visit turns on is taken back by the next one
        if _self.select(OWNED[rep], "(%s) and not rep %s" % (target, rep), 0):
            _self.show(rep, OWNED[rep])
        else:
            _self.delete(OWNED[rep])

    name = CONTACTS
    if name in _self.get_names("all"):  # somebody else's: it is left alone
        name = _self.get_unused_name(CONTACTS + "_")
    # of the state that is shown: another state is another visit
    mean = _self.distance(
        name, ligand, host, mode=2, label=0, reset=1, quiet=1, state=_self.get_state()
    )
    contacts = mean > 0 and name in _self.get_names("objects")
    if contacts:
        _self.hide("labels", name)
    elif name in _self.get_names("objects"):
        _self.delete(name)  # made, but empty
    state["contacts"] = name if contacts else None
    state["current"] = ligand
    _self.zoom("(%s) or (%s)" % (ligand, site), animate=-1)
    if not quiet:
        print(
            " ligand_next: %s of %s (%d of %d), %s."
            % (
                label,
                model,
                index + 1,
                len(rows),
                "polar contacts by geometry in '%s'" % name
                if contacts
                else "no polar contacts",
            )
        )
    return ligand
