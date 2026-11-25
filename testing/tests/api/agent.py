"""Live discovery and reviewed execution shared by the chat (31a)."""

import pytest

from pymol import CmdException, agent, cmd, snapshots


@pytest.fixture
def executor():
    snapshots._undo.clear()
    cmd.fragment("ala")
    return agent.Executor(cmd)


def test_catalog_is_live():
    names, total = set(), agent.discover()["total"]
    for offset in range(0, total, 100):
        names |= {c["name"] for c in agent.discover("", offset, 100)["commands"]}
    # every registered public keyword, including fork commands and plugins
    assert {k for k in cmd.keyword if not k.startswith("_")} <= names
    assert {
        "ligand_2d",
        "ligand_next",
        "stage",
        "ask",
        "preset.ball_and_stick",
    } <= names
    cmd.extend("agent_test_command", lambda: None)
    try:
        found = agent.discover("agent_test_command")["commands"]
        assert found and found[0]["policy"] == "discoverable only"
        assert agent.help_command("agent_test_command")["documentation"] == (
            "No documentation supplied."
        )
    finally:
        cmd.keyword.pop("agent_test_command")
    with pytest.raises(CmdException):
        agent.help_command("no_such_command")


@pytest.mark.usefixtures("executor")
def test_settings_and_state():
    record = agent.settings("ball_and_stick_color")["settings"][0]
    assert record["name"] == "ball_and_stick_color" and record["level"] == "atom"
    records = agent.settings("transparency", limit=100)["settings"]
    assert {"name": "transparency", "factory_default": 0.0}.items() <= next(
        r for r in records if r["name"] == "transparency"
    ).items()
    state = agent.scene_state()
    assert state["objects"] == [{"name": "ala", "type": "object:molecule"}]
    assert agent.atoms("all", 3)["total"] == 10
    assert len(agent.atoms("all", 3)["atoms"]) == 3
    assert "rdkit" in agent.capabilities()["optional"]


@pytest.mark.parametrize(
    "command, arguments",
    [
        ("do", {"commands": "quit"}),  # command separators / aliases
        ("iterate", {"selection": "all", "expression": "x"}),  # expressions
        ("run", {"filename": "x.py"}),  # scripts
        ("color", {"color": "red", "_self": None}),  # private argument
        ("set", {"name": "fetch_path", "value": "/tmp"}),  # file setting
        ("load", {"filename": "evil.pse"}),  # unpickling a session
    ],
)
def test_policy_refuses(executor, command, arguments):
    result = executor.call(
        command, "execute", {"command": command, "arguments": arguments}
    )
    assert not result["ok"]


def test_untrusted_plugin_override(executor):
    original = cmd.keyword["color"]
    cmd.keyword["color"] = [lambda **_: None] + original[1:]
    try:
        result = executor.call(
            "1", "execute", {"command": "color", "arguments": {"color": "red"}}
        )
        assert not result["ok"]
    finally:
        cmd.keyword["color"] = original


def test_execute_matches_real_command(executor):
    result = executor.call(
        "1",
        "execute",
        {"command": "color", "arguments": {"color": "red", "selection": "all"}},
    )
    assert result["ok"] and result["result"]["undo_snapshot"]
    colors = set()
    cmd.iterate("all", "colors.add(color)", space={"colors": colors})
    assert colors == {cmd.get_color_index("red")}
    # same ID and arguments: replayed, not executed twice
    assert (
        executor.call(
            "1",
            "execute",
            {"command": "color", "arguments": {"color": "red", "selection": "all"}},
        )
        is result
    )
    with pytest.raises(CmdException, match="reused"):
        executor.call("1", "state", {})
    assert len(snapshots._undo) == 1


def test_confirmation_and_cancel(executor):
    asked = []
    executor.confirm = lambda proposal: asked.append(proposal) or False
    result = executor.call(
        "1", "execute", {"command": "delete", "arguments": {"name": "all"}}
    )
    assert not result["ok"] and asked and cmd.get_names() == ["ala"]
    executor.cancel.set()
    with pytest.raises(CmdException):
        executor.call("3", "state", {})
    executor.begin_turn()
    assert executor.call("4", "state", {})["ok"]


def test_python_and_look_are_off(executor):
    assert not executor.call("1", "python", {"code": "cmd.delete('all')"})["ok"]
    assert not executor.call("2", "look", {})["ok"]
    assert cmd.get_names() == ["ala"]


def test_uniprot_downloads(executor, monkeypatch):
    from pymol import fetching

    rows = [(code, "X-ray", "2.00 A", "A=1-9") for code in ("1TUP", "2OCJ")]
    monkeypatch.setattr(fetching, "pdb_entries", lambda accession: rows)
    monkeypatch.setattr(cmd, "fetch", lambda code, name, **_: cmd.fragment("gly", name))
    background = []
    monkeypatch.setattr(cmd, "async_", lambda *a, **k: background.append(a))
    asked = []
    executor.confirm = lambda proposal: asked.append(proposal) or True

    def run(call_id, command, **arguments):
        call = {"command": command, "arguments": arguments}
        return executor.call(call_id, "execute", call)

    for name in agent.DOWNLOADS | {"list_uniprot_structures"}:
        assert agent.help_command(name)["policy"] == "reviewed"
    # the list asks nothing, keeps no snapshot and shows the table
    listed = run("1", "list_uniprot_structures", accession="P00533")
    assert listed["result"]["value"] == ["1TUP", "2OCJ"] and not asked
    assert "X-ray" in listed["output"] and not listed["result"]["undo_snapshot"]
    assert not run("2", "list_uniprot_structures", accession="P00533/../x")["ok"]
    # up to ten entries: one question, the result in this turn
    loaded = run("3", "fetch_by_uniprot", accession="P00533", limit=2, async_=1)
    assert loaded["result"]["value"] == ["P00533_1TUP", "P00533_2OCJ"]
    assert len(asked) == 1 and not background
    # all entries: in the background, and without a question once switched off
    executor.downloads = True
    started = run("4", "fetch_by_uniprot", accession="P00533", group="egfr")
    assert "background" in started["result"]["value"] and len(asked) == 1
    assert background[0][:4] == (fetching.fetch_by_uniprot, "P00533", 0, "egfr")
    # the switch is for downloads only
    assert run("5", "delete", name="none")["ok"] and len(asked) == 2
