# Step 1: from the challenge files to structured requirements

| | |
|---|---|
| Date | 2026-10-24 |
| State | Done, and approved by you on 2026-10-24 (see [step 1.2](step-01.2-review.md)) |
| Goal | Turn every line of the challenge files in the repository root into traceable requirements, with no line skipped, and make the result checkable by tools |
| Not in this step | Solution code, `output.csv`, and requirements that go beyond the hackathon (that is step 2) |

> **Later change:** after this step, the organizers fixed the submission URL in AGENTS.md. The
> baseline moved to their commit `0eddbbd`, and ISS-06 is resolved; you decided the other 9
> issues in step 1.2.
> See [step 1.1](step-01.1-rebaseline-agents-url-fix.md). This page still describes step 1 as it
> was done.

## Results in numbers

| What | Count |
|---|---|
| Input files | 5: AGENTS.md, CLAUDE.md, README.md, agent_trace_instructions.md, problem_statement.md |
| Input lines | 872 (602 non-blank, 270 blank) |
| Source units (SRC) | 489: requirement 373, heading 61, formatting 39, context 5, not-applicable 11 |
| Challenge requirements (CHR) | 202, in 9 sections (plus 9 section titles) |
| Links from requirements to source units | 620; all 373 requirement units are covered |
| By party | system 104, participant 51, coding agent 38, organizer 9 |
| By modality | shall 164, fact 33, should 4, may 1 |
| Open issues | 10 (see [requirements/ISSUES.md](../../requirements/ISSUES.md)) |
| Items waiting for your review | 605 (394 source-unit classifications + 211 CHR items) |

## Who did what: tools or AI

You asked that anything repeatable is done by an open-source tool instead of AI. This is how
the work was split:

| Task | Done by | Gives the same result when repeated? |
|---|---|---|
| Freeze the input files (git commit, SHA-256 per file) | git, sha256 | yes |
| Cut the files into source units | `srctrace.py split` (one fixed rule) | yes |
| Label headings, `---`, and table header and delimiter rows (95 units) | fixed rules in `srctrace.py` | yes |
| Label the other 394 units (requirement, context, ...) | **AI**, waiting for your review | no, this is judgment |
| Write the 202 requirements and choose their links | **AI**, waiting for your review | no, this is judgment |
| Create the item files | `doorstop import` | yes |
| Check links and coverage | Doorstop validation | yes |
| Prove that every line is covered, verbatim | `srctrace.py check` | yes |
| Produce the readable views and the traceability matrix | `srctrace.py views`, `doorstop publish` | yes |

## What was done, step by step

### 1. Defined the inputs

"Input files in the root" = the five files tracked by git in the repository root at commit
`acb3dfc` (872 lines in total). Not included, and why:

- `dataset/`: data that the solution reads, not instructions. Its file names, columns, and
  meanings *are* covered, because the root files describe them. Whether the content of
  `dataset/deletion_rules.csv` should also become requirements is a question for step 2.
- `code/main.py` and `code/evaluation/main.py`: starter files that are empty (0 lines).
- `log.txt`: written by the coding agent during this session, not an input.

### 2. Chose the tools

- **Doorstop 3.2** (open source) stores the requirements: one YAML file per item, links between
  items, review fingerprints, validation, and publishing (Markdown, HTML, traceability matrix).
- No existing tool proves that *every line* of a Markdown file is covered, so one small script was
  written for that: [requirements/tools/srctrace.py](../../requirements/tools/srctrace.py). It is
  the only code written in this step. It is not solution code.
- The tools run in their own environment `.venv-req/` (not in git). The exact versions are in
  [requirements/tools/pip-requirements.txt](../../requirements/tools/pip-requirements.txt).
- Two workarounds were needed for Python 3.15, both documented in
  [requirements/README.md](../../requirements/README.md#setup-once).
- Before choosing, a trial run in a temporary folder confirmed every Doorstop feature this design
  relies on.

### 3. Froze the baseline

[requirements/sources.yml](../../requirements/sources.yml) records the git commit, a 2-letter code
per file, the line count, and the SHA-256 of each file. The tools always read the files **from
git at that commit**, not from the working folder. Reason: our own README.md will replace the
organizers' README.md later (see ISS-10), and the organizers may update their files. The baseline
must never change silently.

### 4. Cut the files into source units (tool)

`srctrace.py split` applies one rule: a fenced code block is one unit, every other non-blank line
is one unit, and blank lines are no unit. Each unit's ID contains the file code and its first line
number, for example `SRC-PS0126` = problem_statement.md line 126. Result: 489 units.

### 5. Labelled every unit (95 by rule, 394 by AI)

- By rule: 56 Markdown headings, 39 formatting lines (`---`, table header and delimiter rows).
- By AI: each of the other 394 units was read and labelled. Default: `requirement` (372 units).
  The AI made exactly these 21 exceptions and 1 override. Each reason is stored in the unit's
  `note`:

| Units | Label | Reason |
|---|---|---|
| SRC-AG0003, SRC-AG0027 | context | Title line; "this is a starter repo" |
| SRC-RM0017, SRC-RM0019 | context | Clone instructions (already done) |
| SRC-PS0003 | context | The Northstar Shop story; the facts that matter are repeated in normative lines |
| SRC-AG0056, SRC-AG0098, SRC-AG0234 | heading | Labels "Rules:" and "Requirements:" |
| SRC-RM0131, SRC-RM0137 | heading | Labels "macOS / Linux:" and "Windows (PowerShell):" |
| SRC-AG0378 to SRC-AG0394 (11 units) | not-applicable | AGENTS.md §7 is for the organizers who generate the dataset |
| SRC-AG0161 | requirement (rule said heading) | The heading "What Not To Log" carries the obligation; its list items have no verb |

### 6. Wrote the challenge requirements (AI)

202 requirements in 9 sections: purpose, inputs, audit logic, output file, solution constraints,
deliverables, evaluation, development process, and agent trace. Writing rules that were followed:

- One statement per requirement, worded as close to the source as possible, with **nothing
  added** that the sources do not say. Where the wording had to interpret something (for example
  the JSON types in CHR-412), the requirement has a `note`.
- When several files say the same thing (very often README.md, AGENTS.md, and
  problem_statement.md), there is one requirement that links to all of them.
- Every requirement has a `party` (who must do it), a `kind`, a `modality` (shall, should, may,
  fact), and a planned `verification` method for the right side of the V.
- Statements for other AI tools (Codex, Antigravity, OpenCode, and others) became conditional
  requirements ("if X was used, …"), because you might still use those tools.

### 7. Recorded conflicts instead of hiding them

10 issues, for example: the evaluation reports' folder differs between README.md and the other
files (ISS-01), the remediation order rules can clash (ISS-02), and "sort by `case_id`" is
ambiguous because the IDs have no leading zeros (ISS-03). All are in
[requirements/ISSUES.md](../../requirements/ISSUES.md). The affected requirements carry the issue
ID.

### 8. Imported, validated, verified

- Both documents were created by Doorstop's own `doorstop import`.
- Doorstop validation: **no** coverage problem. There are no `no links from child document`
  warnings (every requirement line has a requirement), no `no links to parent document` warnings
  (every requirement has a source), and no links to non-requirement lines. The only messages are
  the 605 `unreviewed changes`, on purpose.
- `srctrace.py check`: **PASS**. For each of the 5 files, rebuilding the file only from its source
  units gives the original bytes exactly.
- The checker was also tested against deliberately broken copies (one changed character, one
  deleted unit, a wrong label, a tampered rule label). It caught all four.

### 9. Generated the views

[requirements/views/line_map.csv](../../requirements/views/line_map.csv) (all 872 lines →
unit → requirements), [requirements/views/SRC.md](../../requirements/views/SRC.md), and
[requirements/views/CHR.md](../../requirements/views/CHR.md). An HTML version with a
traceability matrix can be built with one command (see the README).

### 10. Housekeeping

- Added `.gitignore` for `.venv*/`, `__pycache__/`, `.env`, and `requirements/_build/`.
- Doorstop runs `git add` on files it saves. During the first validation it staged the 700 item
  files. They were unstaged again (`git reset`), so your git index is exactly as it was before.
  The routine checks now use `doorstop -F`, which saves nothing. **Nothing was committed.**
- `log.txt` was created and is appended to, as AGENTS.md requires.

## How to check everything yourself

From the repository root in PowerShell (one-time setup:
[requirements/README.md](../../requirements/README.md#setup-once)):

```powershell
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with: RESULT: PASS
.venv-req\Scripts\doorstop -F -W                                 # must show no WARNING/ERROR lines
.venv-req\Scripts\doorstop -F                                    # lists what you have not reviewed yet
```

Spot checks you can do by hand:

- Pick any line in a root file → find it in `requirements/views/line_map.csv` → follow the
  `chr_uids` into `requirements/views/CHR.md`.
- Pick any requirement in `CHR.md` → follow its *Parent links* → open the file at that line.

## What I need from you

1. **Review** the requirements, at your own pace. The order that makes sense: sections 3 and 4
   of [CHR.md](../../requirements/views/CHR.md) (they define the solution), then the rest, then
   the 22 AI labelling decisions above (21 exceptions and 1 override). Mark what you accept with `doorstop review <ID>` (or
   `doorstop review CHR` for a whole document). Change anything you disagree with, or tell me
   and I will change it.
2. **Decide** the 10 issues in [ISSUES.md](../../requirements/ISSUES.md). The ones that
   influence the solution most are ISS-01, ISS-02, and ISS-03.
3. **Confirm the tooling**: Doorstop plus the one small checker. If you prefer a different tool,
   now is the cheapest moment to switch.
4. **Scope for step 2**: should the content of `dataset/deletion_rules.csv` (15 policy rules) and
   the CSV column lists be added to the source baseline as well?
5. **Git**: nothing is committed. Tell me if you want a commit (and on which branch).

## Next step (preview, not started)

Step 2: requirements beyond what the hackathon gives, kept apart in their own document (`EXT`) and
traced to your own words or to a written rationale. The plan is in
[docs/v-model.md](../v-model.md#keeping-beyond-the-hackathon-requirements-apart-step-2).

## Files created or changed in this step

| Path | Change |
|---|---|
| `.gitignore` | new |
| `log.txt` | new (session log required by AGENTS.md) |
| `requirements/` | new: README.md, ISSUES.md, sources.yml, `src/` (489 items + config), `chr/` (211 items + config), `tools/`, `views/` |
| `docs/v-model.md`, `docs/steps/step-01-requirements-baseline.md` | new |
| `.venv-req/`, `requirements/_build/` | local only, ignored by git |
| Challenge files, `dataset/`, `code/` | unchanged |
