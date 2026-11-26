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
        # expressions inside reviewed commands
        ("label", {"selection": "all", "expression": "__import__('os').getcwd()"}),
        ("label", {"selection": "all", "expression": "resn.__class__"}),
        ("spectrum", {"expression": "b or exit()"}),
        ("get_fastastr", {"key": "exit()"}),
        ("assign_stereo", {"prop": "b = exit(); stereo"}),
        ("fab", {"input": "AA", "chain": '"""+exit()+"""'}),
        ("fragment", {"name": "../../x"}),  # a pickle is read from that path
        ("load_files", {"directory": ".", "format": "pse"}),
        ("set_bond", {"name": "fetch_path", "value": "/tmp", "selection1": "all"}),
        ("png", {"filename": ""}),  # the image itself would be the result
        ("get_area", {"load_b": 1}),  # a query that would write B-factors
        # run other commands or Python by name
        ("preset.from_menu", {"name": "exec"}),
        ("extra_fit", {"method": "do"}),
        ("copy_to", {"name": "x", "selection": "all", "rename": "exit()"}),
        ("mdo", {"frame": 1, "command": "quit"}),
        ("system", {"command": "true"}),
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

    for name in "fetch fetch_by_uniprot fetch_uniprot_ligands fetch_fold list_uniprot_structures".split():
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
    executor.unasked = True
    started = run("4", "fetch_by_uniprot", accession="P00533", group="egfr")
    assert "background" in started["result"]["value"] and len(asked) == 1
    assert background[0][:4] == (fetching.fetch_by_uniprot, "P00533", 0, "egfr")


def test_run_without_asking(executor):
    asked = []
    executor.confirm = lambda proposal: asked.append(proposal) or False
    executor.unasked = True

    def python(call_id):
        return executor.call(call_id, "python", {"code": "cmd.delete('all')"})

    # Python stays off without "Trusted Python"
    assert not python("1")["ok"] and cmd.get_names() == ["ala"]
    call = {"command": "set_name", "arguments": {"old_name": "ala", "new_name": "gly"}}
    assert executor.call("2", "execute", call)["ok"] and cmd.get_names() == ["gly"]
    executor.trusted = True
    assert python("3")["ok"] and not cmd.get_names() and not asked
    # switched off again: the question is back
    executor.unasked = False
    assert not python("4")["ok"] and len(asked) == 1


def test_more_reviewed_commands(executor):
    asked = []
    executor.confirm = lambda proposal: asked.append(proposal["command"]) or True

    def run(command, **arguments):
        call = {"command": command, "arguments": arguments}
        result = executor.call(str(len(executor.results)), "execute", call)
        assert result["ok"], result
        return result["result"]["value"]

    # queries and changes of the view ask nothing
    assert run("get_chains", selection="all") == [""]
    assert run("get_fastastr", selection="all").splitlines()[1] == "A"
    run("label", selection="name CA", expression="'%s-%s' % (resn, resi)")
    labels = []
    cmd.iterate("name CA", "labels.append(label)", space={"labels": labels})
    assert labels == ["ALA-2"]
    run("label", selection="all", expression="")
    run("distance", name="d", selection1="name N", selection2="name O")
    run("spectrum", expression="b", palette="blue_red", selection="all")
    run("util.cbag", selection="all")
    run("preset.pretty", selection="all")
    run("set_bond", name="stick_radius", value=0.3, selection1="all")
    assert "d" in cmd.get_names() and not asked
    # changes of the structure and new molecules ask
    run("fab", input="AG", name="pep", chain="B")
    run("fragment", name="gly", object="frag")
    run("h_add", selection="frag")
    assert asked == ["fab", "fragment", "h_add"]
    assert cmd.get_chains("pep") == ["B"] and cmd.count_atoms("frag and hydro")
