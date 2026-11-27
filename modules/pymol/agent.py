"""Live discovery and reviewed API execution, shared by chat and local agents."""

import ast
import base64
import contextlib
import importlib.util
import inspect
import io
import json
import math
import shutil
import threading
from pathlib import Path

from pymol import CmdException, api, cmd, fetching, palettes, preset, snapshots, util


# Execution is deliberately narrower than discovery. Capture the native API
# functions, then reject registry overrides; never feed model text to cmd.do.
QUERIES = set("count_atoms count_states get_names get_object_list get_type get_state get_view get_distance get_angle get_dihedral get_color_tuple get_atom_coords get_setting_tuple get_setting_int get_setting_float get get_names_of_type list_uniprot_structures".split())
QUERIES |= set("count_discrete count_frames get_chains get_extent get_symmetry get_title get_phipsi get_fastastr get_color_index get_color_indices get_object_matrix get_object_color_index get_position get_movie_length get_frame get_scene_list get_scene_message get_renderer get_version get_viewport get_clip get_unused_name get_legal_name get_object_state get_selection_state get_object_settings get_setting_boolean get_setting_text get_assembly_ids get_property get_property_list get_bond get_volume_histogram get_area centerofmass find_pairs overlap identify index id_atom intra_rms intra_rms_cur rms_cur get_raw_alignment".split())
VISUAL = set("show hide show_as color color_cpk palette bg_color zoom orient center turn clip enable disable frame select scene cartoon set_color ligand_next stage ligand_2d set unset".split())
VISUAL |= set("distance angle dihedral pi_interactions toggle origin reset move rock view set_view group ungroup order group_enable group_disable group_next group_previous sort_group cluster_ligands spectrum color_deep color_plddt set_object_color color_group_with_gradient recolor rebuild label deselect indicate set_bond unset_bond set_frame forward backward rewind ending middle mplay mstop mtoggle mset mview mclear isomesh isosurface isodot isolevel gradient volume volume_color slice_new ramp_new ramp_update pseudoatom search_sequence edit unpick mask unmask protect deprotect scene_order set_title".split())
CONFIRM = set("delete remove set_name create copy align super cealign dss load save load_table save_table fetch sequence_align load_smiles fix_structure minimize fetch_by_uniprot fetch_uniprot_ligands fetch_fold".split())
# changes of the structure, new molecules, files
CONFIRM |= set("h_add h_fill h_fix remove_picked bond unbond valence fuse attach replace invert torsion set_dihedral set_geometry cycle_valence fix_chemistry rename sort rebond set_symmetry symmetry_copy translate rotate transform_selection transform_object matrix_copy matrix_reset set_object_ttt extract fragment fab fnab symexp split_chains split_states split_types extract_chain join_states copy_group morph map_new map_double map_halve map_trim fit intra_fit usalign update smooth mse2met delete_states read_pdbstr read_molstr read_sdfstr clean assign_stereo set_property set_atom_property png multisave multifilesave export_objects load_traj load_files".split())
REVIEWED = {name: getattr(api, name) for name in QUERIES | VISUAL | CONFIRM}
PRESETS = {name: getattr(preset, name) for name in "default classified technical ball_and_stick space_filling illustrated_atoms licorice bond_shell b_factor_putty pretty_solv pub_solv glass balls_in_glass cylinders wire spring illustration ligands ligand_sites ligand_sites_hq ligand_sites_trans ligand_sites_trans_hq ligand_sites_mesh ligand_sites_dots interface interaction antibody pretty pretty_no_solv publication pub_no_solv publication_green simple simple_no_solv ligand_cartoon cartoon_style cartoon_transparency transparency depth_fog glow show_solvent".split()}
REVIEWED.update({"preset." + name: fn for name, fn in PRESETS.items()})
REVIEWED.update({"preset.look": preset.look, "preset.theme": preset.theme})
REVIEWED.update({"util." + name: getattr(util, name) for name in "cbc cbag cbac cbam cbak cbao cbap cbas cbaw cbay cbab cnc chainbow rainbow".split()})
# arguments that go into an expression the command runs as Python, or that
# turn a query into a change
REFUSED = {"get_fastastr": "key", "assign_stereo": "prop", "get_area": "load_b", "rms_cur": "object"}
FORMATS = ("pdb", "cif", "mmcif", "sdf", "mol")  # read without running anything
LABEL = (ast.Expression, ast.Constant, ast.Name, ast.Load, ast.BinOp, ast.Add, ast.Mod, ast.Tuple, ast.JoinedStr, ast.FormattedValue)
OPTIONAL = {"load_smiles": ["rdkit"], "clean": ["rdkit"], "ligand_2d": ["rdkit"], "fix_structure": ["pdbfixer", "openmm"], "minimize": ["openmm"], "sequence_align": ["MAFFT"]}
VISUAL_SETTINGS = ("ball_and_stick_", "sphere_", "stick_", "cartoon_", "ribbon_", "surface_", "line_", "mesh_", "dot_", "dash_", "label_", "light", "ambient", "ray_", "fog", "bg_rgb")
OTHER_VISUAL_SETTINGS = set("transparency orthoscopic depth_cue antialias direct reflect specular shininess power two_sided_lighting opaque_background valence seq_view".split())
LOCK = threading.RLock()


def _functions(_self):
    functions = {name: fn for name, fn in vars(api).items() if not name.startswith("_") and inspect.isroutine(fn)}
    functions.update({name: entry[0] for name, entry in _self.keyword.items() if not name.startswith("_")})
    functions.update({"preset." + name: fn for name, fn in vars(preset).items() if not name.startswith("_") and inspect.isfunction(fn) and fn.__module__ == preset.__name__})
    return functions


def _signature(function):
    try:
        signature = inspect.signature(function)
        return signature.replace(parameters=[p for p in signature.parameters.values() if not p.name.startswith("_")])
    except (TypeError, ValueError):
        return None


def capabilities(_self=cmd):
    return {
        "version": _self.get_version()[0],
        "commands": len(_functions(_self)),
        "optional": {name: bool(shutil.which("mafft") or shutil.which("mafft.bat")) if name == "MAFFT" else importlib.util.find_spec(name) is not None for name in {p for packages in OPTIONAL.values() for p in packages} | {"openai", "anthropic"}},
        "execution": "Reviewed API calls; file/network/destructive actions and Python require confirmation, unless the user has ticked 'Run without asking' in the Chat tab. A UniProt download of more than ten entries runs in the background. Python is separately trusted. Discovery is not permission.",
    }


def discover(query="", offset=0, limit=40, *, _self=cmd):
    functions = _functions(_self)
    names = sorted(n for n in functions if query.lower() in n.lower())
    offset, limit = max(0, int(offset)), min(100, max(1, int(limit)))
    return {"total": len(names), "offset": offset, "commands": [
        {"name": name, "signature": str(_signature(functions[name])), "origin": getattr(functions[name], "__module__", "registered command"), "policy": "reviewed" if functions[name] is REVIEWED.get(name) else "discoverable only", "requires": OPTIONAL.get(name, [])}
        for name in names[offset:offset + limit]
    ]}


def help_command(name, *, _self=cmd):
    function = _functions(_self).get(name)
    if function is None:
        raise CmdException("Unknown command; use discover to find installed names")
    signature = _signature(function)
    return {"name": name, "signature": str(signature) if signature else None,
            "syntax": "Python API keyword arguments via execute; command-line usage is in the documentation",
            "documentation": (inspect.getdoc(function) or "No documentation supplied.")[:16000],
            "requires": OPTIONAL.get(name, []),
            "policy": "reviewed" if function is REVIEWED.get(name) else "discoverable only"}


def settings(query="", offset=0, limit=40, *, _self=cmd):
    from . import _cmd

    names = sorted(n for n in _self.setting.get_name_list() if query.lower() in n.lower())
    offset, limit = max(0, int(offset)), min(100, max(1, int(limit)))
    records = []
    types = {1: "boolean", 2: "integer", 3: "float", 4: "vector", 5: "color", 6: "string"}
    for name in names[offset:offset + limit]:
        index = _self.setting._get_index(name)
        kind, value = _self.get_setting_tuple(name)
        records.append({"name": name, "type": types.get(kind, "unknown"), "level": _cmd.get_setting_level(index), "current": value[0] if len(value) == 1 else value, "factory_default": _cmd.get_setting_default(index)})
    return {"total": len(names), "settings": records, "looks": list(preset.LOOKS), "themes": list(preset.THEMES), "palettes": ["default", *palettes.PALETTES], "representations": list(_self.repres), "presets": discover("preset.", _self=_self)["commands"]}


def scene_state(*, _self=cmd):
    from . import ligand_nav

    names = _self.get_names("public_objects")
    return {"objects": [{"name": n, "type": _self.get_type(n)} for n in names[:200]],
            "object_count": len(names), "enabled": _self.get_names("public_objects", enabled_only=1)[:200],
            "selections": _self.get_names("selections")[:200], "atoms": _self.count_atoms(),
            "selected_atoms": _self.count_atoms("?sele"), "state": _self.get_state(),
            "scenes": _self.get_scene_list()[:200], "current_scene": _self.get("scene_current_name"),
            "ligand": ligand_nav.current(), "visible_representations": {r: _self.count_atoms("enabled and rep " + r) for r in _self.repres if r != "everything"}}


def atoms(selection="sele", limit=100, *, _self=cmd):
    records = []
    limit = min(200, max(1, int(limit)))
    _self.iterate_state(-1, selection,
        "records.append(dict(object=model, chain=chain, segment=segi, residue=resi, residue_name=resn, atom=name, element=elem, b=b, occupancy=q, ss=ss, x=x, y=y, z=z)) if len(records) < limit else None",
        space={"records": records, "limit": limit})
    return {"atoms": records, "limit": limit, "total": _self.count_atoms(selection)}


def _validate(value, depth=0):
    if depth > 5:
        raise CmdException("Arguments are nested too deeply")
    if isinstance(value, str):
        if len(value) > 16000 or any(ord(c) < 32 and c not in "\n\t" for c in value):
            raise CmdException("Invalid or oversized text argument")
    elif isinstance(value, (list, dict)):
        if len(value) > 200:
            raise CmdException("Too many arguments")
        for item in (value.values() if isinstance(value, dict) else value):
            _validate(item, depth + 1)
        if isinstance(value, dict) and any(not isinstance(k, str) or k.startswith("_") for k in value):
            raise CmdException("Private or non-string argument names are not accepted")
    elif value is not None and not isinstance(value, (int, float, bool)):
        raise CmdException("Only JSON arguments are accepted")
    elif isinstance(value, float) and not math.isfinite(value):
        raise CmdException("Numbers must be finite")


def _policy(name, arguments, _self):
    if arguments.get(REFUSED.get(name)):
        raise CmdException(f"The argument '{REFUSED[name]}' of {name} is not reviewed")
    if name in ("set", "unset", "set_bond", "unset_bond"):
        setting = arguments.get("name", "")
        if setting not in _self.setting.get_name_list() or not (setting.startswith(VISUAL_SETTINGS) or setting in OTHER_VISUAL_SETTINGS):
            raise CmdException("This setting is discoverable but is not a reviewed visual setting")
        kind = _self.get_setting_tuple(setting)[0]
        if kind == 6:
            raise CmdException("String settings can name files or programs and are not reviewed")
        if name in ("set", "set_bond") and kind == 4:
            value = arguments.get("value")
            if not isinstance(value, list) or len(value) != 3 or not all(isinstance(x, (float, int)) for x in value):
                raise CmdException("A vector setting requires three JSON numbers")
    if name == "load":
        filename = arguments.get("filename", "")
        suffix = Path(filename.split("?", 1)[0]).suffix.lower().lstrip(".")
        if suffix == "gz":
            suffix = Path(filename[:-3]).suffix.lower().lstrip(".")
        format = arguments.get("format") or suffix
        if format not in FORMATS:
            raise CmdException("Reviewed load accepts PDB/mmCIF/SDF/MOL only. Sessions and scripts can execute Python; use separately trusted Python after reviewing the file.")
        arguments["format"] = format
    if name in ("fetch", "fetch_fold"):
        arguments["async_"] = 0  # completion, errors and Undo belong to this turn
    if name == "fetch":
        if not isinstance(arguments.get("code"), str) or len(arguments["code"].split()) > 10:
            raise CmdException("Fetch at most ten identifiers per action")
    if name == "load_files" and str(arguments.get("format", "pdb")).lower().lstrip(".") not in FORMATS:
        raise CmdException("Reviewed load_files accepts PDB/mmCIF/SDF/MOL only")
    if name == "png" and not arguments.get("filename"):
        raise CmdException("png needs a file name; use look to see the viewport")
    # the next three reach Python inside the command: a label and the property
    # of a spectrum are expressions, a fragment is a file name, and fab puts
    # chain and segi into an expression
    if name == "label" and arguments.get("expression"):
        try:
            nodes = list(ast.walk(ast.parse(str(arguments["expression"]).strip(), mode="eval")))
        except SyntaxError:
            nodes = [None]
        if not all(isinstance(node, LABEL) for node in nodes):
            raise CmdException("A reviewed label is made of atom properties, text, + and %, for example '%s%s' % (resn, resi)")
    if name == "spectrum" and not str(arguments.get("expression", "count")).replace("_", "").isalpha():
        raise CmdException("A reviewed spectrum takes one atom property, for example b")
    if name in ("fragment", "fab"):
        arguments.pop("async_", None)
        texts = [str(arguments[key]) for key in ("name", "input", "chain", "segi") if arguments.get(key)]
        if not all(text.replace("_", "").isalnum() for text in texts):
            raise CmdException("Letters, digits and _ only in the name, the sequence, chain and segi")
    if "accession" in arguments:  # the three UniProt commands
        if not fetching._ACCESSION.fullmatch(str(arguments["accession"]).strip().upper()):
            raise CmdException("Not a UniProt accession; an example is P00533")
        if name == "list_uniprot_structures":
            arguments.setdefault("quiet", 0)  # the table: method, resolution, chains
        else:
            # more than ten entries would block the window: they load in the background
            arguments["async_"] = int(not 0 < int(arguments.get("limit") or 0) <= 10)
    if name == "scene" and arguments.get("action", "recall") not in ("recall", "store", "insert", "update", "clear", "rename", "delete", "next", "previous"):
        raise CmdException("Unsupported scene action")
    return (name in CONFIRM or name == "ligand_2d" and bool(arguments.get("filename"))
            or name == "scene" and arguments.get("action", "recall") != "recall")


class Executor:
    def __init__(self, _self=cmd, confirm=None, log=None):
        self.cmd = _self
        self.confirm = confirm or (lambda proposal: False)
        self.log = log or (lambda text: None)
        self.cancel = threading.Event()
        self.trusted = False
        self.images = False
        self.unasked = False  # True: nothing asks ("Run without asking")
        self.snapshot = None
        self.results = {}

    def begin_turn(self):
        self.cancel.clear()
        self.snapshot = None

    def _check(self):
        if self.cancel.is_set():
            raise CmdException("Cancelled")

    def _keep(self):
        if self.snapshot is None:
            if self.cmd.count_atoms() > snapshots.ATOMS:
                raise CmdException("This change exceeds the session Undo limit; use the normal command line")
            snapshots.keep(self.cmd)
            if not snapshots._undo:
                raise CmdException("Could not keep an Undo snapshot; nothing executed")
            self.snapshot = snapshots._undo[-1]

    def execute(self, command, arguments=None):
        arguments = dict(arguments or {})
        function = _functions(self.cmd).get(command)
        if function is None or function is not REVIEWED.get(command):
            raise CmdException("Command is not reviewed for execution; its help remains available")
        _validate(arguments)
        signature = _signature(function)
        if signature is None or any(k not in signature.parameters for k in arguments):
            raise CmdException("Use documented named arguments; private/extra arguments are refused")
        signature.bind(**arguments)
        confirmation = _policy(command, arguments, self.cmd)
        proposal = {"command": command, "arguments": arguments,
                    "effect": "File/network or destructive operation; external effects cannot be undone."}
        self._check()
        if confirmation and not self.unasked and not self.confirm(proposal):
            raise CmdException("The user declined this action")
        self._check()
        if command not in QUERIES:
            self._keep()
        if "_self" in inspect.signature(function).parameters:
            arguments["_self"] = self.cmd
        with snapshots.paused():  # the turn's snapshot is its one step
            value = function(**arguments)
        if arguments.get("async_"):
            value = "Runs in the background; this turn does not see its result. Use state to follow it."
        # Older APIs sometimes report failure as -1 rather than raising.
        if isinstance(value, int) and not isinstance(value, bool) and value < 0:
            raise CmdException(f"{command} returned failure ({value})")
        return {"value": value, "undo_snapshot": self.snapshot is not None,
                "external_effects_undoable": False if confirmation else None}

    def call(self, call_id, operation, arguments=None):
        """Serialized, duplicate-safe tool call. Cancel is checked after lock/approval."""
        arguments = arguments or {}
        fingerprint = json.dumps([operation, arguments], sort_keys=True)
        with LOCK:
            self._check()
            if call_id in self.results:
                previous, result = self.results[call_id]
                if previous != fingerprint:
                    raise CmdException("Tool call ID was reused with different arguments")
                return result
            output = io.StringIO()
            pending = self.cmd._get_feedback()
            if pending:
                self.log("\n".join(pending))
            try:
                _validate(arguments)
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    self._check()
                    if operation == "execute":
                        value = self.execute(**arguments)
                    elif operation == "python":
                        code = arguments.get("code", "")
                        if not self.trusted or not self.unasked and not self.confirm({"python": code, "effect": "Arbitrary Python has full filesystem and network access; it is not sandboxed."}):
                            raise CmdException("Trusted Python is off or the user declined")
                        self._check()
                        self._keep()
                        with snapshots.paused():
                            exec(compile(code, "<reviewed assistant Python>", "exec"), {"cmd": self.cmd})
                        value = {"undo_snapshot": True, "external_effects_undoable": False}
                    elif operation == "look":
                        if not self.images:
                            raise CmdException("Viewport sharing is off; the user must enable it")
                        headless = bool(self.cmd._pymol.invocation.options.no_gui)
                        png = self.cmd.png(None, 640, 480, ray=int(headless), quiet=1)
                        if not isinstance(png, bytes) or not png.startswith(b"\x89PNG") or len(png) > 2_000_000:
                            raise CmdException("No bounded viewport PNG is available")
                        value = {"image": base64.b64encode(png).decode(), "mime_type": "image/png"}
                    else:
                        function = {"discover": discover, "help": help_command, "settings": settings, "state": scene_state, "atoms": atoms}.get(operation)
                        if function is None:
                            raise CmdException("Unknown operation")
                        value = function(**arguments, _self=self.cmd)
                result = {"ok": True, "result": value}
            except Exception as error:
                result = {"ok": False, "error": str(error)[:4000]}
            feedback = self.cmd._get_feedback() or []
            result["output"] = (output.getvalue() + "\n".join(feedback))[-16000:]
            if not (operation == "look" and result["ok"]):
                encoded = json.dumps(result, default=str)
                if len(encoded) > 24000:
                    result = {"ok": result["ok"], "truncated": True, "text": encoded[:24000], "hint": "Narrow the query or request fewer rows"}
            self.log(json.dumps({"operation": operation, "arguments": arguments, "result": {"image": "shared"} if operation == "look" and result["ok"] else result}, default=str))
            self.results[call_id] = fingerprint, result
            # A conversation is bounded by the caller; keep IDs across retries.
            return result
