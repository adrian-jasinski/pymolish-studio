"""The chat loop with provider stand-ins (31c); no network, no SDK."""

import asyncio
import json

import pytest

from pymol import CmdException, agent, assistant, cmd, snapshots


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
