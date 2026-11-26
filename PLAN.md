# pymolish-studio — current roadmap

Updated 2026-11-26 at **4.90.0**. Questions **128 A** and **129 A** are
recorded: add a viewport-only glow menu entry; keep Solid as the default
surface. This update changes plans only; the glow menu entry is not built.

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
| 3 | **15p follow-up** — [Glow in the light menu](docs/plans/15-presets.md#question-128-a-glow-menu-follow-up) | Apply answer 128 A: add "glow" / "no glow" beside fog in Presets > light, using the existing setting. Viewport only. | Both actions work by keyboard and Undo; scene/session checks pass; the viewport-only limit is documented. |
| 4 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend preset snapshots to add/remove/edit commands, retain the coordinate ring, finish toolbar labels and tests. Then remove the incentive error/mark and `-n`. | Existing undo/jira cases pass before removing the marks in `jira/PYMOL-1276.py` and `jira/PYMOL-1697.py`. |
| 5 | **38 rest** — [Documentation and demos](docs/plans/38-documentation.md) | Verify MP4 playback from GitHub posters after pushing; add a finished Chat turn picture/clip after order 2; complete the checklist's manual, platform and new-reader checks. | Clips play or fallback links are documented; the Chat picture is in `docs/assistant.md`; outstanding checks are recorded. |
| any time | **1b** — [Measured performance work](docs/plans/01-performance-gpu.md) | Profile surface triangulation and sticks/lines drawn as triangles on a quiet machine; driver comparisons also need Windows/macOS. | Each change has before/after measurements. |

The glow follow-up is the next local task. General undo and the remaining
documentation move from orders 3 and 4 to 4 and 5. Step 15 stays open until
the menu entry ships. Answer 129 needs no code change: Solid stays the
default and Solid (grid) remains optional.

## Waiting for the user

**No unanswered numbered questions.** [Answers 128 and 129](PLAN-DONE.md#decisions-128-and-129)
are recorded with the earlier decisions. The following checks remain:

- Push `feature15` (currently no upstream configured) and inspect Windows,
  macOS and sanitizer CI; try UI scale, right-button dragging and FXAA on
  those systems. No remote status was checked in this update.
- Complete the account and task trials for order 2; record commands,
  errors, time, tokens and the system used.
- Read the [documentation](docs/README.md), test the video posters after
  the push, and choose which faults listed in [plan 38](docs/plans/38-documentation.md)
  should become repair tasks.
- Review the recent presets, footer, surface and glow changes in your own
  window. The [detailed checklist](docs/plans/roadmap-checks.md) keeps the
  individual checks, CPK comparison and optional reference-picture cleanup.

## Working rules

- One implementation slice per session/PR; start from its linked plan.
- Follow [AGENTS.md](AGENTS.md) for versioning, checks and plan upkeep.
- Keep file formats, supported commands and plugin loading working; report
  checks that could not run. [Full completion criteria](docs/plans/roadmap-background.md#shared-completion-criteria).
- Deferred ideas stay outside the current work until requested. MAFFT stays
  separately installed; provider SDKs stay in the lazy `ai` extra; builds
  stay on GitHub Actions (5c remains shelved).
