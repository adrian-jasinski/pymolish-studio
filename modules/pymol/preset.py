#A* -------------------------------------------------------------------
#B* This file contains source code for the PyMOL computer program
#C* Copyright (c) Schrodinger, LLC.
#D* -------------------------------------------------------------------
#E* It is unlawful to modify or remove this copyright notice.
#F* -------------------------------------------------------------------
#G* Please see the accompanying LICENSE file for further information.
#H* -------------------------------------------------------------------
#I* Additional authors of this source file include:
#-*
#-*
#-*
#Z* -------------------------------------------------------------------

cmd = __import__("sys").modules["pymol.cmd"]
from . import util
import traceback

polar_contacts_suffix = "_pol_conts"
default_polar_contacts = "polar_contacts"

tmp_sele = "_p_tmp"

prot_and_dna_sele = "(resn ALA+CYS+CYX+ASP+GLU+PHE+GLY+HIS+HID+HIE+HIP+HISE+HISD+HISP+ILE+LYS+LEU+MET+MSE+ASN+PRO+GLN+ARG+SER+THR+VAL+TRP+TYR+A+C+T+G+U+DA+DC+DT+DG+DU+DI)"
wat_sele = "solvent"
ion_sele = "(resn CA,HG,K,NA,ZN,MG,CL)"
solv_sele = "("+wat_sele+"|"+ion_sele+")"
lig_excl = "(resn MSE)"
lig_sele = "((hetatm or not "+prot_and_dna_sele+") and not ("+solv_sele+"|"+ion_sele+"|"+lig_excl+"))"
lig_and_solv_sele = "("+lig_sele+"|"+solv_sele+")"

def get_sname_oname_dname(selection, _self=cmd):
    '''
    Get a named selection, object names and a distance (polar contacts) name
    '''
    _self.select(tmp_sele, selection)

    if selection not in _self.get_object_list():
        selection = ' '.join(_self.get_object_list(tmp_sele))

    if selection and ' ' not in selection:
        dname = selection + polar_contacts_suffix
    else:
        dname = default_polar_contacts

    return tmp_sele, selection, dname

def _prepare(selection,polar_contacts=None,_self=cmd):
    cmd=_self
    # this function should undo everything that is done by any preset function in this module
    # (except for coloring)

    s, selection, dname = get_sname_oname_dname(selection, _self=cmd)

    cmd.cartoon("auto",s)
    cmd.hide("everything",s)

    cmd.set("two_sided_lighting",0) # global
    cmd.unset("cartoon_debug") # global
    cmd.unset("ray_transparency_oblique") # global
    cmd.unset("transparency",s)
    cmd.unset("cartoon_transparency",s)
    cmd.unset("cartoon_transparency",selection)
    cmd.unset("surface_color", selection)
    cmd.unset("surface_color", s) # per atom: interaction
    cmd.unset("surface_quality", selection)
    cmd.unset("surface_type",selection)
    cmd.unset("sphere_scale",s)
    cmd.unset_bond("stick_radius",s,s)
    cmd.unset_bond("stick_color",s,s)
    cmd.unset("cartoon_highlight_color",selection)
    cmd.unset("cartoon_fancy_helices",selection)
    cmd.unset("cartoon_smooth_loops",selection)
    cmd.unset("cartoon_flat_sheets",selection)
    cmd.unset("cartoon_side_chain_helper",selection)
    if polar_contacts is None:
        polar_contacts = dname
        if polar_contacts in cmd.get_names('objects'):
            cmd.delete(polar_contacts)

    return s, selection, dname

def simple(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = _prepare(selection, _self=cmd)[:2]
    util.cbc(s,_self=cmd)
    cmd.show("ribbon",s)
    cmd.show("lines","(byres (("+s+" & r. CYS+CYX & n. SG) & bound_to ("+s+" & r. CYS+CYX & n. SG))) & n. CA+CB+SG")
    # try to show what covalent ligands are connected to...
    cmd.show("sticks","("+lig_sele+" and ("+s+")) extend 2")
    cmd.show("sticks","byres (("+lig_sele+" and ("+s+") and not resn ACE+NAC+NME+NH2) extend 1)")
    cmd.hide("sticks","("+s+") and ((not rep sticks) extend 1)")
    cmd.show("sticks","("+lig_sele+" and ("+s+")) extend 2")
    # color by atom if lines or sticks are shown
    util.cnc("(( rep lines or rep sticks or ("+lig_and_solv_sele+")) and ("+s+"))",_self=cmd)
    cmd.show("nonbonded","("+lig_and_solv_sele+" and ("+s+"))")
    cmd.show("lines","("+lig_and_solv_sele+" and ("+s+"))")
    cmd.delete(s)

def _ball_and_stick_ligand(lig, _self=cmd):
    # thin dark sticks and small balls, after BallnStick of bobbypaton's
    # pymol_style.py gist
    _self.show("sticks", lig)
    _self.show("spheres", lig)
    _self.set_bond("stick_radius", 0.07, lig, lig)
    _self.set_bond("stick_color", "grey30", lig, lig)
    _self.set("sphere_scale", 0.18, lig)
    _self.set("sphere_scale", 0.13, lig + " & elem H")
    # not the guide atom of a modified residue: it colors the cartoon
    _self.color("grey85", lig + " & elem C & !guide")

def simple_no_solv(selection="(all)",_self=cmd):
    cmd=_self
    simple(selection,_self=_self)
    s, selection = get_sname_oname_dname(selection, _self=_self)[:2]
    cmd.hide("everything","("+solv_sele+" and "+s+")")
    cmd.delete(s)

def ligands(selection="(all)",_self=cmd):
    cmd=_self
    try:
        s, selection, polar_contacts = _prepare(selection, _self=cmd)
        host = "_preset_host"
        solvent = "_preset_solvent"
        near_solvent = "_preset_solvent"
        lig = "_preset_lig"
        cmd.select(host,s+" and "+prot_and_dna_sele)
        cmd.select(solvent,s+" and "+solv_sele)
        cmd.select(lig,s+" and "+lig_sele)
        cmd.select(near_solvent,s+" and ("+solvent+" within 4 of "+lig+")")

        util.cbac("(("+s+") and not elem C)",_self=cmd)
        cmd.hide("everything",s)
        cmd.show("cartoon",host)
        cmd.show("lines","("+s+" and byres ("+host+" within 5 of "+lig+"))")
        _ball_and_stick_ligand(lig, _self=cmd)
        cmd.show("sticks",solvent+" and neighbor "+lig)
        cmd.show("lines","("+s+" and (rep lines extend 1) and "+lig+")")

        if cmd.count_atoms(lig):
            cmd.dist(polar_contacts,host+"|"+near_solvent,lig+"|"+near_solvent,
                     mode=2,quiet=1,label=0,reset=1) # hbonds
            if polar_contacts in cmd.get_names():
                cmd.enable(polar_contacts)
                cmd.hide("labels",polar_contacts)
                cmd.show("dashes",polar_contacts)
        else:
            cmd.delete(polar_contacts)
        cmd.show("nonbonded",lig+"|"+host+"|"+near_solvent)
        if cmd.count_atoms(lig):
            cmd.zoom(lig,3, animate=1)
        cmd.delete(host)
        cmd.delete(solvent)
        cmd.delete(near_solvent)
        cmd.delete(lig)
    except:
        traceback.print_exc()
    cmd.delete(s)

def ball_and_stick(selection="(all)",mode=1,_self=cmd):
    cmd=_self
    s, selection = _prepare(selection, _self=cmd)[:2]
    if mode == 1:
        cmd.hide("everything",s)
        cmd.set_bond("stick_color","white",s,s)
        cmd.set_bond("stick_radius","0.14",s,s)
        cmd.set("sphere_scale","0.25",s)
        cmd.show("sticks",s)
        cmd.show("spheres",s)
    elif mode == 2:
        cmd.hide("everything",s)
        cmd.set_bond("stick_color","white",s,s)
        cmd.set_bond("stick_radius","-0.14",s,s)
        cmd.set("stick_ball","1")
        cmd.set("stick_ball_ratio",-1.0)
        cmd.set("stick_ball_color","atomic")
        cmd.show("sticks",s)
    cmd.delete(s)

def b_factor_putty(selection="(name CA+P)",_self=cmd):
    cmd=_self
    s, selection = _prepare(selection, _self=cmd)[:2]
    cmd.select(s,"(name CA+P) and ("+selection+") and present")
    cmd.show("cartoon",s)
    cmd.set("cartoon_flat_sheets",0,selection)
    cmd.cartoon("putty",s)
    cmd.spectrum("b",selection=s)
    cmd.delete(s)

def ligand_cartoon(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.set("cartoon_side_chain_helper",1,selection)
    cmd.hide("surface")
    cmd.delete(s)

def ligand_sites(selection="(all)",_self=cmd):
    cmd=_self
    try:
        s, selection, polar_contacts = _prepare(selection, _self=cmd)
        host = "_preset_host"
        solvent = "_preset_solvent"
        near_solvent = "_preset_solvent"
        lig = "_preset_lig"
        cmd.select(host,s+" and "+prot_and_dna_sele)
        cmd.select(solvent,s+" and "+solv_sele)
        cmd.select(lig,s+" and "+lig_sele)
        cmd.select(near_solvent,s+" and ("+solvent+" within 4 of "+lig+")")
        cmd.flag("ignore",host,"clear")
        cmd.flag("ignore",lig+"|"+solvent,"set")

        util.cbac("(("+s+") and not elem C)",_self=cmd)
        cmd.hide("everything",s)
        cmd.show("cartoon",host)
        cmd.show("lines","("+s+" and byres ("+host+" within 5 of "+lig+"))")
        cmd.show("surface","("+s+" and ((rep lines expand 4) within 6 of "+lig+"))")
        cmd.set("two_sided_lighting",1) # global setting
        cmd.set("transparency",0,s)
        cmd.set("surface_quality",0, selection)

        _ball_and_stick_ligand(lig, _self=cmd)
        cmd.show("sticks",solvent+" and neighbor "+lig)
        cmd.show("lines","("+s+" and (rep lines extend 1) and "+lig+")")

        if cmd.count_atoms(lig):
            cmd.dist(polar_contacts,host+"|"+near_solvent,lig+"|"+near_solvent,mode=2,quiet=1,label=0,reset=1) # hbonds
            if polar_contacts in cmd.get_names():
                cmd.enable(polar_contacts)
                cmd.hide("labels",polar_contacts)
                cmd.show("dashes",polar_contacts)
        else:
            cmd.delete(polar_contacts)

        cmd.show("nb_spheres",lig+"|"+host+"|"+near_solvent)

        # add lines because nb_spheres won't show solvent with hydrogens
        cmd.show("lines", near_solvent)

        if cmd.count_atoms(lig):
            cmd.zoom(lig,3, animate=1)
        cmd.delete(host)
        cmd.delete(solvent)
        cmd.delete(near_solvent)
        cmd.delete(lig)
    finally:
        pass

    return s, selection, polar_contacts

def ligand_sites_hq(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.set("surface_quality","1",selection)
    cmd.set("surface_type",0,selection)
    cmd.delete(s)

def ligand_sites_trans(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.show("sticks",s+" and rep lines")
    cmd.hide("lines",s+" and rep lines")
    cmd.set("transparency","0.33",s)
    cmd.set("surface_type",0,selection)
    cmd.set("surface_quality",0,selection)
    cmd.delete(s)

def ligand_sites_trans_hq(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.show("sticks",s+" and rep lines")
    cmd.hide("lines",s+" and rep lines")
    cmd.set("transparency","0.33",s)
    cmd.set("surface_type",0,selection)
    cmd.set("surface_quality",1,selection)
    cmd.delete(s)

def ligand_sites_mesh(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.show("sticks",s+" and rep lines")
    cmd.hide("lines",s+" and rep lines")
    cmd.set("surface_type","2",selection)
    cmd.set("surface_quality","0",selection)
    cmd.delete(s)

def ligand_sites_dots(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = ligand_sites(selection, _self)[:2]
    cmd.show("sticks",s+" and rep lines")
    cmd.hide("lines",s+" and rep lines")
    cmd.set("surface_type","1",selection)
    cmd.set("surface_quality","1",selection)
    cmd.delete(s)

def technical(selection="(all)",_self=cmd):
    cmd=_self
    s, selection, polar_contacts = _prepare(selection, _self=cmd)
    # the protein keeps its colors: only ligands and non-carbon atoms
    util.cbc("("+lig_sele+" and ("+s+") and not guide)",_self=cmd)
    util.cbac("(("+s+") and not elem C)",_self=cmd)
    cmd.show("nonbonded",s)
    cmd.show("lines","((("+s+") and not "+lig_sele+") extend 1)")
    cmd.show("sticks","("+lig_sele+" and ("+s+"))")
    cmd.show("cartoon",s)
    cmd.dist(polar_contacts,s,s,mode=2,label=0,reset=1) # hbonds
    if polar_contacts in cmd.get_names():
        cmd.enable(polar_contacts)
        cmd.set("dash_width",1.5,polar_contacts)
        cmd.hide("labels",polar_contacts)
        cmd.show("dashes",polar_contacts)
    cmd.show("nonbonded","(("+lig_sele+"|resn HOH+WAT+H2O) and ("+s+"))")
    cmd.delete(s)

def pretty_solv(selection="(all)",_self=cmd):
    pretty(selection, solv=True, _self=_self)

def pretty(selection="(all)", *, solv=False, _self=cmd):
    cmd=_self
    s, selection = _prepare(selection, _self=cmd)[:2]
    cmd.dss(s,preserve=1)
    cmd.cartoon("auto",s)
    cmd.show("cartoon",s)
    if solv:
        cmd.show("licorice", f"({lig_sele}|{wat_sele}) and ?{s}")
    else:
        cmd.show("sticks", f"({lig_sele}) and ?{s}")
    util.cbc("("+lig_sele+" and ("+s+"))",_self=cmd)
    util.cbac("("+lig_sele+" and ("+s+") and not elem C)",_self=cmd)
    cmd.spectrum("count",selection="(elem C and ("+s+") and not "+lig_sele+")")
    cmd.set("cartoon_highlight_color",-1,selection)
    cmd.set("cartoon_fancy_helices",0,selection)
    cmd.set("cartoon_smooth_loops",0,selection)
    cmd.set("cartoon_flat_sheets",1,selection)
    cmd.set("cartoon_side_chain_helper",0,selection)
    cmd.delete(s)

pretty_no_solv = pretty

def pub_solv(selection="(all)",_self=cmd):
    publication(selection, solv=True, _self=_self)

def publication(selection="(all)", *, solv=False, _self=cmd):
    cmd=_self
    pretty(selection, solv=solv, _self=_self)
    s, selection = get_sname_oname_dname(selection, _self=_self)[:2]
    cmd.set("cartoon_smooth_loops",1,selection)
    cmd.set("cartoon_highlight_color","grey50",selection)
    cmd.set("cartoon_fancy_helices",1,selection)
    cmd.set("cartoon_flat_sheets",1,selection)
    cmd.set("cartoon_side_chain_helper",0,selection)
    cmd.delete(s)

pub_no_solv = publication

def default(selection="(all)",_self=cmd):
    cmd=_self
    s, selection = _prepare(selection, _self=cmd)[:2]
    cmd.show("lines",s)
    cmd.show("nonbonded",s)
    color=cmd.get_object_color_index(selection)
    if color<0:
        util.cbag(selection,_self=cmd)
    else:
        util.cnc(selection,_self=cmd)
        cmd.color(str(color),"("+s+") and elem C")
    cmd.delete(s)


def interface(selection='*', _self=cmd):
    '''
    Protein-Protein interface preset, mimics the BioLuminate preset
    '''
    s = _prepare(selection, _self=_self)[0]

    # temporary selection names
    s_interface = _self.get_unused_name('_iface')

    # interface atoms
    _self.select(s_interface, '?%s & (%s)' % (s, ' '.join(
        '((chain "%s") around 4.5) ' % (chain)
        for chain in _self.get_chains(s))), 0)

    # Color by chain, non-carbon by element
    util.cbc(s, _self=_self)
    _self.color('atomic', '?%s & !(elem C)' % (s))

    # Change everything to cartoons
    _self.show_as('cartoon', s)

    # interface residues as sticks
    _self.show('sticks', 'byres ?' + s_interface)
    _self.show('nb_spheres', '?' + s_interface)

    # delete temporary selections
    _self.delete(s_interface)
    _self.delete(s)


def _units(s, _self=cmd):
    '''
    The polymer chains of the named selection `s` as (selection, chain)
    pairs, one per object and chain.
    '''
    return [
        ('(?%s & %%%s & polymer & chain "%s")' % (s, model, chain), chain)
        for model in _self.get_object_list('?' + s) or ()
        for chain in _self.get_chains('?%s & %%%s & polymer' % (s, model))
    ]


def _contacts(name, pairs, _self=cmd):
    '''
    Polar contacts between each pair of selections, as dashes without
    labels in one measurement object.
    '''
    for i, (a, b) in enumerate(pairs):
        # zoom=0: a preset of this kind leaves the camera where it is
        _self.dist(name, a, b, mode=2, quiet=1, label=0, reset=not i, zoom=0)
    if name in _self.get_names():
        _self.enable(name)
        _self.hide('labels', name)
        _self.show('dashes', name)


def interaction(selection='*', _self=cmd):
    '''
    Protein-protein interaction: every chain as cartoon in its own color
    inside a faint surface of that color, the side chains that touch
    another chain as sticks, and the polar contacts between chains as
    dashes.
    '''
    from . import palettes
    s, selection, dname = _prepare(selection, _self=_self)
    units = _units(s, _self)

    # one color per chain, also for its surface: the element colors of the
    # sticks below would speckle it
    colors = palettes.cycle()
    for i, (unit, _) in enumerate(units):
        color = str(colors[i % len(colors)])
        _self.color(color, unit)
        _self.set('surface_color', color, unit)

    _self.show('cartoon', 'polymer & ?' + s)
    _self.show('licorice', '(organic | inorganic) & ?' + s)
    _self.show('surface', 'polymer & ?' + s)
    _self.set('transparency', 0.75, s)

    # atoms within 4.5 A of another chain
    iface = _self.get_unused_name('_iface')
    _self.select(iface, 'none')
    for unit, _ in units:
        _self.select(iface, '?%s | ((polymer & ?%s & !%s) within 4.5 of %s)'
                     % (iface, s, unit, unit), 0)
    _self.set('cartoon_side_chain_helper', 1, selection)
    _self.show('sticks', 'byres ?' + iface)
    _self.color('atomic', '((byres ?%s) | ((organic | inorganic) & ?%s)) & !(elem C)'
                % (iface, s))
    _contacts(dname, [
        ('?%s & %s' % (iface, a), '?%s & %s' % (iface, b))
        for i, (a, _) in enumerate(units) for b, _ in units[i + 1:]
    ], _self)

    _self.delete(iface)
    _self.delete(s)


# The start of framework 2 of an antibody variable domain: heavy chains and
# single-domain antibodies (W-V-R-Q-A-P-G, W-F-R-Q-A-P-G, mouse W-V-K-Q-R-P-G),
# light chains (kappa W-Y-Q-Q-K-P-G, lambda W-Y-Q-Q-L-P-G).
_heavy_re = 'W[VIFY][RK]Q.PG'
_light_re = 'W[YFL][QLH]Q.[PSA]G'


def antibody(selection='*', _self=cmd):
    '''
    Antibody with its antigen: the heavy chain blue and the light chain
    light blue, as cartoon; the antigen as a sand-colored surface with the
    epitope in orange; the residues of the antibody that touch the antigen
    as sticks; the polar contacts between the two as dashes.

    Antibody chains are found by the conserved start of framework 2 in
    their sequence; a chain named H or L fills a role that the sequences
    left empty. Without any antibody chain this is "interaction".
    '''
    import re
    s, selection, dname = _prepare(selection, _self=_self)
    heavy, light, other = [], [], []
    for unit, chain in _units(s, _self):
        lines = _self.get_fastastr(unit).splitlines()
        sequence = ''.join(x for x in lines if not x.startswith('>'))
        if re.search(_heavy_re, sequence):
            heavy.append(unit)
        elif re.search(_light_re, sequence):
            light.append(unit)
        else:
            other.append((unit, chain))
    for role, name in ((heavy, 'H'), (light, 'L')):
        if not role:
            role.extend(unit for unit, chain in other if chain == name)
    antigen = [unit for unit, chain in other if unit not in heavy + light]
    if not heavy and not light:
        print(' preset.antibody: no antibody chain found, showing "interaction".')
        _self.delete(s)
        return interaction(selection, _self=_self)

    ab = '(%s)' % ' | '.join(heavy + light)
    ag = '(%s)' % (' | '.join(antigen) or 'none')
    for units, color in ((heavy, 'skyblue'), (light, 'lightblue'), (antigen, 'wheat')):
        for unit in units:
            _self.color(color, unit)
    epitope = '(%s within 4.5 of %s)' % (ag, ab)
    paratope = '(%s within 4.5 of %s)' % (ab, ag)
    _self.color('orange', 'byres ' + epitope)
    # element colors only on what is drawn as sticks: the surface of the
    # antigen stays sand and orange
    _self.color('atomic', '((byres %s) | ((organic | inorganic) & ?%s)) & !(elem C)'
                % (paratope, s))

    _self.show('cartoon', ab)
    _self.show('surface', ag)
    _self.show('licorice', '(organic | inorganic) & ?' + s)
    _self.set('cartoon_side_chain_helper', 1, selection)
    _self.show('sticks', 'byres ' + paratope)
    _contacts(dname, [(paratope, epitope)], _self)

    _self.delete(s)


def cartoon_transparency(value, selection='*', _self=cmd):
    '''
    The cartoon transparency rows of the preset menu: for every object of
    the selection. The next preset makes the cartoon opaque again.
    '''
    for name in _self.get_object_list(selection) or ():
        _self.set('cartoon_transparency', value, name)


def classified(selection='*', _self=cmd):
    '''
    Equivalent of "auto_show_classified" setting. Sets representations
    according to atom classification ("auto_classify_atoms"). Does not
    change any colors or settings.
    '''
    s = _prepare(selection, _self=_self)[0]

    _self.show_as('cartoon', 'polymer & %' + s)
    _self.show_as('sticks', 'organic & %' + s)
    _self.show_as('spheres', 'inorganic & %' + s)

    _self.delete(s)


def glass(selection='*', _self=cmd):
    '''
    Cartoon and ligand sticks by chain, inside a transparent white surface
    that gets denser toward its edges, like glass.
    '''
    s, selection = _prepare(selection, _self=_self)[:2]

    util.cbc(s, _self=_self)
    _self.color('atomic', '?%s & !(elem C)' % (s))

    _self.show('cartoon', 'polymer & ?' + s)
    _self.show('licorice', '(organic | inorganic) & ?' + s)
    _self.show('surface', 'polymer & ?' + s)
    _self.set('transparency', 0.6, s)
    _self.set('surface_color', 'white', selection)
    _self.set('ray_transparency_oblique', 1) # global

    _self.delete(s)


def wire(selection='*', _self=cmd):
    '''
    Cartoon by chain as a wire mesh, and ligand sticks.
    '''
    s = _prepare(selection, _self=_self)[0]

    util.cbc(s, _self=_self)
    _self.color('atomic', '?%s & !(elem C)' % (s))

    _self.show('cartoon', 'polymer & ?' + s)
    _self.show('licorice', '(organic | inorganic) & ?' + s)
    # global, the cartoon builder reads no other level: line strips
    # instead of triangle strips
    _self.set('cartoon_debug', 3)

    _self.delete(s)


def illustration(selection='*', _self=cmd):
    '''
    Cartoon in shades of blue inside a faint surface, and the look "flat":
    ray traced, a colored line drawing like the pictures of proteinbase.
    '''
    s, selection = _prepare(selection, _self=_self)[:2]

    util.shades('marine', 'polymer & ?' + s, _self=_self)

    _self.show('cartoon', 'polymer & ?' + s)
    _self.show('licorice', '(organic | inorganic) & ?' + s)
    _self.show('surface', 'polymer & ?' + s)
    _self.set('transparency', 0.85, s)
    _self.set('surface_color', 'white', selection)
    look('flat', _self=_self) # the picture is its outline

    _self.delete(s)


solvent = False  # the solvent row of the preset menu


def from_menu(name, selection='*', _self=cmd):
    '''
    A row of the preset menu: preset `name`, without the solvent unless the
    menu's "show solvent" row was used. "default" shows everything.
    '''
    if not solvent and name != 'default':
        _self.hide('everything', '(%s) & solvent' % (selection))
        selection = '(%s) & !solvent' % (selection)
    globals()[name](selection, _self=_self)


def show_solvent(show, selection='*', _self=cmd):
    '''
    The solvent row of the preset menu: show or hide the solvent now, and
    keep it that way in the presets picked from the menu afterwards.
    '''
    global solvent
    solvent = bool(show)
    if solvent:
        _self.show('licorice', '(%s) & solvent' % (selection))
    else:
        _self.hide('everything', '(%s) & solvent' % (selection))


# Looks: light and outline of the whole scene (global settings). They are
# the last group of the preset menu. The outline is drawn in ray-traced
# images only; its color is the default "front", which contrasts with the
# background, so a look works on any background and sets none.
_outline = dict(depth_cue=0, ray_trace_mode=1, antialias=2)
LOOKS = {
    'default': {},
    # matte, the Rubber light of the Lighting plugin
    'figure': dict(_outline, ambient=0.05, direct=0.2, reflect=0.5,
                   shininess=10, power=1.67),
    # light from eight sides and soft shadows, after ChimeraX "lighting soft"
    'soft': dict(_outline, light_count=8, ambient=0.35, direct=0, reflect=0.9,
                 spec_count=1, shininess=10, specular=0.1,
                 ray_shadow_decay_factor=0.1, ray_shadow_decay_range=2),
    # unshaded colors as they are; outlines also around transparent things
    'flat': dict(_outline, ambient=1, direct=0, reflect=0, specular=0,
                 ray_shadow=0, ray_trace_trans_cutoff=1),
    # bright colors in four steps inside thick outlines, like a comic
    'comic': dict(_outline, ray_trace_mode=3, antialias=1, ambient=0.5,
                  direct=0.6, reflect=0.3, specular=0, ray_shadow=0),
    # black outlines on white and nothing else, a line drawing
    'sketch': dict(_outline, ray_trace_mode=2),
    # the X-Ray light of the Lighting plugin
    'x-ray': dict(ambient=1, direct=-0.6, reflect=-0.6, shininess=0,
                  specular=0),
}


def look(name, _self=cmd):
    '''
    Give the whole scene the light and outline of LOOKS[name]. The
    background stays as it is.
    '''
    for key in {key for settings in LOOKS.values() for key in settings}:
        _self.unset(key)
    for key, value in LOOKS[name].items():
        _self.set(key, value)
