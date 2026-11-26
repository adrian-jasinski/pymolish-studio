"""The agent connector (31b): the operations of pymol.agent for an external
agent on this computer (Claude Code, Codex), as an MCP server over Streamable
HTTP. Loopback only, a bearer token, nothing listens before "agent_server on".

ponytail: answers the handshake revisions of MCP below with plain JSON, one
tool, no event stream and no sessions. The stateless revision 2026-07-28 is
not answered: add it when a supported client stops sending "initialize".
"""

import hmac
import json
import os
import secrets
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pymol import CmdException, assistant, cmd

PORT = 9257
VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26")  # newest first
MAX_BODY = 1_000_000
TOKEN_VARIABLE = "PYMOLISH_AGENT_TOKEN"
LOCAL = ("127.0.0.1", "localhost")

_server = None


class RpcError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Handler(BaseHTTPRequestHandler):
    timeout = 30  # a client that stops sending does not keep a thread
    server_version = "pymolish"

    def log_message(self, format, *args):
        pass  # the token and the requests stay out of the terminal

    def _send(self, status, body=None):
        data = b"" if body is None else json.dumps(body, default=str).encode()
        self.send_response(status)
        if data:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self._send(405)  # no event stream, no session to end

    do_DELETE = do_GET

    def do_POST(self):
        server = self.server
        local = {"%s:%d" % (name, server.server_port) for name in LOCAL}
        origin = self.headers.get("Origin")
        # a web page that reaches this port (DNS rebinding) is turned away
        if self.headers.get("Host") not in local or (
            origin is not None and origin.partition("://")[2] not in local
        ):
            return self._send(403)
        given = self.headers.get("Authorization", "").encode("latin-1", "replace")
        if not hmac.compare_digest(given, b"Bearer " + server.token.encode()):
            return self._send(401)
        if self.path != "/mcp":
            return self._send(404)
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= MAX_BODY:
                return self._send(413)
            message = json.loads(self.rfile.read(length))
            if not isinstance(message, dict):
                raise ValueError("one message per request")
        except (ValueError, OSError):
            return self._send(400, _reply(None, error=(-32700, "Parse error")))
        if "method" not in message or "id" not in message:
            return self._send(202)  # a notification or a response: no answer
        try:
            params = message.get("params") or {}
            if not isinstance(params, dict):
                raise RpcError(-32602, "params must be an object")
            reply = _reply(message["id"], server.rpc(message["method"], params))
        except RpcError as error:
            reply = _reply(message["id"], error=(error.code, str(error)))
        self._send(200, reply)


def _reply(id, result=None, error=None):
    reply = {"jsonrpc": "2.0", "id": id}
    if error:
        reply["error"] = {"code": error[0], "message": error[1]}
    else:
        reply["result"] = result
    return reply


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, token, executor, _self=cmd):
        super().__init__(("127.0.0.1", port), Handler)
        self.token, self.executor, self.cmd = token, executor, _self

    def rpc(self, method, params):
        tool = assistant.TOOL
        if method == "initialize":
            asked = params.get("protocolVersion")
            return {
                "protocolVersion": asked if asked in VERSIONS else VERSIONS[0],
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "pymolish",
                    "version": self.cmd.get_version()[0],
                },
                "instructions": assistant.INSTRUCTIONS,
            }
        if method == "ping":
            return {}
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "inputSchema": tool["parameters"],
                    }
                ]
            }
        if method != "tools/call":
            raise RpcError(-32601, "Method not found: %s" % method)
        arguments = params.get("arguments")
        if (
            params.get("name") != tool["name"]
            or not isinstance(arguments, dict)
            or not isinstance(arguments.get("operation"), str)
            or not isinstance(arguments.get("arguments", {}), dict)
        ):
            raise RpcError(-32602, "Expected the tool pymol: operation, arguments")
        result = self.call(arguments["operation"], arguments.get("arguments", {}))
        value = result.get("result")
        if isinstance(value, dict) and "image" in value:
            content = {
                "type": "image",
                "data": value["image"],
                "mimeType": value["mime_type"],
            }
        else:
            content = {"type": "text", "text": json.dumps(result, default=str)}
        return {"content": [content], "isError": not result["ok"]}

    def call(self, operation, arguments):
        """One tool call is one turn: it runs on the GUI thread, after the
        calls before it, and a change keeps an Undo snapshot of its own."""
        executor, call_id = self.executor, uuid.uuid4().hex

        def run():
            executor.begin_turn()
            try:
                return executor.call(call_id, operation, arguments)
            finally:
                executor.results.pop(call_id, None)

        try:
            return self.cmd._call_in_gui_thread(run)
        except CmdException as error:  # cancelled before it ran
            return {"ok": False, "error": str(error)}


def setup(port, token):
    """What the user runs once in a terminal to connect each client."""
    url = "http://127.0.0.1:%d/mcp" % port
    return {
        "Claude Code": 'claude mcp add --transport http pymolish %s --header "Authorization: Bearer %s"'
        % (url, token),
        "Codex": "export %s=%s && codex mcp add pymolish --url %s --bearer-token-env-var %s"
        % (TOKEN_VARIABLE, token, url, TOKEN_VARIABLE),
    }


def agent_server(action="status", port=PORT, quiet=0, *, _self=cmd):
    """
    DESCRIPTION

        "agent_server" lets an AI agent on this computer (Claude Code, Codex)
        work in this session through MCP: it finds the installed commands and
        settings, reads the session and runs reviewed operations, the same ones
        as the Chat tab, and its switches "Share viewport" and "Trusted Python"
        hold here too. Actions that delete, read or write files or use the
        network ask first in the window. Requires the Qt interface.

        Nothing listens until "agent_server on". The server answers on
        127.0.0.1 only, to requests that carry the token. The token is the
        environment variable PYMOLISH_AGENT_TOKEN, or a new one for each run.
        "on" prints the line that connects each client, with the token.

    USAGE

        agent_server [ action [, port ]]

    ARGUMENTS

        action = on, off or status {default: status}

        port = integer: the port on 127.0.0.1 {default: 9257}

    PYMOL API

        cmd.agent_server(action, port)  # the URL while on, else None
    """
    from . import gui

    global _server
    window = gui.get_qtwindow()
    if action not in ("on", "off", "status"):
        raise CmdException("agent_server: on, off or status")
    if action != "status" and _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
    if action == "on":
        if window is None:  # nothing would run the calls: see Server.call
            raise CmdException("agent_server requires the Qt interface")
        token = os.environ.get(TOKEN_VARIABLE) or secrets.token_urlsafe(24)
        try:
            _server = Server(int(port), token, window.chat_panel.connector, _self)
        except OSError as error:
            raise CmdException(
                "agent_server: port %s cannot be used (%s); name another one"
                % (port, error.strerror)
            ) from None
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    url = _server and "http://127.0.0.1:%d/mcp" % _server.server_port
    if window is not None and action != "status":
        _self._call_in_gui_thread(lambda: window.show_agent_server(bool(url)))
    if not int(quiet):
        print(" Agent connector: %s" % (url or "off"))
        if action == "on":
            for client, line in setup(_server.server_port, _server.token).items():
                print(" %s: %s" % (client, line))
    return url
