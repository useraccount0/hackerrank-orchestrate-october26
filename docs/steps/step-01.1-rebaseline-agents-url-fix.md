# Step 1.1: moving the baseline after the organizers fixed AGENTS.md

| | |
|---|---|
| Date | 2026-10-24 |
| Trigger | The organizers fixed the submission URL in AGENTS.md (their commit `0eddbbd` "Update AGENTS.md", merged into `main` as `acb7221`) |
| State | Done. The two changed items wait for your review like all the others |

## What changed in the input files

Exactly one line. AGENTS.md line 94 changed from

`https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists`

to

`https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists`

The other four root files did not change, and AGENTS.md still has 422 lines, so no line number
and no unit ID moved. This was checked with `git diff acb3dfc 0eddbbd`.

## What was done, step by step

1. **Found what changed.** `git diff` between the old baseline `acb3dfc` and the organizers'
   commit `0eddbbd` showed the one line above and nothing else.
2. **Moved the baseline.** This is the one decision in the procedure. In
   [requirements/sources.yml](../../requirements/sources.yml), `baseline_commit` is now
   `0eddbbd`. That is the organizers' own commit, not our merge commit, so the baseline is still
   "exactly the organizers' version". The old baseline is kept in a history comment.
3. **Let the tool find the damage before touching anything.** `srctrace.py check` failed with
   exactly three problems, all about line 94:
   - AGENTS.md has a new SHA-256;
   - unit SRC-AG0094 no longer matches the line;
   - AGENTS.md no longer rebuilds byte for byte.

   The new SHA-256 printed by the tool was confirmed independently with `git show` and
   `sha256sum`, then copied into `sources.yml`.
4. **Updated the source unit with a tool, not by hand.** Unit text is never typed by hand, so
   `srctrace.py` got a new command, `update`. It rewrites the text of units whose line changed in
   place. If lines were added, removed, or moved in a file, it refuses to touch that file and
   reports it, because unit IDs would shift. It also lists anything else that needs a human
   decision; here it found none. It reported `updated SRC-AG0094: text`. It saves through
   Doorstop's own API with git staging switched off. All three behaviours were tested on a
   throwaway copy of the repository (see "Tests of the new command").
5. **Let Doorstop find the affected requirement.** `srctrace.py check` passed again. Then
   `doorstop -F -W` reported exactly one warning: `CHR-836: suspect link: SRC-AG0094`. CHR-836
   is the only requirement built on line 94.
6. **Updated that requirement.** CHR-836 now states the `www` URL, and ISS-06 was removed from
   its open issues. `doorstop clear CHR-836` then confirmed that it was re-read against the new
   line. Doorstop staged the file while doing that, and it was unstaged again.
7. **Closed the issue.** ISS-06 is marked *resolved* in
   [requirements/ISSUES.md](../../requirements/ISSUES.md). It stays in the list as a record.
8. **Updated the documents that named the old commit.** [requirements/README.md](../../requirements/README.md),
   [docs/v-model.md](../v-model.md), and ISS-10 now refer to `sources.yml` instead of a fixed
   commit, so they will not need editing at the next baseline move. The README now describes the
   baseline-move procedure exactly as it was used here. The step 1 page got a short notice at
   the top and otherwise still describes step 1 as it was done.
9. **Regenerated the views**: `line_map.csv`, `SRC.md`, `CHR.md`, and the HTML version.

## Results

| Check | Result |
|---|---|
| `srctrace.py check` | PASS: 872 lines, 489 units, all 5 files rebuild byte for byte |
| `doorstop -F -W` | no warnings, no errors |
| Items waiting for your review | 605, unchanged (SRC-AG0094 and CHR-836 were already waiting) |
| Open issues | 9 (ISS-06 resolved) |
| Git | nothing committed, nothing staged |

## Tests of the new command

`srctrace.py update` was tested on a throwaway local clone of the repository; your working
copy was never touched. One test commit contained three kinds of change:

| Change in the test commit | What `update` did | As intended? |
|---|---|---|
| problem_statement.md line 126: one word changed | rewrote the text of SRC-PS0126 | yes |
| AGENTS.md line 1: the heading turned into plain text | rewrote the text of SRC-AG0001 and reported that its label (`heading`, set by rule) must be decided again | yes |
| README.md: a line inserted near the top | changed nothing in README.md (all 89 unit files identical) and reported that its units and links must be re-mapped by a person | yes |

It ended with an error code because decisions were needed, and it staged nothing.

## What this shows

The change tracking works as designed. One changed input line led the tool to name exactly
one unit, and Doorstop then named exactly one requirement. Nothing else had to be touched, and
nothing was guessed.

## What I need from you

- Review CHR-836 (and SRC-AG0094) when you reach them in your normal review.
- Commit when you are ready.

## Files changed in this step

| Path | Change | Done by |
|---|---|---|
| `requirements/sources.yml` | `baseline_commit` = `0eddbbd`, new SHA-256 of AGENTS.md, history comment | baseline decision; SHA-256 printed by the tool |
| `requirements/src/SRC-AG0094.yml` | text of line 94 | `srctrace.py update` |
| `requirements/chr/CHR-836.yml` | URL in the text, `issues` emptied, link fingerprint | AI edit; fingerprint by `doorstop clear` |
| `requirements/tools/srctrace.py` | new `update` command; `check` now prints the actual SHA-256 | AI |
| `requirements/ISSUES.md` | ISS-06 resolved; ISS-10 wording | AI |
| `requirements/README.md` | baseline-move procedure; no fixed commit in the diagram | AI |
| `docs/v-model.md` | commit reference; example of change tracking | AI |
| `docs/steps/step-01-requirements-baseline.md` | notice at the top | AI |
| `docs/steps/step-01.1-rebaseline-agents-url-fix.md` | new (this page) | AI |
| `requirements/views/*` | regenerated | `srctrace.py views`, `doorstop publish` |
| `log.txt` | new entry | AI |
