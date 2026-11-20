# 29 — Version numbers

[Roadmap](../../PLAN.md) · Request 2026-11-20 · **Done 2026-11-20: option A
was chosen and is in `AGENTS.md` §5. The first version under it is 4.20.0.**

**The first number stays 4. The second and third numbers get a rule that
does not depend on roadmap steps. Recommended: the second number counts
releases of something a user can see, the third counts everything else since
then.**

## What exists

| Thing | State |
| --- | --- |
| The rule | `AGENTS.md` §5: `4.X.Y`, "`X` bumps once per roadmap step, with the release that delivers the step's main user-visible change; everything else bumps `Y`". |
| What happened | `X` stood at 19 from 2026-11-18 while step 17 finished and step 21, 14d, 14e and 15i to 15l shipped: 44 versions named 4.19.x in three days, 126 version entries in twelve. New features, fixes and a license note all look alike in the number. The steps are not done in order and most have many slices, so "once per step" has no natural moment. |
| Where the number lives | `layer0/Version.h`: `_PyMOL_VERSION "4.19.43"` and `_PyMOL_VERSION_int 4019043` (`X.Y.Z` as `XYYYZZZ`, so the second and third numbers each go to 999). `get_version()` and session headers read it. |
| Who reads it | The release job tags `v<version>` at every push to `master` (so far `v4.19.11` and `v4.19.30`); the About box; `ChangeLog` has one entry per version. |

## Options (question 30, answered: A, with both smaller rules)

| | Option | Second number | Third number | Note |
| --- | --- | --- | --- | --- |
| A | **By what changed for the user. Recommended.** | +1 when a change ships that a user can see or use: a new or changed command, button, panel, menu, preset, file type, or a feature taken away. The third number goes back to 0. | +1 for every other change to the program: a fix, a speed-up, cleanup of the code, a dependency or build change. | The number says what kind of release it is: 4.20.0 has something new, 4.20.3 is 4.20.0 with three repairs. It follows from the commit type nearly always: `ui`, and a `remove` of something usable, move the second number; `fix`, `perf`, `simplify`, `deps` and a `remove` of dead code move the third. One feature slice of a plan (22a, 26b ...) is one step of the second number, however many commits it took. |
| B | By release. | +1 at the first change after a merge to `master`, so each second number is one downloadable release line. | +1 for every change on the branch. | Easy to apply (compare with the version on `origin/master`), and "4.21" names what a tester downloaded. But it says nothing about content, and it depends on when merges happen. |
| C | Keep the rule, and bump the second number for the steps that were skipped. | as today | as today | No change in habit; the problem that started the request stays. |

**With A, two smaller rules** (part of the same question):

| Rule | Recommended |
| --- | --- |
| A commit that changes nothing that ships (plans, docs, CI, tests only) | No version change and no `ChangeLog` entry. Today such commits sometimes take a number (4.19.43 is a license note). Fewer empty entries; the tag of a release is still unique because a release always contains at least one real change since the last. |
| A change of public `cmd.*` behavior that is called a fix | Second number, since scripts can see it; it is in `ChangeLog` either way (`AGENTS.md` §5). |
| Limits | 999 for each number (`XYYYZZZ`). At one step of the second number per feature slice, the open roadmap (about 45 slices) ends near 4.65. |
| The first number | Not touched by any rule. It changes when the user says so. |

## What changes when the rule is chosen

| File | Change |
| --- | --- |
| `AGENTS.md` §5 | The version bullet is rewritten with the chosen rule (four lines). |
| `PLAN.md` | "Working rules" names the rule; the open-work table needs no version column. |
| `layer0/Version.h` | Nothing at that moment. The next feature that ships is 4.20.0 under A. |
| `ChangeLog` | One line under the first entry that uses the new rule, saying from where it applies. Old entries stay as they are. |
| A check | `testing/tests/system/`: `_PyMOL_VERSION` and `_PyMOL_VERSION_int` agree, and the top `ChangeLog` entry names that version. If a test with this content exists already it is kept as it is. |

## Skipped

- Calendar versions (4.2611.x): do not fit the three digits of
  `_PyMOL_VERSION_int`, and sessions compare that number.
- Pre-release marks (`-rc1`, `.dev0`): every push to `master` is already a
  pre-release on GitHub.
- A version derived from `git describe`: the number is compiled into the
  core and written into sessions, so it must be in the source.
