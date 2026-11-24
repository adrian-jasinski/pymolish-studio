"""Sequence rows, FASTA and local MAFFT alignment. No Qt or chemistry dependency."""

import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

from pymol import CmdException, cmd


def read_fasta(text):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            label = line[1:].strip()
            if not label:
                raise CmdException("FASTA: a sequence needs a name")
            rows.append(
                {"label": label, "sequence": "", "source": None, "residues": []}
            )
        else:
            letters = "".join(line.split()).upper().replace(".", "-")
            if not rows or any(
                c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ-*?" for c in letters
            ):
                raise CmdException(
                    "FASTA: expected a header followed by sequence letters"
                )
            rows[-1]["sequence"] += letters
    if not rows or any(not r["sequence"].replace("-", "") for r in rows):
        raise CmdException("FASTA: no sequence letters")
    return rows


def fasta(rows):
    return "".join(
        ">"
        + r["label"].replace("\n", " ").replace("\r", " ")
        + "\n"
        + "\n".join(r["sequence"][i : i + 80] for i in range(0, len(r["sequence"]), 80))
        + "\n"
        for r in rows
    )


def structure_rows(selection="enabled", state=0, *, _self=cmd):
    """One row per object/segment/chain; residue identities outlive atom indices."""
    state = int(state) or _self.get_state()
    atoms = []
    _self.iterate_state(
        state,
        f"({selection}) and polymer and guide",
        "atoms.append((model, segi, chain, resi, resn, oneletter, ss, alt))",
        space={"atoms": atoms},
    )
    groups = {}
    seen = set()
    for model, segi, chain, resi, resn, letter, ss, alt in atoms:
        key = (model, segi, chain, resi)
        if key in seen:  # alternate conformers are one residue
            continue
        seen.add(key)
        source = (model, segi, chain, state)
        row = groups.setdefault(
            source,
            {
                "label": f"{model}/{segi}/{chain or '-'} (state {state})",
                "sequence": "",
                "source": list(source),
                "residues": [],
            },
        )
        row["sequence"] += letter if letter and letter.isalpha() else "X"
        row["residues"].append([resi, resn, ss if ss in ("H", "S", "L") else "?"])
    return list(groups.values())


def aligned_residues(row):
    residues = iter(row["residues"])
    return [next(residues, None) if c != "-" else None for c in row["sequence"]]


def validate_rows(rows):
    """Reject malformed session mappings before they reach the table model."""
    if not isinstance(rows, list):
        raise TypeError("Invalid alignment rows")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("label"), str):
            raise TypeError("Invalid alignment label")
        letters = row.get("sequence")
        if not isinstance(letters, str) or any(
            c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ-*?" for c in letters
        ):
            raise ValueError("Invalid alignment sequence")
        source, residues = row.get("source"), row.get("residues")
        if not isinstance(residues, list):
            raise TypeError("Invalid residue mapping")
        if source is None:
            if residues:
                raise ValueError("FASTA rows cannot map residues")
        elif (
            not isinstance(source, (list, tuple))
            or len(source) != 4
            or not all(isinstance(s, str) for s in source[:3])
            or not isinstance(source[3], int)
            or source[3] < 1
            or len(residues) != len(letters.replace("-", ""))
        ):
            raise ValueError("Invalid structure mapping")
        for residue in residues:
            if (
                not isinstance(residue, (list, tuple))
                or len(residue) != 3
                or not all(isinstance(s, str) for s in residue)
                or residue[2] not in ("H", "S", "L", "?")
            ):
                raise ValueError("Invalid mapped residue")


def atom_indices(row, residue_numbers, *, _self=cmd):
    """Resolve fresh indices, including all atoms in a picked residue."""
    if not row["source"]:
        return []
    model, segi, chain, state = row["source"]
    if model not in _self.get_object_list():
        return []
    wanted = {(r[0], r[1]) for r in residue_numbers}
    indices = []
    _self.iterate_state(
        state,
        "all",
        "indices.append(index) if model == obj and segi == segment and chain == ch "
        "and (resi, resn) in wanted else None",
        space={
            "indices": indices,
            "obj": model,
            "segment": segi,
            "ch": chain,
            "wanted": wanted,
        },
    )
    return indices


def select_residues(picks, add=False, *, _self=cmd):
    """picks is (row, residue list); no expression is assembled from imported labels."""
    temporary = _self.get_unused_name("_sequence_pick")
    combined = _self.get_unused_name("_sequence_selection")
    try:
        _self.select(combined, "none")
        for row, residues in picks:
            indices = atom_indices(row, residues, _self=_self)
            if indices:
                _self.select_list(temporary, row["source"][0], indices, mode="index")
                _self.select(combined, f"?{combined} or ?{temporary}")
        _self.select("sele", f"?{combined}" + (" or ?sele" if add else ""))
    finally:
        _self.delete(temporary)
        _self.delete(combined)


def align_sequences(rows, executable="", cancel=None):
    """Return aligned strings in input order; MAFFT runs locally, never in a shell."""
    if len(rows) < 2:
        raise CmdException("Choose at least two sequences")
    program = executable or shutil.which("mafft") or shutil.which("mafft.bat")
    if not program:
        raise CmdException(
            "Install MAFFT and put it on PATH, or choose its executable in the sequence window."
        )
    sequences = [r["sequence"].replace("-", "") for r in rows]
    if any(
        not s or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ*?" for c in s)
        for s in sequences
    ):
        raise CmdException("Invalid or empty sequence")
    if cancel and cancel.is_set():
        raise CmdException("Alignment cancelled")
    with tempfile.TemporaryDirectory(prefix="pymolish-align-") as directory:
        source = Path(directory, "input.fasta")
        source.write_text("".join(f">row{i}\n{s}\n" for i, s in enumerate(sequences)))
        args = [str(program), "--auto", "--inputorder", "--anysymbol", str(source)]
        if os.name == "nt" and str(program).lower().endswith((".bat", ".cmd")):
            # MAFFT's Windows distribution is a batch entry point. Its path
            # is user-chosen; all other arguments are fixed/generated here.
            if any(c in str(program) + str(source) for c in '&|<>^%\r\n"'):
                raise CmdException("MAFFT batch path contains shell metacharacters")
            args = [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", *args]
        with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
            try:
                process = subprocess.Popen(
                    args,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=errors,
                    start_new_session=os.name != "nt",
                )
            except OSError as exc:
                raise CmdException(f"Cannot start MAFFT: {exc}") from exc
            while True:
                try:
                    process.wait(timeout=0.1)
                    break
                except subprocess.TimeoutExpired:
                    if cancel and cancel.is_set():
                        if os.name == "nt":
                            subprocess.run(
                                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                check=False,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                        else:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                        process.wait()
                        raise CmdException("Alignment cancelled")
            if cancel and cancel.is_set():
                raise CmdException("Alignment cancelled")
            errors.seek(0)
            if process.returncode:
                raise CmdException(
                    "MAFFT failed: " + errors.read()[-4000:].decode(errors="replace")
                )
            output.seek(0)
            result = read_fasta(output.read().decode())
    by_name = {r["label"]: r["sequence"] for r in result}
    if len(result) != len(rows) or set(by_name) != {
        f"row{i}" for i in range(len(rows))
    }:
        raise CmdException("MAFFT returned unexpected sequence identifiers")
    aligned = [by_name[f"row{i}"] for i in range(len(rows))]
    if len({len(s) for s in aligned}) != 1 or any(
        a.replace("-", "") != b for a, b in zip(aligned, sequences)
    ):
        raise CmdException("MAFFT changed the input sequences")
    return aligned


def statistics(rows, reference=0):
    """Identity excludes gaps and X/?/*; conservation uses the same denominator."""
    from collections import Counter

    letters = [r["sequence"] for r in rows]
    if not letters:
        return "", [], []
    if len({len(s) for s in letters}) != 1:
        return "", [], []
    consensus, conservation = [], []
    for column in zip(*letters):
        counts = Counter(c for c in column if c not in "-X?*")
        best = counts.most_common(1)
        consensus.append(best[0][0] if best else "-")
        conservation.append(best[0][1] / sum(counts.values()) if best else 0)
    identities = []
    for sequence in letters:
        pairs = [
            (a, b)
            for a, b in zip(sequence, letters[reference])
            if a not in "-X?*" and b not in "-X?*"
        ]
        identities.append(sum(a == b for a, b in pairs) / len(pairs) if pairs else None)
    return "".join(consensus), conservation, identities


def fit_rows(rows, reference=0, method="align", cancel=None, *, _self=cmd):
    """Fit each mobile object to one reference; return per-object results/errors."""
    from . import snapshots

    if method not in ("align", "super", "cealign"):
        raise CmdException("Choose align, super or cealign")
    if len(rows) < 2 or any(not r["source"] for r in rows):
        raise CmdException("Structure fitting needs at least two structure rows")
    if not 0 <= reference < len(rows):
        raise CmdException("Choose a reference row")
    if cancel and cancel.is_set():
        raise CmdException("Fitting cancelled")
    objects = [r["source"][0] for r in rows]
    if len(set(objects)) != len(objects):
        raise CmdException(
            "Choose one chain/state per object; a fit moves the whole object"
        )
    if _self.count_atoms() > snapshots.ATOMS:
        raise CmdException("This fit exceeds the Undo snapshot limit")
    resolved = [atom_indices(row, row["residues"], _self=_self) for row in rows]
    if any(not indices for indices in resolved):
        raise CmdException("A structure row is no longer mapped; add its chain again")
    snapshots.keep(_self)
    target = _self.get_unused_name("_sequence_target")
    mobile = _self.get_unused_name("_sequence_mobile")
    results = []
    try:
        _self.select_list(target, objects[reference], resolved[reference], mode="index")
        for i, row in enumerate(rows):
            if i == reference:
                continue
            if cancel and cancel.is_set():
                break
            _self.select_list(mobile, objects[i], resolved[i], mode="index")
            try:
                kwargs = {
                    "mobile_state": row["source"][3],
                    "target_state": rows[reference]["source"][3],
                }
                if method == "cealign":
                    result = _self.cealign(target, mobile, **kwargs)
                    rmsd, count = result["RMSD"], result["alignment_length"]
                else:
                    result = getattr(_self, method)(mobile, target, **kwargs)
                    rmsd, count = result[:2]
                results.append({"label": row["label"], "rmsd": rmsd, "atoms": count})
            except CmdException as exc:
                results.append({"label": row["label"], "error": str(exc)})
    finally:
        _self.delete(target)
        _self.delete(mobile)
    return results


def assign_secondary(rows, cancel=None, *, _self=cmd):
    from . import snapshots

    if _self.count_atoms() > snapshots.ATOMS:
        raise CmdException("This operation exceeds the Undo snapshot limit")
    snapshots.keep(_self)
    temporary = _self.get_unused_name("_sequence_ss")
    try:
        for row in rows:
            if cancel and cancel.is_set():
                break
            if not row["source"]:
                continue
            indices = atom_indices(row, row["residues"], _self=_self)
            if not indices:
                continue
            _self.select_list(temporary, row["source"][0], indices, mode="index")
            _self.dss(temporary, state=row["source"][3])
            updated = structure_rows(temporary, row["source"][3], _self=_self)
            assigned = {
                (r[0], r[1]): r[2] for record in updated for r in record["residues"]
            }
            row["residues"] = [
                [r[0], r[1], assigned.get((r[0], r[1]), "?")] for r in row["residues"]
            ]
    finally:
        _self.delete(temporary)
    return rows


def sequence_align(filename, output="", executable="", *, _self=cmd):
    """
    DESCRIPTION

        Align FASTA sequences with an optional local MAFFT installation.
        No coordinates are changed. Returns aligned FASTA and optionally writes it.

    USAGE

        sequence_align filename [, output [, executable ]]

        executable defaults to mafft on PATH (mafft.bat on Windows).
        Install MAFFT separately; it is not required to open the sequence window.
        Import and export support FASTA only. Alignment runs locally.
    """
    rows = read_fasta(Path(_self.exp_path(filename)).read_text(encoding="utf-8-sig"))
    for row, aligned in zip(rows, align_sequences(rows, executable)):
        row["sequence"] = aligned
    text = fasta(rows)
    if output:
        Path(_self.exp_path(output)).write_text(text, encoding="utf-8")
    return text
