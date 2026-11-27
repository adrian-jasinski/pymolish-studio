"""The chat loop with provider stand-ins (31c); no network, no SDK."""

import asyncio
import json
import os
import sys
import threading
import time
import types

import pytest

from pymol import CmdException, agent, assistant, cmd, signin, snapshots


class Anthropic:
    """Replies with the queued responses; records what it was sent."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.sent = []
        self.messages = self

    async def create(self, **request):
        self.sent.append(json.loads(json.dumps(request["messages"])))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        if response == "hang":
            await asyncio.sleep(60)
        return response


def use(call_id, operation, **arguments):
    return {
        "type": "tool_use",
        "id": call_id,
        "name": "pymol",
        "input": {"operation": operation, "arguments": arguments},
    }


def reply(*blocks):
    return {"content": list(blocks), "usage": {"input_tokens": 3, "output_tokens": 2}}


TEXT = {"type": "text", "text": "Done."}


@pytest.fixture
def chat():
    snapshots._undo.clear()
    cmd.fragment("ala")
    executor = agent.Executor(cmd)
    emitted = []
    conversation = assistant.Conversation(
        "Anthropic", "stand-in", executor, emit=lambda *a: emitted.append(a)
    )
    conversation.emitted = emitted
    return conversation


def run(conversation, client, prompt="color it"):
    return asyncio.run(conversation.run_client(prompt, client))


def results(client, index=-1):
    return client.sent[index][-1]["content"]


def test_multiple_calls_and_error_correction(chat):
    client = Anthropic(
        reply(
            use("a", "state"),
            use("b", "execute", command="do", arguments={"commands": "quit"}),
        ),
        reply(
            use(
                "c",
                "execute",
                command="color",
                arguments={"color": "red", "selection": "all"},
            )
        ),
        reply(TEXT),
    )
    report = run(chat, client)
    first = results(client, 1)
    assert [r["is_error"] for r in first] == [False, True]
    assert report["tool_calls"] == 3 and report["input_tokens"] == 9
    assert ("assistant", "Done.") in chat.emitted
    assert len(snapshots._undo) == 1


def test_image_result(chat):
    chat.executor.images = True
    chat.dispatch = lambda *a: {
        "ok": True,
        "result": {"image": "iVBOR", "mime_type": "image/png"},
    }
    client = Anthropic(reply(use("a", "look")), reply(TEXT))
    run(chat, client)
    assert results(client)[0]["content"][0]["type"] == "image"


def test_duplicate_call_runs_once(chat):
    calls = []
    executor_call = chat.executor.call
    chat.dispatch = lambda *a: calls.append(a) or executor_call(*a)
    same = use(
        "a", "execute", command="color", arguments={"color": "blue", "selection": "all"}
    )
    run(chat, Anthropic(reply(same, same), reply(TEXT)))
    assert len(calls) == 2 and len(chat.executor.results) == 1


@pytest.mark.parametrize(
    "error", [TimeoutError("timed out"), RuntimeError("429 rate limit")]
)
def test_provider_errors_are_reported(chat, error):
    client = Anthropic(error)

    async def wrapped():
        try:
            return await chat.run_client("hi", client)
        except Exception as e:
            raise CmdException(str(e)) from None

    with pytest.raises(CmdException):
        asyncio.run(wrapped())
    assert cmd.get_names() == ["ala"]


def test_stop_drops_queued_mutation(chat):
    executed = []

    def dispatch(*a):
        executed.append(a)
        chat.executor.cancel.set()  # Stop arrives after the first call
        return {"ok": True, "result": None}

    chat.dispatch = dispatch
    client = Anthropic(
        reply(
            use("a", "state"),
            use("b", "execute", command="delete", arguments={"name": "all"}),
        )
    )
    with pytest.raises(CmdException, match="Cancelled"):
        run(chat, client)
    assert len(executed) == 1 and cmd.get_names() == ["ala"]


def test_stop_cancels_waiting_request(chat):
    client = Anthropic("hang")

    async def stop_soon():
        task = asyncio.ensure_future(chat.run_client("hi", client))
        await asyncio.sleep(0.2)
        chat.executor.cancel.set()
        return await task

    with pytest.raises(CmdException, match="Cancelled"):
        asyncio.run(stop_soon())


def test_snapshot_failure_executes_nothing(chat, monkeypatch):
    monkeypatch.setattr(snapshots, "ATOMS", 1)
    shown = agent.scene_state()["visible_representations"]
    client = Anthropic(
        reply(use("a", "execute", command="hide", arguments={})), reply(TEXT)
    )
    run(chat, client)
    assert results(client)[0]["is_error"]
    assert not snapshots._undo
    assert agent.scene_state()["visible_representations"] == shown
    assert any(shown.values())


def test_openai_shape(chat):
    chat.provider = "OpenAI"

    class Client:
        def __init__(self):
            self.sent = []
            self.responses = self
            self.queue = [
                {
                    "output": [
                        {
                            "type": "function_call",
                            "call_id": "a",
                            "name": "pymol",
                            "arguments": json.dumps(
                                {"operation": "state", "arguments": {}}
                            ),
                        }
                    ]
                },
                {
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "Done."}],
                        }
                    ]
                },
            ]

        async def create(self, **request):
            self.sent.append(json.loads(json.dumps(request["input"])))
            return self.queue.pop(0)

    client = Client()
    run(chat, client)
    output = client.sent[1][-1]
    assert (
        output["type"] == "function_call_output" and json.loads(output["output"])["ok"]
    )


class PlanClient:
    """Streams the queued events, as requests on a ChatGPT plan must."""

    def __init__(self, *streams):
        self.streams = list(streams)
        self.sent = []
        self.responses = self

    async def create(self, **request):
        self.sent.append(json.loads(json.dumps(request)))  # input grows later
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, *error):
        pass

    async def __aiter__(self):
        for event in self.streams.pop(0):
            yield types.SimpleNamespace(**event)


def test_chatgpt_plan_streams_namespaced_tools(chat):
    chat.provider = "ChatGPT"
    call = {
        "type": "function_call",
        "call_id": "a",
        "namespace": "pymolish",
        "name": "pymol",
        "arguments": json.dumps({"operation": "state", "arguments": {}}),
    }
    message = {"type": "message", "content": [{"type": "output_text", "text": "Done."}]}
    client = PlanClient(
        [
            {"type": "response.output_item.done", "item": call},
            # this route may finish without repeating the items
            {"type": "response.completed", "response": {"output": []}},
        ],
        [{"type": "response.completed", "response": {"output": [message]}}],
    )
    run(chat, client)
    first, second = client.sent
    assert first["stream"] is True and first["store"] is False
    assert "max_output_tokens" not in first
    assert [t["type"] for t in first["tools"]] == ["namespace"]
    assert first["tools"][0]["tools"][0]["name"] == "pymol"
    output = second["input"][-1]
    assert output["call_id"] == "a" and json.loads(output["output"])["ok"]
    assert ("assistant", "Done.") in chat.emitted


@pytest.mark.parametrize(
    "events, message",
    [
        (
            [
                {
                    "type": "response.failed",
                    "response": {
                        "error": {"code": "subscription_sharing_usage_limit_exceeded"}
                    },
                }
            ],
            "usage_limit_exceeded",
        ),
        ([], "ended before"),
    ],
)
def test_chatgpt_plan_counts_only_a_completed_response(chat, events, message):
    chat.provider = "ChatGPT"
    with pytest.raises(CmdException, match=message):
        run(chat, PlanClient(events))


# A stand-in for "claude -p": it notes its arguments, calls the tool of the MCP
# server it was given and answers in Claude Code's stream of JSON lines.
CLAUDE = r"""
import json, os, sys, time, urllib.request
args, prompt, mode = sys.argv[2:], sys.stdin.read(), open(sys.argv[1] + ".mode").read()
server = json.load(open(args[args.index("--mcp-config") + 1]))["mcpServers"]["pymolish"]
with open(sys.argv[1], "a") as log:
    log.write(json.dumps({"args": args, "prompt": prompt, "cwd": os.getcwd(),
                          "system": open(args[args.index("--system-prompt-file") + 1]).read()}) + "\n")
def say(**event):
    print(json.dumps(event), flush=True)
def rpc(method, **params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    request = urllib.request.Request(server["url"], body, {**server["headers"], "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(request))["result"]
print("a line that is not JSON", flush=True)
say(type="system", subtype="init", session_id="s-1")
if mode == "hang":
    time.sleep(60)
if mode == "fail":
    say(type="result", is_error=True, result="Not logged in · Please run /login", session_id="s-1")
    sys.exit(1)
if mode == "crash":
    sys.exit("claude: unknown option")
answer = rpc("tools/call", name="pymol", arguments={"operation": "state", "arguments": {}})
say(type="assistant", message={"content": [{"type": "text", "text": "Saw " + answer["content"][0]["text"]}]})
say(type="result", is_error=False, result="Done.", session_id="s-1",
    usage={"input_tokens": 2, "cache_read_input_tokens": 5, "output_tokens": 4})
"""


@pytest.fixture
def claude_code(chat, monkeypatch, tmp_path):
    """A conversation through the stand-in; .mode chooses what it does."""
    log, script = tmp_path / "log", tmp_path / "claude.py"
    script.write_text(CLAUDE, encoding="utf-8")
    monkeypatch.setattr(
        signin, "claude", lambda: [sys.executable, str(script), str(log)]
    )
    seen = []

    def dispatch(call_id, operation, arguments):
        seen.append((call_id, operation, arguments))
        return {"ok": True, "result": {"objects": ["ala"]}}

    conversation = assistant.Conversation(
        "Claude Code",
        "default",
        chat.executor,
        dispatch,
        lambda *a: chat.emitted.append(a),
    )
    conversation.emitted, conversation.seen = chat.emitted, seen
    conversation.mode = (tmp_path / "log.mode").write_text
    conversation.log = lambda: [
        json.loads(line) for line in log.read_text().splitlines()
    ]
    conversation.mode("")
    return conversation


def test_claude_code_turn_serves_the_tool_and_resumes_the_session(claude_code):
    report = asyncio.run(claude_code.run("what is loaded?"))
    assert report["tool_calls"] == 1 and report["input_tokens"] == 7
    assert [s[1:] for s in claude_code.seen] == [("state", {})]
    assert claude_code.emitted[0] == (
        "assistant",
        'Saw {"ok": true, "result": {"objects": ["ala"]}}',
    )
    claude_code.model = "opus"
    asyncio.run(claude_code.run("and now?"))
    first, second = claude_code.log()
    assert first["prompt"] == "what is loaded?" and "--resume" not in first["args"]
    assert "--model" not in first["args"]  # "default" leaves it to Claude Code
    assert second["args"][-4:] == ["--model", "opus", "--resume", "s-1"]
    assert first["cwd"] == second["cwd"]  # a session resumes only where it began
    assert "Installed capabilities" in first["system"]
    # nothing of the user's Claude Code but its sign-in: no tools, no other servers
    assert first["args"][first["args"].index("--tools") + 1] == ""
    assert {"--restricted", "--strict-mcp-config"} <= set(first["args"])
    assert (
        first["args"][first["args"].index("--allowed-tools") + 1]
        == "mcp__pymolish__pymol"
    )
    config = first["args"][first["args"].index("--mcp-config") + 1]
    assert not os.path.exists(config)  # the token went with the turn
    assert claude_code.seen[0][0] != claude_code.seen[1][0]


@pytest.mark.parametrize(
    "mode, message",
    [("fail", "Please run /login"), ("crash", "unknown option")],
)
def test_claude_code_failure_is_reported_and_starts_a_new_session(
    claude_code, mode, message
):
    asyncio.run(claude_code.run("first"))
    claude_code.mode(mode)
    with pytest.raises(CmdException, match=message):
        asyncio.run(claude_code.run("second"))
    assert claude_code.session is None


def test_claude_code_needs_the_program_and_a_plain_model_name(claude_code, monkeypatch):
    claude_code.model = "opus; rm -rf"
    with pytest.raises(CmdException, match="Not a model name"):
        asyncio.run(claude_code.run("hello"))
    monkeypatch.setattr(signin, "claude", lambda: None)
    with pytest.raises(CmdException, match="not installed"):
        asyncio.run(claude_code.run("hello"))


def test_stop_ends_claude_code(claude_code):
    claude_code.mode("hang")
    threading.Timer(0.5, claude_code.executor.cancel.set).start()
    started = time.monotonic()
    with pytest.raises(CmdException):
        asyncio.run(claude_code.run("hello"))
    assert time.monotonic() - started < 10
