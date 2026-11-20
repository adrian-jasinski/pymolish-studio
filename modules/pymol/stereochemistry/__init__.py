import sys
import pymol
cmd = sys.modules["pymol.cmd"]


def assign_stereo(selection='all', state=-1, method='', quiet=1, prop='stereo',
        _self=cmd):
    '''
DESCRIPTION

    Assign the "stereo" atom property (R/S stereochemistry) from the
    coordinates and bonds, with rdkit's CIP rules. The property is not
    updated by itself: run the command again after an edit.

    Needs rdkit: pip install 'pymolish[chem]'; the downloadable builds
    include it.

USAGE

    assign_stereo [selection [, state [, method ]]]

ARGUMENTS

    selection = str: atom selection {default: all}

    state = int: object state {default: -1 (current)}

    method = rdkit: the only method {default: rdkit}

EXAMPLE

    fragment cys
    assign_stereo
    label stereo R+S, stereo
    '''
    from ..smiles import rdkit

    if method not in ('', 'rdkit'):
        raise pymol.CmdException('assign_stereo: the only method is rdkit')

    Chem, _ = rdkit()
    count = 0

    for oname in _self.get_object_list(selection):
        sele = '(%s) & model %s' % (selection, oname)
        mol = Chem.MolFromMolBlock(
            _self.get_str('mol', sele, state), sanitize=False, removeHs=False)
        if mol is None or mol.GetNumAtoms() != _self.count_atoms(sele):
            raise pymol.CmdException(
                'assign_stereo: rdkit cannot read ' + oname)
        # no sanitization: structures from PDB files come without bond
        # orders and charges, and the CIP rules need neither
        mol.UpdatePropertyCache(strict=False)
        Chem.AssignStereochemistryFrom3D(mol)
        labels = [
            a.GetProp('_CIPCode') if a.HasProp('_CIPCode') else ''
            for a in mol.GetAtoms()
        ]
        _self.alter(sele, prop + ' = next(labels)',
                    space={'labels': iter(labels), 'next': next})
        count += len(labels) - labels.count('')

    if not int(quiet):
        print(' assign_stereo: %d chiral centers' % count)
