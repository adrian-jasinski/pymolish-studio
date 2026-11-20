'''
Various morphing workflows

(c) 2013 Schrodinger, Inc.
(c) 2011 Thomas Holder
(c) 2009 DeLano Scientific LLC.
'''

import pymol
cmd = __import__("sys").modules["pymol.cmd"]

def _matched(sele1, sele2, state1, state2, match, _self):
    """(selection of the atoms of sele1 that have a partner in sele2, their
    coordinates, the partners' coordinates), paired by a sequence alignment.
    """
    import numpy

    if match not in ('align', 'super'):
        raise pymol.CmdException('morph: match must be align or super')

    aln = _self.get_unused_name('_morph_aln')
    tmp = _self.get_unused_name('_morph_sele')
    try:
        getattr(_self, match)(sele1, sele2, cycles=0, transform=0, object=aln,
                mobile_state=state1, target_state=state2, quiet=1)
        _self.select(tmp, '(%s) & %s' % (sele1, aln), 0)
        xyz1, xyz2 = {}, {}
        _self.iterate_state(state1, tmp, 'xyz[model, index] = (x, y, z)',
                space={'xyz': xyz1})
        _self.iterate_state(state2, '(%s) & %s' % (sele2, aln),
                'xyz[model, index] = (x, y, z)', space={'xyz': xyz2})
        partner = dict(
            (a, b) if a in xyz1 else (b, a)
            for a, b in _self.get_raw_alignment(aln))
        keys = []
        _self.iterate(tmp, 'keys.append((model, index))', space={'keys': keys})
        if not keys or any(partner.get(k) not in xyz2 for k in keys):
            raise pymol.CmdException('morph: no atoms could be matched')
        return (tmp,
                numpy.array([xyz1[k] for k in keys]),
                numpy.array([xyz2[partner[k]] for k in keys]))
    except BaseException:
        _self.delete(tmp)
        raise
    finally:
        _self.delete(aln)


def morph(name, sele1, sele2=None, state1=-1, state2=-1, refinement=3,
        steps=30, method='linear', match='align', quiet=1, _self=cmd):
    '''
DESCRIPTION

    Creates an interpolated trajectory between two or multiple conformations.
    If the two input objects are not the same, match them based on sequence
    alignment. The conformations are not superposed: do that first.

    The method is linear interpolation of the coordinates, followed by
    sculpting of the intermediates, which restores bond lengths, angles and
    planar groups. It is quick; intermediates of a large motion can still
    look distorted. (RigiMOL of the commercial PyMOL is not part of this
    program.)

ARGUMENTS

    name = string: name of object to create

    sele1 = string: atom selection of first conformation

    sele2 = string: atom selection of second conformation {default: <sele1>}

    state1 = int: sele1 state {default: 1}. If state1=0 and sele1 has N
    states, create N morphings between all consecutive states and back from
    state N to 1 (so the morph will have N*steps states). If state2=0, create
    N-1 morphings and stop at last state.

    state2 = int: sele2 state {default: 2 if sele1=sele2, else 1}

    refinement = int: number of sculpting refinement cycles to clean
    distorted intermediates {default: 3}

    steps = int: number of states for sele2 object {default: 30}

    method = string: linear, the only method {default: linear}

    match = string: align or super, the command that pairs the atoms of
    two different objects {default: align}

EXAMPLE

    fetch 1akeA 4akeA, async=0
    align 1akeA, 4akeA
    morph mout, 1akeA, 4akeA
    '''
    import numpy

    state1, state2 = int(state1), int(state2)
    refinement, steps = int(refinement), int(steps)

    if method != 'linear':
        raise pymol.CmdException(
            'morph: the only method is linear (RigiMOL is not available)')
    if steps < 1:
        raise pymol.CmdException('morph: steps must be 1 or more')

    loop = False
    source = sele1
    tmp = None

    try:
        if sele2 is None or sele2 == sele1:
            if state1 == 0:
                states = range(1, _self.count_states(sele1) + 1)
                loop = state2 != 0
            else:
                states = [state1 if state1 > 0 else 1,
                          state2 if state2 > 0 else 2]
            confs = [_self.get_coords(sele1, state) for state in states]
            if any(c is None or len(c) != len(confs[0]) for c in confs):
                raise pymol.CmdException(
                    'morph: the states do not have the same atoms')
            state1 = states[0]
        else:
            state1 = state1 if state1 > 0 else 1
            tmp, *confs = _matched(sele1, sele2, state1,
                    state2 if state2 > 0 else 1, match, _self)
            source = tmp

        if len(confs) < 2:
            raise pymol.CmdException('morph: needs two conformations')
        if loop:
            confs.append(confs[0])

        _self.delete(name)
        _self.create(name, source, state1, 1, zoom=0)
        # ponytail: relies on "create" keeping the atom order of its source,
        # which holds for every object that is sorted (all loaded ones are)
        if not numpy.allclose(_self.get_coords(name, 1), confs[0], atol=1e-3):
            _self.delete(name)
            raise pymol.CmdException('morph: atoms of the source are not in '
                                     'sorted order; "sort" the object first')

        # every piece has "steps" states and starts at its conformation; the
        # last piece of an open morph also ends at its conformation
        fixed = set()
        count = 0
        for i in range(len(confs) - 1):
            last = not loop and i == len(confs) - 2
            for k in range(steps):
                f = k / (max(steps - 1, 1) if last else steps)
                count += 1
                if f in (0., 1.):
                    fixed.add(count)
                _self.load_coordset(
                    confs[i] * (1. - f) + confs[i + 1] * f, name, count)

        if refinement > 0 and len(confs[0]) > 3:
            # local geometry only, taken from the first conformation
            _self.set('sculpt_field_mask', 0x01F, name)
            _self.sculpt_activate(name, 1)
            for state in range(1, count + 1):
                if state not in fixed:
                    _self.sculpt_iterate(name, state, 10 * refinement)
            _self.sculpt_deactivate(name)
            _self.unset('sculpt_field_mask', name)
    finally:
        if tmp:
            _self.delete(tmp)

    if not int(quiet):
        print(' morph: %d states, %d atoms' % (count, len(confs[0])))

# vi: ts=4:sw=4:smarttab:expandtab
