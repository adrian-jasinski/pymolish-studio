"""
README and license files (plan step 10): relative links resolve, LICENSE
still ends with the upstream notice, and the PyMOL(TM) slogans are used the
way LICENSE allows. The user documentation (plan step 38): anchors resolve,
every guide leads back to the docs home, and every command has an entry.
"""

import hashlib
import os
import re

from pymol import testing

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DOCS = ["README.md", "CONTRIBUTING.md"] + sorted(
    "docs/" + name
    for name in os.listdir(os.path.join(ROOT, "docs"))
    if name.endswith(".md")
)
DOCS.append("docs/media/README.md")
# every place that shows a slogan to users
SLOGAN_FILES = DOCS + ["pyproject.toml", ".github/workflows/build.yml"]
SLOGANS = (
    "Includes PyMOL(TM).",
    "Based on PyMOL(TM) technology.",
    "Contains PyMOL(TM) source code.",
    "Built using PyMOL(TM).",
)
FOOTNOTE = "PyMOL is a trademark of Schrodinger, LLC."
UPSTREAM_LENGTH = 2268
UPSTREAM_SHA256 = "a1fd32ff4f11d3b7eedd8dd4ecfcec1bd65374e16ee8a823899dc3c2be13d85e"


def read(name):
    # text mode: a Windows checkout may have CRLF line ends
    with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
        return handle.read()


def test_links():
    for name in DOCS:
        targets = re.findall(r"\]\(([^)#\s]+)", read(name))
        targets += re.findall(r'src="([^"]+)"', read(name))
        for target in targets:
            if "://" in target:
                continue
            path = os.path.join(ROOT, os.path.dirname(name), target)
            assert os.path.exists(path), "%s: %s" % (name, target)


def anchors(name):
    """The anchors GitHub gives the headings of a Markdown file."""
    found = set()
    for heading in re.findall(r"^#+ +(.+?) *$", read(name), re.M):
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading).lower()
        found.add(re.sub(r"[^\w\- ]", "", text).replace(" ", "-"))
    return found


def test_anchors():
    for name in DOCS:
        for target, anchor in re.findall(r"\]\(([^)#\s]*)#([^)\s]+)\)", read(name)):
            if "://" in target or target.endswith("ChangeLog"):
                continue
            other = os.path.normpath(
                os.path.join(os.path.dirname(name), target or os.path.basename(name))
            )
            if other.endswith(".md"):
                assert anchor in anchors(other.replace(os.sep, "/")), "%s: %s#%s" % (
                    name,
                    target,
                    anchor,
                )


def test_docs_home_reaches_every_page():
    home = read("docs/README.md")
    plans = ("baseline.md",)  # a measurement record, linked from benchmark.md
    for name in DOCS:
        page = os.path.basename(name)
        if name.startswith("docs/") and name.count("/") == 1 and page != "README.md":
            assert "(%s" % page in home or page in plans, name
            if "Docs home](README.md)" not in read(name):
                # older project pages: no way back is required of them
                assert page in (
                    "install.md",
                    "plugins.md",
                    "licenses.md",
                    "benchmark.md",
                    "baseline.md",
                ), name


def test_every_command_is_indexed():
    from pymol import cmd

    indexed = set(re.findall(r"`([\w.]+)`", read("docs/commands.md")))
    # commands of the program: other tests register their own in passing
    own = {
        name
        for name, entry in cmd.keyword.items()
        if (getattr(entry[0], "__module__", None) or "").split(".")[0] == "pymol"
        and not (entry[0].__module__ or "").startswith("pymol.plugins.startup")
    }
    missing = sorted(own - indexed - {"run_testfiles"})  # of the test runner
    assert len(own) > 300
    assert not missing, "docs/commands.md lacks: %s" % ", ".join(missing)


def test_upstream_notice():
    tail = read("LICENSE")[-UPSTREAM_LENGTH:]
    assert hashlib.sha256(tail.encode()).hexdigest() == UPSTREAM_SHA256
    assert "MIT License" in read("LICENSE-MIT")
    # the icon and logo are outside both code licenses and say so
    assert "NOT under the MIT license" in read("data/pymol/icons/LICENSE")


def test_slogans():
    for name in SLOGAN_FILES:
        text = read(name)
        assert not re.search(r"(?i)pymolish(-studio)?\(TM\)", text), name
        if "PyMOL(TM)" in text:
            assert FOOTNOTE in text, name
        for slogan in SLOGANS:
            if slogan in text:
                assert text.count(slogan) == text.count("pymolish-studio. " + slogan), (
                    name
                )
    assert read("README.md").rstrip().endswith(FOOTNOTE)
