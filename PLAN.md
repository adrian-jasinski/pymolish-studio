# pymolish-studio — current roadmap

Updated 2026-11-27 at **4.94.1**. The user's request to implement 15q,
15r and 21g answered **question 139** with A (both slices). Shipped: the
glow, outline and smoothing in pictures of any size (15q, 4.92.0), the
glow in ray-traced pictures (15r, 4.93.0), undo of every step (21g,
4.94.0) and the removal of what only stood for the commercial build
(4.94.1). Steps 15 and 21 are finished. Answer **129 A** keeps Solid as
the default surface. The Windows installer request adds **5d**, order 4.
Question **137 A** is recorded: a per-user Inno Setup `.exe` plus the
portable ZIP, **unsigned for now**; signing (question 138) is deferred
until the user asks for it.

Keep Qt Widgets with PySide6. Follow [AGENTS.md](AGENTS.md): smaller,
faster, simpler, prettier.

| Read more | Contents |
| --- | --- |
| [Shipped state](PLAN-STATE.md) | Released versions and current capabilities. |
| [Decisions and finished work](PLAN-DONE.md) | Accepted choices, completed steps and their results. |
| [Background and deferred ideas](docs/plans/roadmap-background.md) | Review history, original draft corrections, settled-decision notes and work excluded from the current plan. |
| [User checks](docs/plans/roadmap-checks.md) | Detailed platform/account trials, manual checks and earlier observations. |

## Open work, in execution order

Orders 1 and 2 need other systems or accounts; proceed with order 3 when
those are unavailable. Step numbers and slice letters identify the detailed
plans and stay stable. Each implementation slice follows the version rules
in `AGENTS.md`; documentation alone takes no version.

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **27c** — [UI scale on Windows and macOS](docs/plans/27-ui-scale.md) | Push the branch, read the scale-test output in CI, and try a scale change by hand on each system. WSLg already uses the next-start fallback. | Both systems restore the live window within the target of two seconds, or are added to `theme.live_scale_blocker`. |
| 2 | **31 trial** — [Chat and agent tools](docs/plans/31-ai-agents.md) | Claude Code and ChatGPT work according to the user's 2026-11-26 report. Complete the [remaining provider, task and connector trials](docs/plans/roadmap-checks.md#completion-requirements-for-the-open-trials). | Five tasks recorded for one API-key provider and Claude Code; OpenRouter sign-in and conversation; one other system; one Codex connector call. |
| 3 | **38 rest** — [Documentation and demos](docs/plans/38-documentation.md) | Verify MP4 playback from GitHub posters after pushing; add a finished Chat turn picture/clip after order 2; complete the checklist's manual, platform and new-reader checks. | Clips play or fallback links are documented; the Chat picture is in `docs/assistant.md`; outstanding checks are recorded. |
| 4 | **5d** — [Windows installer and code signing](docs/plans/05-builds-binaries.md#5d--windows-installer-and-code-signing) | Answer 137 A: package the existing Windows bundle as an unsigned per-user Inno Setup `.exe` with installation, upgrade and uninstall, beside the ZIP, and publish it with checksums. Signing waits for question 138. | The downloaded installer installs, launches, upgrades and uninstalls on clean Windows with protections on; checksums verify. The expected "unknown publisher" SmartScreen prompt is recorded, not hidden. |
| 5 | **39** — [Install after cloning](docs/plans/39-source-install.md) | Current request: plan first, then implement `./install` and `install.cmd`, OS detection, dependency setup and actionable fallback instructions. | Preview and failure checks pass; local build verified; native platform trials recorded honestly. |
| any time | **1b** — [Measured performance work](docs/plans/01-performance-gpu.md) | Profile surface triangulation and sticks/lines drawn as triangles on a quiet machine; driver comparisons also need Windows/macOS. | Each change has before/after measurements. |

The remaining documentation and the Windows installer are orders 3 and
4. Answer 129 needs no code change: Solid stays the default and Solid
(grid) remains optional.

The Windows request reopens step 5 after its completed bundle work; 5c
stays shelved. An installer alone cannot establish Windows trust: until
signing is added, SmartScreen will show an "unknown publisher" prompt for
the downloaded installer. No plan can guarantee that SmartScreen, Defender
or a managed-device policy will never block a build.

## Waiting for the user

Step 39 choices were offered on 2026-11-27: Linux system packages with
Pixi on Windows/macOS and as a Python fallback (recommended), or Pixi
everywhere; core with an extras prompt (recommended), or all user extras.
The recommended defaults apply unless the user selects otherwise.

No numbered question is open.
[Answer 139 A](PLAN-DONE.md#decision-139) is recorded and built.
[Answer 137 A](PLAN-DONE.md#decision-137) is recorded
with signing skipped for now; question 138 (signing provider) is
**deferred**, not open: it comes back when the user asks for signing.
[Answers 128 and 129](PLAN-DONE.md#decisions-128-and-129) remain recorded.
Details are in [5d](docs/plans/05-builds-binaries.md#choices-before-implementation).

The following checks remain:

- `feature15` is pushed up to `10f87ea9`; CI run 45834660395 on
  `25238548` passed every job (Linux, sanitizer, Windows and macOS).
  4.91.0 to 4.94.1 and their plan updates are committed locally, not
  pushed; CI has not seen them. PR #12 (`feature14`) does not
  contain that fix yet and stays red until it does. Try UI scale,
  right-button dragging and FXAA on Windows and macOS by hand.
- Try the new Undo in your own window: a few typed lines and menu rows,
  a drag of atoms in Editing mode, then Undo/Redo and their tooltips
  (checked here only by a script in the real window under WSLg, without
  a mouse drag). Save a picture with glow on (Draw (fast) and Ray) on
  your GPU.
- Complete the account and task trials for order 2; record commands,
  errors, time, tokens and the system used.
- Read the [documentation](docs/README.md), test the video posters after
  the push, and choose which faults listed in [plan 38](docs/plans/38-documentation.md)
  should become repair tasks.
- Review the recent presets, footer, surface and glow changes in your own
  window, including Presets > light > glow on your GPU (tried only on the
  integrated AMD GPU under WSLg). The [detailed checklist](docs/plans/roadmap-checks.md) keeps the
  individual checks, CPK comparison and optional reference-picture cleanup.

## Working rules

- One implementation slice per session/PR; start from its linked plan.
- Follow [AGENTS.md](AGENTS.md) for versioning, checks and plan upkeep.
- Keep file formats, supported commands and plugin loading working; report
  checks that could not run. [Full completion criteria](docs/plans/roadmap-background.md#shared-completion-criteria).
- Deferred ideas stay outside the current work until requested. MAFFT stays
  separately installed; provider SDKs stay in the lazy `ai` extra; builds
  stay on GitHub Actions (5c remains shelved).
