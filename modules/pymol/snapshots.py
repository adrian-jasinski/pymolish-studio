"""
Undo and redo for what the coordinate ring of the core does not cover.
Before a row of the preset menu runs, the session is kept in memory; "undo"
puts it back and keeps the state it leaves for "redo". The first piece of
21g (docs/plans/21-commercial-features.md); new code, MIT.
"""

cmd = __import__("sys").modules["pymol.cmd"]

# ponytail: a snapshot is the whole session (1AON, 59,192 atoms: 0.15 s and
# 17.8 MB), so "undo" also takes back what was done after the preset, and a
# snapshot comes before the coordinate ring of the core: the two are not in
# one order. 21g replaces both limits by one stack of what each command
# changed.
STEPS = 5
ATOMS = 600_000  # over all kept steps; about 180 MB at 300 bytes per atom

_undo, _redo = [], []  # (atoms, session, state of preset.py and stage.py)


def _take(_self):
    from . import preset, stage

    return (
        _self.count_atoms("all"),
        _self.get_session(compress=0, cache=0),
        (preset.solvent, preset._lit_by_preset, dict(stage._state)),
    )


def keep(_self=cmd):
    """Call before a change that "undo" is to take back."""
    atoms = _self.count_atoms("all")
    if atoms > ATOMS:
        print(
            " Undo: %d atoms are too many to keep; this step cannot be undone." % atoms
        )
        return
    _undo.append(_take(_self))
    _redo.clear()
    while len(_undo) > STEPS or sum(step[0] for step in _undo) > ATOMS:
        del _undo[0]


def step(back, _self=cmd):
    """Undo (`back`) or redo one kept step; false when there is none."""
    from . import preset, stage

    source, target = (_undo, _redo) if back else (_redo, _undo)
    if not source:
        return False
    target.append(_take(_self))
    _, session, (preset.solvent, preset._lit_by_preset, state) = source.pop()
    stage._state.update(state)
    _self.set_session(session)
    return True


def clear():
    """The kept steps belong to a session that is gone."""
    _undo.clear()
    _redo.clear()
