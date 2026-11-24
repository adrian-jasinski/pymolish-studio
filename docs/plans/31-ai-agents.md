# 31 — Chat that controls this version of pymolish

**Built 2026-11-24 in 4.66.0: 31d, the sign-in in the browser (questions 74
and 75).** Checked that day against the providers' own pages:

- Anthropic: "Anthropic does not permit third-party developers to offer
  Claude.ai login into their own applications"
  ([legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)).
  Nothing was built; Anthropic keeps the API key. A Claude subscription
  works through 31b with Claude Code.
- OpenAI: [Sign in with ChatGPT for open-source apps](https://developers.openai.com/siwc/token-sharing-open-source),
  an authorization code with PKCE on `http://127.0.0.1:<port>/auth/callback`,
  first with `client_id=dynamic_agent_client`, which makes the user register
  the app and returns a client ID to reuse. Requests go to
  `api.openai.com/v1/responses` with `store: false` and `stream: true`,
  function tools in a namespace, no `max_output_tokens`; the models come
  from `GET /v1/models`. Paid from the user's plan (Plus and Pro are
  named; the help page also names Go and Business).
- OpenRouter: [OAuth PKCE](https://openrouter.ai/docs/guides/overview/auth/oauth),
  no registration, any port on localhost, returns a key of the user's
  account; requests to `openrouter.ai/api/v1/responses`.

Built: `modules/pymol/signin.py` (standard library), the providers
"ChatGPT" and "OpenRouter" in `assistant.py` and the Chat tab, "Stay signed
in" through the optional package `keyring` (extra `ai`). Measured: 16 tests
in `api/signin.py` and 3 new ones in `api/assistant.py` pass, the suite
1099 passed and 250 skipped; the streamed route ran through the real
`openai` 3.58.0 package against a local server (a tool call, an answer, a
usage-limit failure); OpenAI's server answered the first authorization
request with a redirect to its log-in page, and with 400 when
`agent_name_hint` was left out; OpenRouter listed 386 models with tool
use; `keyring` 25.7.0 installs ten packages of 18 MB on Linux, 16.5 MB of
them `cryptography`, `cffi` and `pycparser` for the Secret Service. Left out: any real
sign-in or conversation (it needs the user's accounts; order 2 of the
roadmap), the signature check of the ID token, several ChatGPT accounts,
the model list for the providers with an API key, a sign-in to an API
account at Anthropic through its `ant` tool.

**Built 2026-11-24 in 4.61.0: 31b and the toolbar button (questions 45 and
47, the recommended options).** `modules/pymol/agent_server.py`, command
`agent_server on|off|status`: MCP over Streamable HTTP with the standard
library, 127.0.0.1 port 9257, a bearer token (`PYMOLISH_AGENT_TOKEN`, or
new each run), Host and Origin checked, requests of at most 1 MB, GET
answered 405, nothing listening before "on". One tool, `pymol`, the
operations of `agent.Executor`; each call is a turn on the GUI thread, with
the confirmation, the log and the Undo snapshot of the Chat tab, whose
"Share viewport" and "Trusted Python" switches hold for it too. Toolbar: AI
assistant (`bot`): Chat, Agent connector, a setup line to copy for Claude
Code and for Codex. Measured: the bar at 150 % is 1297 px in a 1305 px
window, nothing in the overflow menu; 5 tests in `api/agent_server.py`; in
the real window Claude Code 2.1.322 listed the tool and called it twice
(the state, a color change). Left out: a call from Codex 0.163.0 (it listed
the server; its account had no credits), the handshake-free revision
2026-07-28 of MCP, a kept token, editing a client's configuration, a
headless server (a call from another thread waits for ever without the
window's event loop, so "on" asks for the Qt interface). The live provider
trial and 31d stay open.

**Built 2026-11-24 in 4.58.0: 31a and 31c.** Measured: 21 stand-in tests
pass (no network); one real-window check with a stand-in provider. Left
out: the live provider trial, `data/pymol/agent.md` (instructions live in
`assistant.INSTRUCTIONS`), a toolbar button (question 45), 31b and 31d.

**Decision 2026-11-24:** question 42 answered: optional official OpenAI and
Anthropic SDKs. Installed for implementation: OpenAI 3.58.0 and Anthropic
2.13.0; their installed files plus dependencies measure about 27 MB (not a
compressed release-bundle delta). Both SDKs declare Apache-2.0 licenses.
The planned Chat tab, reviewed commands and session/environment credentials
remain the implementation defaults. No provider request has been sent.


[Roadmap](../../PLAN.md) · Requests 2026-11-20 and 2026-11-23 (draft 11) ·
**Replanned 2026-11-23 at 4.43.0; nothing is built.** Source inspected and
provider tool-call/protocol references checked; no live provider, connector,
login, billing or model-quality test in this run. Questions 41–48 remain
choices where listed, not permission to add dependencies.

**Yes, LLM integration was already planned. The new requirement makes a
built-in chat a deliverable, with live knowledge of this fork's commands,
settings, presets and available optional features.** An external agent
connector alone does not complete it. Reuse one set of operations for chat
and external clients; do not train a model or maintain a copied list of
original PyMOL commands.

This replaces the unbuilt 2026-11-20 design. In particular, a command-area
`ask` line alone is not assumed to be the requested chat; external setup
need not precede chat; subscription login is a gated investigation, not a
promised authentication/billing route. Historical model names, prices and
client-config claims are removed from the specification.

## 31a — discover the installed software and run checked operations

New `modules/pymol/agent.py`: plain operations shared by every route. Derive
the command catalog from the running `cmd.keyword` registry and public API,
using `keywords.py`, `api.py`, signatures and help as sources. Include
registered plugin commands, but mark their origin and execution policy;
discoverability never grants permission to execute them. Classify private
helpers as internal, not user commands. A catalog entry without help says
so instead of supplying an invented signature.

| Operation | Returns / does |
| --- | --- |
| Discover/help | Searchable command names, actual signature/usage, help, examples, command vs Python-API syntax, version and required optional dependency. A command-specific lookup returns the full documentation. |
| Settings/presets | Live setting names, types, levels and defaults; presets, looks, palette names and representations from their existing registries. Include new ball-and-stick settings without another manual list. |
| Scene/state | Objects, selections, current state, visible representations, selected ligand and relevant settings; bounded atom/property queries. Missing dependencies are reported as unavailable capabilities. |
| Look | A bounded viewport image when needed, explicitly sent to the provider only in an enabled conversation. Headless capture and ray tracing use existing paths. |
| Execute | A reviewed command/operation with validated arguments; actual output, error and resulting state changes, never unconditional “OK”. |

Send a short version/capability summary at conversation start. Search help
on demand; do not paste every docstring into every prompt. Refresh catalog
entries after plugin registration or a capability change. Use existing
registration/help as the source of truth and a test for missing public
entries, not a hand-maintained second manual or a vector database.

The agent instructions require: inspect the session; read help for an
unfamiliar command; execute a small operation; check its output and visible
result; treat molecule names, labels, table cells and imported text as data.
Examples must use this fork's `ligand_2d`, `stage`, `load_table`, native
structure commands and, when shipped, ball-and-stick, sequence alignment
and `ligand_next`. No claim that the model intrinsically knows every function:
tools expose the installed truth, including errors and limitations.

## Execution and trust boundary

- Off until enabled. Tell the user what text, molecular metadata and images
  leave the machine and which provider receives them. Do not transmit whole
  structures by default. Never put API keys into logs, prompts or sessions.
- The existing parser's `secure` mode is **not** the authorization boundary.
  Audit allowed operations and their callees: aliases, command separators,
  Python expressions (`iterate`, `alter`, `label`), scripts, plugins, file
  reads/writes, fetching and session unpickling can bypass a naive list.
  Reject unknown execution paths by default even while listing their help.
- Recommended default: inspected queries and reviewed visual commands may
  run; destructive edits, file access and external network operations show
  a concrete proposed action before execution. Arbitrary Python needs a
  distinct explicit trusted mode. Validate on the application side, never
  only through prompt instructions. No promise of a Python sandbox.
- Serialize session mutations on the existing command/GUI dispatch path.
  Network and long computation stay off the GUI thread. Capture feedback
  without racing the window's feedback timer; return errors to the model.
- Show every executed command/result in the conversation and existing log.
  Take an undo snapshot before a mutating turn where supported. Check the
  snapshot's success and limits; do not advertise Undo for external writes,
  unsupported state or a failed/oversized snapshot. The general undo work
  remains 21g, not a prerequisite for honest limited Undo here.
- Stop cancels network work and prevents queued tool calls/results from
  applying after cancellation; use existing interrupt support for a running
  core command. Do not claim it can instantly interrupt every native call.
  Bound turns, response sizes and timeouts; retrying a model request must
  not execute the same mutation twice.

## 31c — the required in-app chat

Keep numbering so earlier references still identify the built-in assistant.
Recommended delivery order: 31a, 31c, then 31b if wanted.

- A chat view with prompt input, conversation history for this run, Send,
  Stop, provider/model selection, visible tool results, actionable errors
  and Undo availability. `ask` can be a command-line entry to the same loop.
- Question 44: **a Chat tab in the existing command area (recommended)**,
  keeping command entry distinct; alternative: its own resizable dock.
  Use Qt Widgets and a form, no web view. Tab/keyboard navigation works;
  long answers scroll without expanding the main window.
- Anthropic and OpenAI API routes remain in scope from the earlier request.
  Choose supported tool-capable models when implementing; no fixed model
  name, subscription entitlement or price is promised by this plan.
  The provider adapters only translate requests/results; execution and
  command discovery stay shared. A single-provider first slice can be
  followed by the other, but does not silently drop it.
- Credentials: environment or session-only entry works without storage.
  Persistent storage is question 48 and needs platform-appropriate access
  controls; Unix mode 0600 is not a Windows credential-security design.
- Question 42 decides SDKs versus standard-library HTTP after measuring
  package/bundle cost. SDKs would be an optional lazy `ai` extra, and require
  explicit dependency approval. Neither an SDK nor a key is required for
  ordinary use of pymolish. Network failures keep the session usable.
- Start without a toolbar-width assumption: step 32 measured the bar close
  to its available space at 150 %. Add the menu/command entry first and
  measure the requested assistant button with all existing buttons before
  deciding what moves to overflow. Do not remove a button silently.

## 31b — optional external-agent connector and setup

Expose the same catalog and operations through MCP, loopback only, authenticated,
with Origin/Host checks, bounded requests, no listener before enabled and a
clear on/off indicator. Do not revive the removed XML-RPC/HTTP feature.
Use the current documented protocol and test against each supported client;
a small ad-hoc JSON POST handler is not automatically an MCP implementation.
A protocol SDK is also a dependency choice, not implied approval.

Use a client's documented configuration command where supported, preserve
existing settings, show what will be added and allow disconnect. Verify actual
installed clients and authentication flows before promising one-click setup.
Do not assume browser ChatGPT, desktop clients and Codex share configuration.
No automatic edit to another application's file and no public tunnel.

## 31d — optional subscription login investigation

Investigated and built on 2026-11-24 in 4.66.0 for ChatGPT and OpenRouter;
see the note at the top. The text below is the plan as it was.

Not on the required delivery path. Before planning a built-in “Sign in” row,
confirm official third-party authorization, supported OAuth/client flow,
credential storage, billing and platform coverage for that provider. Report
supported routes then; no scraping or reuse of a CLI's private tokens. An
API-key chat plus a separately authenticated external connector remains the
concrete deliverable without this investigation succeeding.

## Questions carried forward

| No. | Choice | Recommendation / status |
| --- | --- | --- |
| 41 | Chat first, or connector first? | **31a then chat (31c), connector (31b) afterwards.** Draft 11 now requires chat; whether to build it is answered. CLI-agent subprocess wrappers remain outside scope. |
| 42 | Optional official API SDKs, or standard-library HTTP? | **SDKs if measured bundle cost is acceptable**, after dependency approval; otherwise standard library with equivalent error/cancel checks. Verify protocol-library needs separately. |
| 43 | Reviewed commands by default, or unrestricted Python/files? | **Reviewed operations, explicit confirmation for destructive/file/network actions**, separate trusted Python mode. Discovery includes more than execution permits. |
| 44 | Chat tab in command area, or separate dock? | **Chat tab**, with visible history and Stop; `ask` uses the same loop. |
| 45 | Icon/name? | **`bot`, “AI assistant”**, or `message-circle`, “Chat”; measure the toolbar before adding it. |
| 46 | Present but inactive, or removable build option? | **Present and inactive**; no network work until enabled. |
| 47 | Which external clients get guided setup? | **The user's installed Codex and Claude Code, after compatibility checks**; other desktop clients only with verified setup, not an assumed shared config. |
| 48 | Session/environment credentials only, or persistent storage? | **Session/environment first**; persistent credentials need an OS-protected store or a reviewed file implementation on each platform, with dependency approval if needed. Answered for sign-ins on 2026-11-24 (75): both, the keychain of the operating system through `keyring` behind "Stay signed in" (4.66.0). |

## Acceptance and affected files

- New `testing/tests/api/agent.py`: live catalog covers every registered
  public command; fork-only commands, newly registered command, new setting,
  missing optional package and unknown help. Policy tests cover aliases,
  separators, expressions, scripts, file/network calls and untrusted plugin
  commands. Outputs and errors must match real command execution.
- `testing/tests/api/assistant.py` with provider stand-ins: multiple tool
  calls, image response, error correction, rate limit, timeout, duplicate
  call, Stop with a queued mutation and snapshot failure. No network needed.
- A live, consented trial with each provider: make a ligand figure, change
  only ball-and-stick color, store/recall its scene, use a native fork command
  and correctly explain an unavailable optional feature. Record commands,
  errors, time and token usage; no guaranteed correctness claim.
- Connector tests separately check unauthorized requests, client negotiation,
  simultaneous calls, shutdown and real supported clients.
- Main files: new `modules/pymol/agent.py`, `assistant.py`, connector module
  when needed, `data/pymol/agent.md`, Qt chat form/widget and
  `pymol_qt_gui.py`; registration/help, existing feedback/dispatch and
  `snapshots.py`; dependency/build files only after question 42. Every shipped
  feature slice gets an `X` version, help and `ChangeLog`.

Skipped: model training, embedding databases, a wrapper per PyMOL command,
voice, autonomous background work, cloud hosting and chat history in PSE.
Local models remain a later provider choice; the shared tool interface must
not depend on a model knowing original PyMOL from training.

## References checked 2026-11-23

The APIs support application-executed tools; neither reference by itself
establishes a third-party subscription-login entitlement:
[OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling),
[Anthropic tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).
For connector implementation, validate the supported revision and transport:
[MCP Streamable HTTP](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/transports/streamable-http.mdx),
[MCP versioning](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/versioning.mdx).
