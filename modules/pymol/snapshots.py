"""
Undo and redo (21g, docs/plans/21-commercial-features.md; new code, MIT).

One stack, in the order things were done, of two kinds of steps:

- a snapshot of the session, kept before a step that adds, removes or edits
  something: a line of the command line or of a script, a menu row, or a
  command of the list CHANGE called from Python;
- a move of the coordinate ring of the core (dragging atoms, the sculpting
  and builder tools, push_undo), which keeps only coordinates and is cheap.

A step is opened by the parser for every line it runs at the top level
(pymol/parser.py), by every command of CHANGE called outside a step, and by
`undoable`. Its snapshot is kept lazily, by the first command in it that
changes something, so a line that only looks or turns the view keeps none.
Commands of AMBIENT (settings) keep one only inside a step: the program sets
settings itself all the time. Snapshots follow the setting suspend_undo;
`keep` (preset menu, chat, sequence window) always keeps one.
"""

import contextlib
import functools
import inspect

cmd = __import__("sys").modules["pymol.cmd"]

# shortcut: a snapshot is the whole session (1AON, 59,192 atoms: 0.15 s and
# 17.8 MB), so a step restores the view and everything else as it was; a
# change that only some commands would need is the upgrade, per command.
STEPS = 20
ATOMS = 600_000  # over all kept steps; about 180 MB at 300 bytes per atom

CHANGE = """
    fragment fab fnab create copy copy_to pseudoatom set_raw_alignment
    isosurface isodot isomesh isolevel map_new group ungroup extract symexp
    gradient join_states split_states split_chains distance angle dihedral
    load load_raw load_traj fetch delete remove remove_picked alter
    alter_state h_add h_fill replace attach fuse bond unbond cycle_valence
    valence protect deprotect mask unmask flag sort set_name update clean fit
    pair_fit align super cealign intra_fit translate rotate origin
    set_geometry invert torsion select deselect color bg_color show hide
    show_as cartoon label spectrum
""".split()
AMBIENT = "set unset set_bond unset_bond".split()

_undo, _redo = [], []  # (label, atoms, (session, module state) or None)
_step = None  # [label, entry]: entry None (not kept yet), False (keep none)
_ring = None  # coordinate sets of the core's rings counted into the stacks
_warned = False


def _ring_saves(_self):
    with _self.lockcm:
        return _self._cmd.undo(_self._COb, 0)


def _sync(_self):
    """Moves of the coordinate ring since the last look become steps."""
    global _ring
    saves = _ring_saves(_self)
    if _ring is not None and saves > _ring:
        _undo.extend([("move", 0, None)] * (saves - _ring))
        _redo.clear()
        _trim()
    _ring = saves


def _trim():
    while len(_undo) > STEPS or sum(step[1] for step in _undo) > ATOMS:
        del _undo[0]


def _take(_self):
    from . import preset, stage

    return (
        _self.get_session(compress=0, cache=0),
        (preset.solvent, preset._lit_by_preset, dict(stage._state)),
    )


def keep(_self=cmd, label=None):
    """Keep the session before a change that "undo" is to take back; inside
    a step, this is its snapshot. Returns the kept step, or None."""
    global _warned
    _sync(_self)
    if label is None:
        label = _step[0] if _step else "change"
    atoms = _self.count_atoms("all")
    if atoms > ATOMS:
        if not _warned:
            print(
                " Undo: %d atoms are too many to keep; this step cannot be undone."
                % atoms
            )
        _warned = True
        return None
    _warned = False
    entry = (label, atoms, _take(_self))
    _undo.append(entry)
    _redo.clear()
    _trim()
    if _step is not None and _step[1] is None:
        _step[1] = entry
    return entry


@contextlib.contextmanager
def undoable(label, _self=cmd, eager=False):
    """One step of undo for what runs inside; nested, it adds nothing. A
    step that fails is taken off again."""
    global _step, _ring
    if _step is not None:
        yield
        return
    _step = [label, None]
    redo = list(_redo)
    try:
        if eager and not keep(_self):
            _step[1] = False
        yield
    except BaseException:
        entry = _step[1]
        if entry and _undo and _undo[-1] is entry:
            _undo.pop()
            _redo[:] = redo
        raise
    finally:
        # the ring saves of a command (fab, torsion ...) are part of it
        _ring = _ring_saves(_self)
        _step = None


@contextlib.contextmanager
def paused():
    """What runs inside keeps no snapshot (cmd.UndoPauseCM)."""
    global _step
    outer, _step = _step, ["", False]
    try:
        yield
    finally:
        _step = outer


def _run(func, args, kwargs, _self):
    """Run a command of CHANGE or AMBIENT inside a step: the first one keeps
    the snapshot, and takes it back if it fails (the parser goes on)."""
    entry = None
    if _step[1] is None:
        if not _self.get_setting_int("suspend_undo"):
            entry = keep(_self, _step[0])
        _step[1] = entry or False  # else not again in this step
    try:
        return func(*args, **kwargs)
    except BaseException:
        if entry and _undo and _undo[-1] is entry:
            _undo.pop()
            _step[1] = None
        raise


def _wrap(func, ambient):
    label = func.__name__
    first = next(iter(inspect.signature(func).parameters), None)

    @functools.wraps(func)
    def command(*args, **kwargs):
        _self = kwargs.get("_self", cmd)
        name = args[0] if args else kwargs.get(first)
        if isinstance(name, str) and name.startswith("_"):
            return func(*args, **kwargs)  # the program's own temporary names
        if _step is not None:
            return _run(func, args, kwargs, _self)
        if ambient:
            return func(*args, **kwargs)
        with undoable(label, _self):
            return _run(func, args, kwargs, _self)

    return command


def install(api):
    """Wrap the commands of CHANGE and AMBIENT in the namespace of pymol.api,
    before pymol.cmd and agent.py take them."""
    for names, ambient in ((CHANGE, False), (AMBIENT, True)):
        for name in names:
            api[name] = _wrap(api[name], ambient)


def step(back, _self=cmd):
    """Undo (`back`) or redo one step. Returns its label, or None."""
    from . import preset, stage

    global _ring
    _sync(_self)
    source, target = (_undo, _redo) if back else (_redo, _undo)
    if not source:
        return None
    label, _, data = source.pop()
    if data is None:
        with _self.lockcm:
            _ring = _self._cmd.undo(_self._COb, -1 if back else 1)
        target.append((label, 0, None))
        return label
    target.append((label, _self.count_atoms("all"), _take(_self)))
    session, (preset.solvent, preset._lit_by_preset, state) = data
    stage._state.update(state)
    with paused():
        _self.set_session(session)
    # the objects are new: what their coordinate rings held is gone
    _undo[:] = [s for s in _undo if s[2] is not None]
    _redo[:] = [s for s in _redo if s[2] is not None]
    _ring = _ring_saves(_self)
    return label


def peek(_self=cmd):
    """The labels of the next undo and redo, None where there is none."""
    _sync(_self)
    return (_undo[-1][0] if _undo else None, _redo[-1][0] if _redo else None)


def clear(_self=cmd):
    """The kept steps belong to a session that is gone."""
    global _ring
    _undo.clear()
    _redo.clear()
    _ring = _ring_saves(_self)
