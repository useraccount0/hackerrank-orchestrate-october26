# Step 1.2: your review of step 1 (done)

| | |
|---|---|
| Date | 2026-10-24 |
| Order | Part 1: AI labelling decisions; Part 2: open issues; Part 3: requirements; bulk approval of the source lines; Part 4: tools and process |
| Result | **Step 1 is approved.** All parts are done |
| Items waiting for your review | 0 (was 605) |

## Result in one table

| What | State |
|---|---|
| Source units (SRC) | 489: 95 stamped by Doorstop because a fixed rule labelled them, 394 approved by you |
| Requirements (CHR) | 211 items (202 requirements + 9 section titles), all approved by you |
| Issues | 9 decided by you, 1 resolved by the organizers (ISS-06); 0 open |
| Line coverage (`srctrace.py check`) | PASS: all 872 lines of the 5 files, rebuilt byte for byte |
| Doorstop, full validation including review status (`doorstop -F`) | 0 warnings, 0 errors |
| First verification (`log.txt` against CHR-820 to CHR-835) | everything met, except CHR-827 in 2 older entries (append-only, cannot be fixed) |

The checks the tools already proved are not part of this review: line coverage, links, the
95 rule-labelled units, and the generated views.

## Part 1: the 22 AI labelling decisions (approved)

- You approved all 22 on 2026-10-24 ("part 1 ok"). The list is in
  [step 1, section 5](step-01-requirements-baseline.md#5-labelled-every-unit-95-by-rule-394-by-ai).
- Recorded with Doorstop's own command, `doorstop review <ID>`, once for each of the 22 units:
  SRC-AG0003, SRC-AG0027, SRC-AG0056, SRC-AG0098, SRC-AG0161, SRC-AG0234, SRC-AG0378,
  SRC-AG0380 to SRC-AG0387, SRC-AG0389, SRC-AG0394, SRC-PS0003, SRC-RM0017, SRC-RM0019,
  SRC-RM0131, SRC-RM0137.
- Each unit's `reviewed` field now holds Doorstop's fingerprint instead of
  `pending-user-review`. If one of these units changes later, Doorstop reports it as unreviewed
  again.
- Doorstop staged the 22 files while saving them. They were unstaged again, so you commit as usual.

## Part 2: the open issues (done: all 9 decided)

Your decisions of 2026-10-24, recorded in [ISSUES.md](../../requirements/ISSUES.md) and copied
into the `note` of each affected requirement (written through Doorstop's API, nothing staged):

| Issue | Decision | Requirements noted | Consequence |
|---|---|---|---|
| ISS-01 | (a) the reports go in `code/evaluation/` | CHR-607, CHR-608, CHR-609 | none beyond the decision |
| ISS-02 | (a) always the sort order | CHR-329, CHR-416 | where "downstream first" conflicts with sorting, sorting wins |
| ISS-03 | (b) number order, which equals the input file's order (checked: 518 unique `case_<number>` IDs) | CHR-405 | none beyond the decision |
| ISS-04 | "row" accuracy = step-level accuracy; the report names both | CHR-611 | none beyond the decision |
| ISS-05 | (revised) at the end, the agent trace is prepared as `agent-trace.zip` exactly as agent_trace_instructions.md describes; `log.txt` stays the `chat_transcript` | CHR-601, CHR-901 | CHR-901 to CHR-916 apply; the upload place is checked at the end |
| ISS-07 | reading confirmed | CHR-435, CHR-436 | none beyond the decision |
| ISS-08 | use `python` as is on this machine for now; `code/README.md` shows both commands | CHR-512 | none beyond the decision |
| ISS-09 | union of the lists (plain text included) | CHR-220 | none beyond the decision |
| ISS-10 | keep the organizers' README; ours is `code/README.md` | CHR-606, CHR-627 | the zip command would pack both READMEs; decide at packaging time |

ISS-05 was first decided as "the trace is `log.txt`, no `agent-trace.zip`" and then revised the
same day. Both versions stay visible in ISSUES.md.

### Evidence gathered before the decisions

Before asking you to decide, the 32 official sample answers (`dataset/sample_output.csv`) were
checked read-only for the two issues they can answer. The results are stored in
[ISSUES.md](../../requirements/ISSUES.md):

- **ISS-02:** all 51 multi-step phase blocks follow the sort rule, and two samples put a source
  before its downstream copy. The proposal changed from "find out" to (a), the sort order.
- **ISS-07:** the samples confirm the reading used in CHR-435, CHR-436, and CHR-437.
- **ISS-03:** the samples cannot settle it, because their IDs all have two digits.

## Part 3: the requirements (done)

Each section is presented in the chat with its source lines; the AI's own judgment calls are
flagged. An approval is recorded with Doorstop's `review()`, saved without staging.

| Section | Requirements | State |
|---|---|---|
| 3 Deletion audit logic | CHR-301 to CHR-331 (31) and the title CHR-300 | approved 2026-10-24 ("section 3 ok"), with all four flagged judgment calls kept as written |
| 4 Output file | CHR-401 to CHR-439 (39) and the title CHR-400 | approved 2026-10-24 ("section 4 ok"); its two judgment calls (CHR-412 field types, CHR-418 to CHR-432 fixed phase and state) were confirmed by the 32 sample answers first, with the evidence added to the notes of CHR-412 and CHR-417 |
| 5 Solution constraints, 6 Submission deliverables | CHR-501 to CHR-513 (13), CHR-601 to CHR-629 (29), and the titles CHR-500, CHR-600 | approved 2026-10-24 ("sections 5 and 6 ok"); CHR-513 got the ISS-10 note first (it also names "the submitted README.md") |
| 1 Purpose and scope, 2 Inputs, 7 Evaluation | CHR-101 to CHR-103 (3), CHR-201 to CHR-223 (23), CHR-701 to CHR-708 (8), and the titles CHR-100, CHR-200, CHR-700 | approved 2026-10-24 ("sections 1 2 and 7 ok"); all 23 facts of section 2 were first checked against the files in `dataset/` (all match) |
| 8 Development process, 9 Agent trace | CHR-801 to CHR-840 (40), CHR-901 to CHR-916 (16), and the titles CHR-800, CHR-900 | approved 2026-10-24 ("sections 8 and 9 ok"); `log.txt` was first checked against the logging rules (see below) |

### First verification: `log.txt` against the logging rules (CHR-820 to CHR-835)

Before section 8 was presented, `log.txt` was checked read-only with a script (15 entries at that
time). The script checked the heading format, titles of at most 80 characters, the fields of the
SESSION START entry, the four sections of each per-turn entry, exactly one `tool=Claude Code` and
one `model=claude-opus-5-5` line per entry, UTF-8 without CR bytes, time order, and that the file
only grew since the last commit (append-only).

- **Passed:** everything, except one rule.
- **Not met:** CHR-827, the 2 to 5 sentence summary. Two earlier entries ("Review part 1
  approved…" and "Review part 2 completed…") have 6 sentences. They cannot be fixed because the
  log is append-only (CHR-823). From now on, each new entry is checked before the turn ends.

## Bulk approval of the source lines (done)

- The 372 source units still waiting were all labelled `requirement`, and each was checked to be
  linked from at least one requirement you had approved. You had therefore seen every one through
  Part 3.
- You approved them on 2026-10-24 ("source lines ok"). This was recorded with Doorstop's
  `review()`, saved without staging.

## Part 4: tools and process (done)

You read the tooling and process documents and approved them on 2026-10-24 ("part 4 ok"):

- [requirements/README.md](../../requirements/README.md): how the requirements work (IDs,
  attributes, commands, review, the baseline-move procedure);
- [docs/v-model.md](../v-model.md): the V-model plan, the status questions, and the **step 2
  plan**: your own instructions go into a source file of their own, and the extension
  requirements go into a separate `EXT` document;
- the step records in [docs/steps/](.): step 1, step 1.1, and this page;
- the tooling: Doorstop 3.2 plus `requirements/tools/srctrace.py`, pinned versions in
  `.venv-req`, and the two Python 3.15 workarounds.

So the tooling stays as it is, and step 2 follows the plan in docs/v-model.md.

## Files changed in this step

| Path | Change | Done by |
|---|---|---|
| `requirements/src/` (394 unit files) | `reviewed` fingerprint (22 in Part 1, 372 in bulk) | `doorstop review` (Part 1), Doorstop's `review()` (bulk) |
| `requirements/chr/` (all 211 items) | `reviewed` fingerprint | Doorstop's `review()` |
| `requirements/chr/` (18 items: CHR-220, CHR-329, CHR-405, CHR-412, CHR-416, CHR-417, CHR-435, CHR-436, CHR-512, CHR-513, CHR-601, CHR-606 to CHR-609, CHR-611, CHR-627, CHR-901) | decision and evidence notes; `issues` of CHR-513 and CHR-627 | Doorstop API (scratch scripts) |
| `requirements/ISSUES.md` | evidence for ISS-02 and ISS-07; decisions on all 9 open issues (ISS-05 revised once); answer to the ISS-08 question | AI |
| `requirements/README.md` | meaning of the `issues` attribute | AI |
| `requirements/views/CHR.md`, `requirements/_build/html/` | regenerated | `doorstop publish` |
| `docs/steps/step-01-requirements-baseline.md` | state row: approved | AI |
| `docs/steps/step-01.2-review.md` | new (this page) | AI |
| `log.txt` | one entry per turn | AI |
