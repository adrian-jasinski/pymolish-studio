"""The agent connector (31b): MCP over loopback HTTP, the operations of
pymol.agent. Real clients are tried by hand: docs/plans/31-ai-agents.md."""

import json
import queue
import threading
import types
import urllib.error
import urllib.request

import pytest

from pymol import CmdException, agent, agent_server, cmd, snapshots

PORT = 9258  # not the default: a running pymolish may hold that one


calls = queue.Queue()  # what the server asks the "GUI thread" to run


def in_gui_thread(function):
    if threading.current_thread() is threading.main_thread():
        return function()
    done = queue.Queue()
    calls.put((function, done))
    return done.get(timeout=10)


def client(function, *args):
    """Run a client in a thread while this one, like the window's event
    loop, runs the calls of the server: a call from another thread would
    wait for ever without a main loop."""
    result = []
    thread = threading.Thread(target=lambda: result.append(function(*args)))
    thread.start()
    while thread.is_alive():
        try:
            run, done = calls.get(timeout=0.01)
        except queue.Empty:
            continue
        done.put(run())
    return result[0]


@pytest.fixture
def url(monkeypatch):
    from pymol import gui

    shown = []
    window = types.SimpleNamespace(
        chat_panel=types.SimpleNamespace(connector=agent.Executor(cmd)),
        show_agent_server=shown.append,
    )
    monkeypatch.setattr(gui, "get_qtwindow", lambda: window)
    monkeypatch.setenv(agent_server.TOKEN_VARIABLE, "test-token")
    snapshots._undo.clear()
    cmd.fragment("ala")
    monkeypatch.setattr(cmd, "_call_in_gui_thread", in_gui_thread)
    yield cmd.agent_server("on", PORT, quiet=1)
    cmd.agent_server("off", quiet=1)
    assert shown[0] and not shown[-1]  # the window was told both times


def post(url, body, token="test-token", **headers):
    request = urllib.request.Request(
        url,
        json.dumps(body).encode(),
        {"Authorization": "Bearer " + token, **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = response.read()
            return response.status, json.loads(data) if data else None
    except urllib.error.HTTPError as error:
        return error.code, None


def rpc(url, method, params=None, id=1):
    status, reply = post(
        url, {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}}
    )
    assert status == 200 and reply["id"] == id
    return reply


def call(url, operation, arguments=None):
    result = client(
        rpc,
        url,
        "tools/call",
        {
            "name": "pymol",
            "arguments": {"operation": operation, "arguments": arguments or {}},
        },
    )["result"]
    return result["isError"], json.loads(result["content"][0]["text"])


def test_off_until_on():
    assert cmd.agent_server(quiet=1) is None
    with pytest.raises(CmdException, match="Qt interface"):
        cmd.agent_server("on", PORT)
    with pytest.raises(OSError):
        post("http://127.0.0.1:%d/mcp" % PORT, {})
    with pytest.raises(CmdException):
        cmd.agent_server("maybe")


def test_refuses_strangers(url):
    ping = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
    assert post(url, ping)[0] == 200
    assert post(url, ping, token="wrong")[0] == 401
    assert post(url, ping, token="")[0] == 401
    # a web page that found the port: the browser names its origin
    assert post(url, ping, Origin="https://example.org")[0] == 403
    assert post(url, ping, Origin="http://localhost:%d" % PORT)[0] == 200
    assert post(url, ping, Host="example.org")[0] == 403  # DNS rebinding
    assert post(url.replace("/mcp", "/other"), ping)[0] == 404
    assert post(url, [ping])[0] == 400  # no batches
    try:  # refused unread: the client sees 413 or a closed connection
        assert post(url, "x" * (agent_server.MAX_BODY + 1))[0] == 413
    except urllib.error.URLError:
        pass
    with pytest.raises(urllib.error.HTTPError) as error:  # no event stream
        urllib.request.urlopen(url, timeout=10)
    assert error.value.code == 405
    # off means closed, and a second "on" on a held port says so
    cmd.agent_server("off", quiet=1)
    with pytest.raises(OSError):
        post(url, ping)


def test_handshake_and_tools(url):
    result = rpc(url, "initialize", {"protocolVersion": "2025-06-18"})["result"]
    assert result["protocolVersion"] == "2025-06-18"
    assert result["serverInfo"] == {
        "name": "pymolish",
        "version": cmd.get_version()[0],
    }
    # an unknown revision gets the newest one this server speaks
    result = rpc(url, "initialize", {"protocolVersion": "1999-01-01"})["result"]
    assert result["protocolVersion"] == agent_server.VERSIONS[0]
    assert post(url, {"jsonrpc": "2.0", "method": "notifications/initialized"}) == (
        202,
        None,
    )
    (tool,) = rpc(url, "tools/list")["result"]["tools"]
    assert tool["name"] == "pymol" and "operation" in tool["inputSchema"]["required"]
    assert rpc(url, "resources/list")["error"]["code"] == -32601
    assert rpc(url, "tools/call", {"name": "other"})["error"]["code"] == -32602


def test_calls_match_the_session(url):
    error, state = call(url, "state")
    assert not error and state["result"]["objects"][0]["name"] == "ala"
    error, found = call(url, "discover", {"query": "agent_server"})
    assert found["result"]["commands"][0]["policy"] == "discoverable only"
    # a reviewed change runs and keeps an Undo snapshot of its own
    error, done = call(
        url, "execute", {"command": "color", "arguments": {"color": "red"}}
    )
    assert not error and done["result"]["undo_snapshot"]
    assert cmd.count_atoms("color red") == 10
    cmd.undo()
    assert cmd.count_atoms("color red") == 0
    # without a window nobody can confirm: a deletion is refused, and said so
    error, refused = call(
        url, "execute", {"command": "delete", "arguments": {"name": "ala"}}
    )
    assert error and "declined" in refused["error"] and cmd.count_atoms() == 10
    for operation, arguments in (("look", {}), ("python", {"code": "1"})):
        assert call(url, operation, arguments)[0]  # both are off
    assert call(url, "execute", {"command": "do", "arguments": {"commands": "quit"}})[0]


def test_simultaneous_calls(url):
    def many():
        results = []

        def one(color):
            reply = rpc(
                url,
                "tools/call",
                {
                    "name": "pymol",
                    "arguments": {
                        "operation": "execute",
                        "arguments": {
                            "command": "color",
                            "arguments": {"color": color},
                        },
                    },
                },
            )
            results.append(reply["result"]["isError"])

        threads = [
            threading.Thread(target=one, args=(c,))
            for c in ("red", "blue", "green") * 4
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results

    assert client(many) == [False] * 12
    assert agent.LOCK.acquire(blocking=False)  # every call gave it back
    agent.LOCK.release()
