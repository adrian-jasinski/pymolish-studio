# Roadmap checks for the user

[Current roadmap](../../PLAN.md) · [Background and deferred ideas](roadmap-background.md)

Updated 2026-11-26 at 4.90.0. Questions 128 and 129 are answered A;
there is no outstanding numbered question. These checks need the user's
accounts, other systems, a published branch or a review in their own window.
Earlier run results below remain dated evidence, not new verification.
Paths in backticks are relative to the repository root.

## Completion requirements for the open trials

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **27c** — [UI scale on Windows and macOS](27-ui-scale.md) | 27d shipped in 4.43.1: on WSLg the scale waits for the next start. Left: read what `test_scale_change_keeps_the_window_alive` prints in the Windows and macOS CI jobs (live, with the time until the window is back, or "unsupported"), and try the change once by hand on each. Needs CI for the pushed branch; the run recorded in the earlier check predates the repair. | Both systems either change the scale in the running window within the target of two seconds, or are added to `theme.live_scale_blocker`. |
| 2 | **31 trial** — [Chat and agent tools](31-ai-agents.md) | 31a and 31c shipped in 4.58.0, the connector 31b in 4.61.0 (tried with Claude Code 2.1.322 in the real window). On 2026-11-26 the user reported that the Chat tab works with Claude Code and with ChatGPT, signed in and with "Run without asking": that is the real sign-in and a conversation for those two (the sign-in of 4.66.0 and 4.80.0 had only seen stand-ins). Nothing was recorded of it here (which tasks, commands, errors, time, tokens, which system). Left: the same for OpenRouter (31d); the Chat tab with an API key of Anthropic and of OpenAI; the five recorded tasks (a ligand figure, ball-and-stick color only, a scene, a native fork command, an unavailable optional feature); the button "Continue with Claude Code" with a signed-out Claude Code; one turn on Windows or macOS; one call through the connector from Codex, whose account had no credits on 2026-11-24. | The five tasks recorded for one provider with a key and for Claude Code; a sign-in and a conversation recorded for OpenRouter; one other system; one Codex call through the connector. |
| 5 | **38 rest** — [Current documentation and real demos](38-documentation.md) | 38a to 38d were written and captured on 2026-11-26 at 4.90.0. Left: see how GitHub plays the four MP4 clips from their posters (needs the pushed branch; each has a plain link as the fallback); a picture and a clip of a finished Chat turn, after the trial of order 2; the GUI statements the checklist marks "code" were not done by hand; nothing was looked at on Windows or macOS; no reader who does not know the window. | The clips play, or their links are the documented way; the Chat picture is in `docs/assistant.md`. |

## Detailed checklist and earlier observations

- Read the new documentation, starting at `docs/README.md`, and say what
  reads wrong. Nine of its guides were written by helper sessions from the
  code and checked by running their commands; what was only read from the
  code is listed in [plan 38](38-documentation.md).
- After the branch is pushed: open `docs/appearance.md` on GitHub and click
  the poster of the clip, to see whether the MP4 plays there.
- Decide which of the faults found while writing (the list in plan 38,
  "Found in the program") are to be repaired; none was touched.
- Look at the changes of 2026-11-26 in your own window: Presets (the
  groups, the four new rows under "atoms and bonds" and "surface",
  transparency), the buttons under the object list, a light with an
  outline (figure, flat, comic, sketch), `set glow, 1`, and `show surface`
  on a large structure. All were tried in a test window on this machine;
  at the end of the run, with your pymolish closed, your `.venv` was
  rebuilt to 4.90.0 with the extras `dev`, `chem`, `fix` and `ai`.
- Look at the changes of 2026-11-25 in your own window. They were built
  and tried in a copy; at the end of the run, with pymolish closed, your
  `.venv` was rebuilt to 4.76.0 with the extras `dev`, `chem`, `fix` and
  `ai` (it had 4.67.0; the extra `ai` added `keyring` 25.7.0, which "Stay
  signed in" needs), and the suite passed there: 1121 passed, 252 skipped.
- Say where File > Get by UniProt failed (37a). On this machine the old
  plugin is not loaded (`~/.pymolpluginsrc.py` sets an empty startup
  path) and the action worked before the change; the error was
  reproduced only by putting `~/.pymol/startup` into the startup path. If
  it happened elsewhere, with another cause, it is not fixed.
- The drag with the right button (4.70.0): you reported on 2026-11-26
  that it works. If that was on Linux, Windows and macOS are still to
  try: there the system asks for the menu when the button is released.
- Push the current branch, `feature15`, then check CI. At this planning
  edit on 2026-11-26 it has no configured upstream. No fetch, push or merge
  was made, and pull request #11 was not checked. The earlier 4.90.0 run
  recorded `origin/feature13` at `5101e943`, 26 commits behind that run;
  that is historical, not the current branch status. The outstanding
  Windows, macOS and sanitizer checks cover the C++ of 4.76.1 to 4.76.14,
  4.81.0, 4.84.0 and 4.87.0 to 4.89.0, and the new shaders (`fxaa.fs`,
  `glow.fs`) on drivers other than Mesa d3d12.
- Look at Presets > surface look in your own window (4.82.0), and at
  Setting > Surface > Solid (grid) with "Cavities and Pockets Only"
  (4.81.0). Both were checked by tests and in ray-traced pictures
  (`docs/img/surface-looks.jpg`); no window was opened in that run,
  because your own pymolish was running and a test window takes the
  keyboard.
- After the push, read the CI run first for step 8: 4.76.1 to 4.76.14
  changed 60 files of the core and were compiled with GCC 13 on Linux
  only. The Windows (MSVC), macOS (Apple Clang) and `sanitize-Linux` (GCC
  11) jobs are the check that was not possible here.
- With "Run without asking" and "Trusted Python" both ticked, Python of
  the model or of an agent runs unseen, with your rights on this
  computer. That was your choice (109); recommended was commands only.
  Untick one of the two before you let it read files or pages you do not
  trust.
- Try in the Chat tab what failed: "download EGFR structures, human, by
  UniProt id". All 388 entries of P00533 (counted 2026-11-25) load in the
  background; they pass 600,000 atoms (an estimate from the first five
  entries, 28,061 atoms), and above that the chat refuses further changes
  of the session, its Undo limit. A limit ("the first 20") avoids that.
- Then the rest of the CI run: the Windows icon, release notes,
  `chem`/`fix` extras on three systems, and for 27c the line that
  `test_scale_change_keeps_the_window_alive` prints in the Windows and
  macOS jobs: "live ... shown after" with a time, or "unsupported on ...".
  The successful master run recorded in the earlier check,
  [44750297890](https://github.com/adrian-jasinski/pymolish-studio/actions/runs/44750297890),
  is at `d40f09f6`, before the scale repair. Native MAFFT launch, the agent
  connector and the FXAA shader have also been tried on Linux/WSLg only.
- Try the Chat tab with your own Anthropic and OpenAI keys and a model
  ID each (`pip install 'pymolish[ai]'`): no request with either API key was recorded in the earlier trial.
- Sign in once with OpenRouter in the Chat tab (4.66.0): choose
  OpenRouter, then "Continue with OpenRouter", and send one request. (The
  ChatGPT sign-in, the button of "OpenAI" since 4.80.0, you reported as
  working on 2026-11-26.) What was written before the first real try: the
  code follows the two published flows, and OpenAI's server took the first
  request up to its log-in page. Three things only a real try shows:
  whether OpenAI lets pymolish register without being asked first (its
  page says the plan route is for "all open-source partners"); whether
  OpenRouter takes the requests in the form the OpenAI package sends them;
  and, on WSL, whether the browser of Windows reaches the listener inside
  WSL (`127.0.0.1:1455` for ChatGPT, `localhost` with a free port for
  OpenRouter). "Stay signed in" needs a keychain service: Windows and
  macOS have one, a Linux desktop usually, WSL usually not; without one
  the box says so and the sign-in lasts for the run.
- Claude Code in the Chat tab was reported working on 2026-11-26. The
  recorded tasks below and the signed-out flow remain: on another computer,
  or after `claude auth logout`, try "Continue with Claude Code". That
  button was run against a stand-in only, since a real try would have
  signed your Claude Code out. The trial of 2026-11-24 made eleven small
  requests on your Team plan (model haiku): seven to find the right
  switches of Claude Code, four turns in the window. Each conversation leaves a transcript
  under `~/.claude/projects` (the folder named after the temporary
  directory).
- Try the connector from Codex once its account has credits: AI assistant
  > Agent connector, then "Copy setup line for Codex". On 2026-11-24
  `codex mcp list` showed the server as enabled, and `codex exec` stopped
  with "Your workspace is out of credits" before it called anything. The
  trial with Claude Code made two small requests on your Claude account
  (model haiku; the client reported 0.005 USD for the second one).
- Turn "Antialias (Real Time)" on once on Windows and on macOS and say
  whether it should be on by default.
- Compare `palettes.CPK` (`modules/pymol/palettes.py`) with the "CPK
  Colours" table of the RasMol manual (question 64).
- Look at one thing that went wrong in the run of 2026-11-23: a helper of
  the freeze test sent Ctrl+A, "120", Enter once, at about 10:06, to
  whatever window had the focus on the Windows desktop. The working tree
  was unchanged; an editor or a terminal that had the focus may show it.
- Optional user cleanup: question 128 is answered, so the reference
  pictures in `plan_images/` need no further decision. The rendering
  experiments are built; only the glow menu entry is pending. The folder
  is ignored by git and was left in place; deleting it is the user's choice.

The README screenshot (`docs/img/window.png`) is the window of 4.90.0
since step 38d (2026-11-26).
