"""
Tables of object properties in and out: "load_table" reads a CSV, TSV or
Excel file and sets the properties of the objects its rows name;
"save_table" writes the properties of the objects as CSV. The property
table of the window (pmg_qt/property_table.py) shows the same properties.
"""

import csv
import io
import os
import re
import zipfile
from xml.etree import ElementTree

import pymol

cmd = __import__("sys").modules["pymol.cmd"]

# headers that say which column names the objects
NAME_HEADERS = ("name", "title", "object", "id", "entry")
_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_xlsx(filename):
    """The first sheet of an Excel file as rows of text. An .xlsx is a zip
    of XML: no package is needed for values.

    shortcut: the first sheet only, a formula gives its stored result, a
    date arrives as Excel's day number, the old binary .xls is not read.
    For those: openpyxl as an optional dependency."""
    with zipfile.ZipFile(filename) as book:
        strings = []
        if "xl/sharedStrings.xml" in book.namelist():
            root = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
            for item in root.iter(_NS + "si"):
                strings.append("".join(t.text or "" for t in item.iter(_NS + "t")))
        sheets = sorted(
            (n for n in book.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
            key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()),
        )
        if not sheets:
            raise pymol.CmdException("no sheet in '%s'" % filename)
        root = ElementTree.fromstring(book.read(sheets[0]))
    rows = []
    for row in root.iter(_NS + "row"):
        cells = []
        for cell in row.iter(_NS + "c"):
            # "C7" is column 2: empty cells are left out of the file
            letters = re.match(r"[A-Z]+", cell.get("r", "")) or None
            column = len(cells)
            if letters:
                column = 0
                for letter in letters.group():
                    column = column * 26 + ord(letter) - 64
                column -= 1
            kind = cell.get("t")
            if kind == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(_NS + "t"))
            else:
                value = cell.find(_NS + "v")
                text = value.text or "" if value is not None else ""
                if kind == "s":
                    text = strings[int(text)]
                elif kind == "b":
                    text = "true" if text == "1" else "false"
            cells += [""] * (column - len(cells)) + [text]
        rows.append(cells)
    return rows


def read_table(filename):
    """Rows of text from a .csv, .tsv, .txt or .xlsx file."""
    if filename.lower().endswith((".xlsx", ".xlsm")):
        return read_xlsx(filename)
    if filename.lower().endswith(".xls"):
        raise pymol.CmdException(
            "the old Excel format .xls is not read: save as .xlsx or .csv"
        )
    with open(filename, newline="", encoding="utf-8-sig") as handle:
        text = handle.read()
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
    except csv.Error:  # one column, or nothing to go by
        dialect = csv.excel_tab if filename.lower().endswith(".tsv") else csv.excel
    return list(csv.reader(io.StringIO(text), dialect))


def load_table(filename, object_column="", quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "load_table" reads a table and sets object properties from it: one
        row per object, one column per property. A row goes to the object
        whose name is in the name column; rows that name no object are
        skipped. A header that is no property yet becomes a new one. An
        empty cell leaves the property as it is.

    USAGE

        load_table filename [, object_column ]

    ARGUMENTS

        filename = str: a .csv, .tsv or .xlsx file (first sheet)

        object_column = str: header of the column with the object names
        {default: the first of name, title, object, id, entry; else the
        first column}

    EXAMPLE

        load_table scores.csv
        load_table results.xlsx, object_column=Ligand

    SEE ALSO

        save_table, set_property
    """
    quiet = int(quiet)
    rows = [r for r in read_table(_self.exp_path(filename)) if any(c.strip() for c in r)]
    if not rows:
        raise pymol.CmdException("'%s' has no rows" % filename)
    header = [h.strip() for h in rows[0]]
    lower = [h.lower() for h in header]
    if object_column:
        if object_column.lower() not in lower:
            raise pymol.CmdException("no column '%s' in '%s'" % (object_column, filename))
        key = lower.index(object_column.lower())
    else:
        key = next((lower.index(h) for h in NAME_HEADERS if h in lower), 0)
    names = set(_self.get_names("objects"))
    known = {p for n in names for p in _self.get_property_list(n) or ()}
    matched, skipped = 0, []
    for row in rows[1:]:
        name = row[key].strip() if key < len(row) else ""
        if name not in names:
            skipped.append(name)
            continue
        matched += 1
        for column, value in enumerate(row):
            if column != key and column < len(header) and header[column] and value.strip():
                _self.set_property(header[column], value.strip(), name)
    added = [h for i, h in enumerate(header) if h and i != key and h not in known]
    if not quiet:
        print(" load_table: %d rows matched an object, %d skipped%s; %d new columns%s" % (
            matched,
            len(skipped),
            " (%s%s)" % (", ".join(skipped[:5]), ", ..." if len(skipped) > 5 else "") if skipped else "",
            len(added),
            " (%s)" % ", ".join(added) if added else "",
        ))
    return matched, skipped, added


def save_table(filename, selection="all", quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "save_table" writes the properties of objects as a CSV file: a
        column "name", then one column per property.

    USAGE

        save_table filename [, selection ]

    SEE ALSO

        load_table
    """
    names = [n for n in _self.get_object_list(selection)]
    props = {n: {p: _self.get_property(p, n) for p in _self.get_property_list(n) or ()} for n in names}
    columns = []
    for name in names:
        columns += [p for p in props[name] if p not in columns]
    with open(_self.exp_path(filename), "w", newline="", encoding="utf-8") as handle:
        out = csv.writer(handle)
        out.writerow(["name", *columns])
        for name in names:
            out.writerow([name, *("" if props[name].get(c) is None else props[name][c] for c in columns)])
    if not int(quiet):
        print(" save_table: %d rows, %d columns to '%s'" % (len(names), len(columns) + 1, filename))
