"""
One key in a session for what pymolish adds: session["pymolish"], a
dictionary with a "version" and one entry per feature ("table": the columns
of the property table). A feature reads and writes its own entry in
`entries`. An entry this version does not know, written by a newer one, is
kept and written back untouched. PyMOL ignores the key.
"""

import copy

VERSION = 1
entries = {}


def session_save(session, _self=None):
    if any(key != "version" for key in entries):
        kept = copy.deepcopy(entries)
        kept["version"] = max(VERSION, kept.get("version", 0))
        session["pymolish"] = kept
    return 1


def session_restore(session, _self=None):
    data = session.get("pymolish") if session else None
    entries.clear()
    if isinstance(data, dict):
        entries.update(data)
    return 1
