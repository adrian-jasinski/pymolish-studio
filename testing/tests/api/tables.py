"""
load_table and save_table: CSV in and out, which column names the objects,
matched and skipped rows, new columns, empty cells, other delimiters, an
Excel file made by hand.
"""

import zipfile

import pytest

from pymol import CmdException, cmd, tables


def _objects():
    for name in ("lig_a", "lig_b", "lig_c"):
        cmd.fragment("gly", name)
    cmd.set_property("score", -1.0, "lig_a")
    cmd.set_property("note", "keep", "lig_a")


def test_csv(tmp_path):
    _objects()
    path = str(tmp_path / "in.csv")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("Title,score,note,rank\nlig_a,-6.5,,1\nlig_b,-10.25,best,2\nnobody,1,x,3\n\n")
    matched, skipped, added = cmd.load_table(path)
    assert (matched, skipped, added) == (2, ["nobody"], ["rank"])
    assert cmd.get_property("score", "lig_a") == -6.5  # overwritten, typed
    assert cmd.get_property("note", "lig_a") == "keep"  # an empty cell keeps
    assert cmd.get_property("rank", "lig_b") == 2
    assert cmd.get_property("note", "lig_b") == "best"
    assert not cmd.get_property_list("lig_c")

    out = str(tmp_path / "out.csv")
    cmd.save_table(out)
    rows = tables.read_table(out)
    assert rows[0] == ["name", "score", "note", "rank"]
    assert rows[1] == ["lig_a", "-6.5", "keep", "1"]
    assert rows[3] == ["lig_c", "", "", ""]
    # and back in, into fresh objects
    cmd.delete("*")
    _objects()
    assert cmd.load_table(out)[0] == 3
    assert cmd.get_property("score", "lig_b") == -10.25


def test_key_column_and_delimiters(tmp_path):
    _objects()
    path = str(tmp_path / "semi.csv")
    with open(path, "w", encoding="utf-8-sig") as handle:  # as Excel writes it
        handle.write("pose;Ligand;energy\n1;lig_c;-3,5\n2;lig_b;-4.5\n")
    # no header says "name": the first column would be taken
    assert cmd.load_table(path)[0] == 0
    matched, skipped, added = cmd.load_table(path, object_column="ligand")
    assert matched == 2 and added == ["pose", "energy"]
    assert cmd.get_property("energy", "lig_b") == -4.5
    assert cmd.get_property("energy", "lig_c") == "-3,5"  # a decimal comma stays text
    with pytest.raises(CmdException):
        cmd.load_table(path, object_column="nothing")
    tab = str(tmp_path / "t.tsv")
    with open(tab, "w") as handle:
        handle.write("name\tstars\nlig_a\t3\n")
    assert cmd.load_table(tab)[2] == ["stars"]
    assert cmd.get_property("stars", "lig_a") == 3
    with pytest.raises(CmdException, match="xlsx"):
        cmd.load_table(str(tmp_path / "old.xls"))


SHEET = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="inlineStr"><is><t>note</t></is></c></row>
<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>-7.25</v></c><c r="C2" t="s"><v>3</v></c></row>
<row r="3"><c r="A3" t="s"><v>4</v></c><c r="C3" t="str"><f>A3</f><v>from a formula</v></c></row>
</sheetData></worksheet>"""
STRINGS = """<?xml version="1.0" encoding="UTF-8"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<si><t>name</t></si><si><t>score</t></si><si><t>lig_a</t></si>
<si><r><t>rich </t></r><r><t>text</t></r></si><si><t>lig_b</t></si></sst>"""


def test_xlsx(tmp_path):
    _objects()
    path = str(tmp_path / "book.xlsx")
    with zipfile.ZipFile(path, "w") as book:
        book.writestr("xl/worksheets/sheet1.xml", SHEET)
        book.writestr("xl/worksheets/sheet2.xml", SHEET.replace("lig", "other"))
        book.writestr("xl/sharedStrings.xml", STRINGS)
    assert tables.read_xlsx(path) == [
        ["name", "score", "note"],
        ["lig_a", "-7.25", "rich text"],
        ["lig_b", "", "from a formula"],  # B3 is not in the file: a gap
    ]
    assert cmd.load_table(path)[0] == 2
    assert cmd.get_property("score", "lig_a") == -7.25
    assert cmd.get_property("note", "lig_b") == "from a formula"
