# pymolish-studio — current roadmap

Updated 2026-11-26 at **4.91.0**. The glow menu of answer **128 A**
shipped in 4.91.0: "glow" / "no glow" beside fog in Presets > light, for
the viewport only. A request the same evening plans the glow in saved
pictures, **15q and 15r**, order 3; **question 139** is open. Answer **129 A** keeps Solid as the
default surface. The Windows installer request adds **5d**, order 6. Question
**137 A** is recorded: a per-user Inno Setup `.exe` plus the portable ZIP,
**unsigned for now**; signing (question 138) is deferred until the user
asks for it.

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
| 3 | **15q, 15r** — [Glow in saved pictures](docs/plans/15-presets.md#request-2026-11-26-evening-glow-in-saved-pictures-15q-15r) | After question 139: 15q runs the post-process (glow, viewport outline, smoothing) for Draw (fast) and `png` pictures of any size; 15r adds the halo to ray-traced pictures on the CPU, from the ray depth. | The measured table of the plan: the sized and the ray rows show a halo whose share is close to the window's; the suite passes. |
| 4 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend preset snapshots to add/remove/edit commands, retain the coordinate ring, finish toolbar labels and tests. Then remove the incentive error/mark and `-n`. | Existing undo/jira cases pass before removing the marks in `jira/PYMOL-1276.py` and `jira/PYMOL-1697.py`. |
| 5 | **38 rest** — [Documentation and demos](docs/plans/38-documentation.md) | Verify MP4 playback from GitHub posters after pushing; add a finished Chat turn picture/clip after order 2; complete the checklist's manual, platform and new-reader checks. | Clips play or fallback links are documented; the Chat picture is in `docs/assistant.md`; outstanding checks are recorded. |
| 6 | **5d** — [Windows installer and code signing](docs/plans/05-builds-binaries.md#5d--windows-installer-and-code-signing) | Answer 137 A: package the existing Windows bundle as an unsigned per-user Inno Setup `.exe` with installation, upgrade and uninstall, beside the ZIP, and publish it with checksums. Signing waits for question 138. | The downloaded installer installs, launches, upgrades and uninstalls on clean Windows with protections on; checksums verify. The expected "unknown publisher" SmartScreen prompt is recorded, not hidden. |
| any time | **1b** — [Measured performance work](docs/plans/01-performance-gpu.md) | Profile surface triangulation and sticks/lines drawn as triangles on a quiet machine; driver comparisons also need Windows/macOS. | Each change has before/after measurements. |

The glow in saved pictures is the next local task once question 139 is
answered; until then, general undo (order 4) can go first. General undo,
the remaining documentation and the Windows installer are orders 4, 5
and 6. Answer 129 needs no code change:
Solid stays the default and Solid (grid) remains optional.

The Windows request reopens step 5 after its completed bundle work; 5c
stays shelved. An installer alone cannot establish Windows trust: until
signing is added, SmartScreen will show an "unknown publisher" prompt for
the downloaded installer. No plan can guarantee that SmartScreen, Defender
or a managed-device policy will never block a build.

## Waiting for the user

**Question 139 — which saved pictures get the glow?**
[Plan](docs/plans/15-presets.md#question-139-which-pictures-get-the-glow).
**A (recommended):** both, 15q (Draw (fast) and `png` of any size, which
also brings the viewport outline into those pictures) and then 15r
(ray-traced pictures). **B:** 15q only. **C:** 15r only.

[Answer 137 A](PLAN-DONE.md#decision-137) is recorded
with signing skipped for now; question 138 (signing provider) is
**deferred**, not open: it comes back when the user asks for signing.
[Answers 128 and 129](PLAN-DONE.md#decisions-128-and-129) remain recorded.
Details are in [5d](docs/plans/05-builds-binaries.md#choices-before-implementation).

The following checks remain:

- `feature15` is pushed up to `10f87ea9`; CI run 45834660395 on
  `25238548` passed every job (Linux, sanitizer, Windows and macOS). The
  glow menu (4.91.0) and its plan update are committed locally, not
  pushed. PR #12 (`feature14`) does not
  contain that fix yet and stays red until it does. Try UI scale,
  right-button dragging and FXAA on Windows and macOS by hand.
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
