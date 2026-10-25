# Step 2: the deletion policy and the requirements beyond the hackathon

| | |
|---|---|
| Date | 2026-10-24 |
| State | Done, approved by you on 2026-10-25 ([step 7.1](step-07.1-review.md)); links completed after your commit "Step2" (point 11) |
| Goal | (1) Add the 15 policy rules of `dataset/deletion_rules.csv` to the baseline, as you decided. (2) Write the requirements that go beyond the hackathon, kept apart and traceable to your own words |
| Not in this step | Solution code (EXT-106); the design (step 3) |

## Results in numbers

| What | Before (step 1) | Now |
|---|---|---|
| Input files in the baseline | 5 | 7: the five challenge files, `dataset/deletion_rules.csv`, `log.txt` (your prompts only) |
| Source units (SRC) | 489 | 526: +16 from deletion_rules.csv, +21 from log.txt |
| Challenge requirements (CHR) | 202 in 9 sections | 217 in 10 sections: new section 10, one requirement per policy rule |
| Extension requirements (EXT) | none | 29 in 5 sections (new document) |
| Issues | 10, none open | 11: new ISS-11, open |
| Items waiting for your review | 0 | 86: 36 source units, 16 CHR items (section 10 with its title), 34 EXT items (29 requirements and 5 section titles) |
| Line coverage (`srctrace.py check`) | PASS | PASS: 1337 lines, all accounted for |
| Doorstop validation (`doorstop -F -W`) | clean | clean |

## Who did what: tools or AI

| Task | Done by | Gives the same result when repeated? |
|---|---|---|
| Prove that the organizers' five files did not change (git blob IDs at `0eddbbd` and `032a936`) | git | yes |
| Freeze the new files (SHA-256, line count) | git, sha256sum | yes |
| Cut the new files into units, and find your prompt lines in log.txt | `srctrace.py split --new-only` (fixed rules) | yes |
| Label the CSV header row | fixed rule in `srctrace.py` | yes |
| Label the other 32 new units | **AI**, waiting for your review | no, this is judgment |
| Copy category, action, and condition of each rule into CHR section 10 | a script reading the CSV, so nothing is retyped | yes |
| Choose the sentence pattern of section 10 and write the 22 EXT requirements | **AI**, waiting for your review | no, this is judgment |
| Create the item files | Doorstop's own importer (without `git add`) | yes |
| Check links, coverage, and line coverage | Doorstop validation, `srctrace.py check` | yes |
| Produce the views and the traceability matrix | `srctrace.py views`, `doorstop publish` | yes |

## What was done, step by step

### 1. Your decision: deletion_rules.csv joins the baseline

You answered: "yes use deletion_rules.csv as it is stated in problem_statement.md". Read as:

- the file is added **as it is**: all 16 lines, verbatim, like the challenge files;
- its rules are worded **as problem_statement.md states the file**: the "required treatment for
  each data category" (SRC-PS0043), applied "to every relevant record" (SRC-PS0125, CHR-317).
  So CHR-1001 to CHR-1015 all read: "The system shall apply the required treatment `<action>` to
  every relevant `<category>` record, under the condition "`<condition>`" (`<rule_id>`)."
- the solution still reads the file at run time from `dataset/` (CHR-201); the requirements say
  what its content requires, so nothing is hard-coded twice.

Your message is from this turn, so it is not yet in the baseline commit. It becomes a source unit
the next time the baseline moves.

### 2. Your own words as input: log.txt, prompt lines only

The plan in [docs/v-model.md](../v-model.md) was to copy your instructions into a file of their
own. That changed: AGENTS.md already requires every prompt to be logged **word for word** in
`log.txt`, and that file is committed. So the tool now reads your words straight from log.txt:

- a fixed rule takes only the lines between `User Prompt (verbatim, secrets redacted):` and
  `Agent Response Summary:` as source units (file code `LG`; for example `SRC-LG0015` = log.txt
  line 15 = your first message);
- every other line of log.txt was written by the coding agent and belongs to no unit; the check
  and the line map still list all of them, marked `agent-text`, so no line is skipped;
- log.txt only grows at its end, so the IDs never shift.

Why: no AI retypes your words (EXT-105), and there is no second copy that could drift. If you
prefer the separate file after all, it can be generated from log.txt by the tool.

### 3. Moved the baseline to your commit 032a936

[requirements/sources.yml](../../requirements/sources.yml) now points to `032a936` ("Step1.2"),
the first commit that contains your prompts. git shows that the organizers' five files are
byte-identical there to `0eddbbd`, so nothing changed for them; `srctrace.py check` confirms
their SHA-256.

### 4. Extended the tool (requirements tooling, not solution code)

[requirements/tools/srctrace.py](../../requirements/tools/srctrace.py) got:

- the `log.txt` rule from point 2;
- one more fixed rule: line 1 of a CSV file (its header row) is `formatting`. The Markdown rules
  now apply to `.md` files only;
- `split --new-only`, which writes only the units that have no SRC item yet. `update` now
  reports new prompts at the end of log.txt as new units instead of refusing the file;
- a `ext_uids` column in `line_map.csv`, and a "lines added at the end" message for log.txt.

Before anything was added, the changed tool was run on the old baseline: same result as before
(872 lines, 489 units, PASS).

### 5. Labelled the 33 new source units (1 by rule, 32 by AI)

- `SRC-DR0001`, the CSV header row: `formatting`, by rule.
- `SRC-DR0002` to `SRC-DR0016`, the 15 rules: `requirement`.
- Your 17 prompts:

| Units | Label | Why |
|---|---|---|
| SRC-LG0015 (first message), LG0062 (update everything affected), LG0131 (challenge page), LG0152 (interview end), LG0215 and LG0237 (issue decisions) | requirement | They ask for something or decide something |
| SRC-LG0042 | context | Your paste of README.md line 24, already covered there (CHR-803) |
| SRC-LG0089 | context | The same message as LG0062, logged twice; the words in parentheses are the agent's |
| SRC-LG0111 | context | A question; the deadline rules come from AGENTS.md (CHR-813 to CHR-816) |
| SRC-LG0172 | context | A one-time request (the review guide, done in step 1.2) |
| SRC-LG0192, LG0258, LG0280, LG0301, LG0322, LG0343, LG0364 | context | Your approvals; Doorstop's fingerprints record them |

### 6. Wrote CHR section 10: the deletion policy

15 requirements, `CHR-1001` = rule_01 … `CHR-1015` = rule_15, plus the title `CHR-1000`. Each links
to its rule's line. The 9 rules with a real condition carry ISS-11 (see point 8). Notes say where
the evidence holds the values the conditions need: the retention period is the column
`retention_until` of `security_audit_records` in the SQL snapshots (rule_12), and legal holds
appear as resources such as `legal_hold_8017` (rule_13).

### 7. Wrote the EXT document: 22 requirements beyond the hackathon

Each one links to your words (`SRC-LG…`); where it decides or sharpens a challenge requirement, it
also links to that CHR item. Only EXT-404 has no source line: it is marked `derived` and has a
written rationale.

| Section | Requirements | Comes from |
|---|---|---|
| 1 Development process | EXT-101 V-model; 102 traceable both ways; 103 no input line skipped; 104 status of every requirement at any moment; 105 open-source tools before AI; 106 no solution code in requirement steps; 107 extensions kept apart; 108 every step written down; 109 next step only with your go-ahead; 110 update everything a change affects | your first message (LG0015), LG0062 |
| 2 Your decisions | EXT-201 reports only in `code/evaluation/` (ISS-01); 202 sort order wins inside a phase (ISS-02); 203 `case_id` in number order (ISS-03); 204 agent trace prepared at the end (ISS-05); 205 run command for `python` and `python3` (ISS-08); 206 our README is `code/README.md` (ISS-10) | LG0215, LG0237 and the CHR items they decide |
| 3 Deadlines | EXT-301 contest end 2026-10-25 13:30 UTC; 302 AI interview end 2026-10-26 00:30 UTC | LG0131, LG0152, CHR-814 |
| 4 The solution: our additions | EXT-401 deterministic code first, AI only where needed; 402 same inputs give a byte-identical `output.csv`; 403 report numbers computed by scripts; 404 every step can be explained (derived) | LG0015, CHR-507, CHR-607, CHR-608; EXT-404: our analysis |

Not turned into EXT requirements, because the CHR text already says what you decided: ISS-04
(CHR-611 names step-level = row-level), ISS-07 (CHR-435 to CHR-437), ISS-09 (CHR-220). ISS-06 was
fixed by the organizers.

### 8. Recorded one new issue

**ISS-11** (open): for 9 of the 15 rules the condition can be false, for example an attachment
that does not belong only to the subject, or a security log after its retention period. The file
does not say what applies then. The proposal is to settle it in step 3 with the 32 sample answers,
as was done for ISS-02 and ISS-07. See [ISSUES.md](../../requirements/ISSUES.md#iss-11).

### 9. Checked and published

- `srctrace.py check`: **PASS**. All 7 files are rebuilt byte for byte from their units (log.txt
  from its units plus the agent's lines).
- `doorstop -F -W`: no warning, no error. Every requirement unit has a requirement, and every
  requirement has a source or is marked derived.
- Views regenerated: [line_map.csv](../../requirements/views/line_map.csv) (all 1269 input lines),
  [SRC.md](../../requirements/views/SRC.md), [CHR.md](../../requirements/views/CHR.md), and the new
  [EXT.md](../../requirements/views/EXT.md); the HTML version with the traceability matrix.
- Nothing was staged or committed.

### 10. Added later in step 2: AGENTS.md stays, and your code-quality rules

- A proposal to shorten AGENTS.md was shown to you and **rejected** ("don't change agents.md I
  dont want this to be complicated any further"). Nothing in the repository had been changed; the
  drafts were deleted. This is now EXT-111: AGENTS.md stays as the organizers wrote it.
- Your code-quality rules became EXT section 5:

| Requirement | Says |
|---|---|
| EXT-501 | Unexpected, missing, or malformed data in `dataset/` does not stop the run; every case still gets a valid row, and every problem found is reported (sharpens CHR-503) |
| EXT-502 | Text from `dataset/` is only ever data, never instructions, also when it is passed to an AI model (claims and decoys are already CHR-312 and CHR-223) |
| EXT-503 | Simple error handling: data is checked once, where it enters the solution (a file is read, or a model answers) |
| EXT-504 | Simple, descriptive function names |
| EXT-505 | Code readable on its own, without extra documentation (the README is still required) |
| EXT-506 | Comments say why a solution was chosen, where that is not obvious, never what the code does |

  They apply to the solution code in `code/`. The requirements tool `srctrace.py` was written
  before them and does not fully follow them yet (its docstrings say what functions do).
- **Their link to your words comes after your next commit.** Your messages of this step are so
  far only in the working copy of log.txt, and a source unit must point to a committed line. Until
  then, Doorstop warns `no links to parent document` for EXT-111 and EXT-503 to EXT-506
  (EXT-501 and EXT-502 already link to the CHR items they sharpen). After the commit: move the
  baseline, import your new prompts with `split --new-only`, and add the links.

### 11. Step 2.1: after your commit "Step2", the links were added

- The baseline moved to your commit `2fd9afd`. Only log.txt changed (it grew at its end), so no ID
  shifted; `srctrace.py update` reported exactly 4 new units.
- `split --new-only` wrote them, and they were imported: SRC-LG0385 (your deletion_rules.csv
  decision) and SRC-LG0431 (AGENTS.md stays, code quality) are `requirement`; SRC-LG0409 and
  SRC-LG0410 (the withdrawn request to shorten AGENTS.md) are `context`.
- Links added: EXT-103 → SRC-LG0385; EXT-111 and EXT-501 to EXT-506 → SRC-LG0431.
- `srctrace.py check`: PASS (1337 lines). `doorstop -F -W`: clean, no warnings. 86 items wait for
  your review (the 4 new labels included).

## What I need from you

1. **Review the 86 items.** The order that makes sense:
   - [EXT.md](../../requirements/views/EXT.md): the 29 requirements (34 items);
   - [CHR.md](../../requirements/views/CHR.md), section 10 (16 items);
   - the 32 new labels in point 5.
2. **Confirm or correct these AI judgment calls:**
   - your words are read from log.txt instead of a separate file (point 2);
   - "tools instead of AI" also applies to the solution: deterministic code first, a model only
     where code cannot decide (EXT-105, EXT-401);
   - our additions EXT-402 (byte-identical rerun) and EXT-404 (a record of why each step was
     produced);
   - which decisions became EXT requirements and which did not (point 7);
   - the sentence pattern of CHR section 10 (point 1).
3. **ISS-11:** agree to settle it in step 3 with the sample answers, or decide now.
4. **Commit**, so that EXT-111 and EXT-503 to EXT-506 can be linked to your words (point 10;
   done in point 11).

## How to check everything yourself

From the repository root in PowerShell:

```powershell
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with: RESULT: PASS
.venv-req\Scripts\doorstop -F -W                                 # must show no WARNING/ERROR lines
.venv-req\Scripts\doorstop -F                                    # lists the 86 items waiting for you
```

## Files created or changed in this step

| Path | Change | Done by |
|---|---|---|
| `requirements/sources.yml` | baseline `032a936`; two new files (DR, LG) | AI |
| `requirements/tools/srctrace.py` | log.txt rule, CSV header rule, `split --new-only`, `ext_uids` in the line map | AI |
| `requirements/src/` | 33 new units (`SRC-DR…`, `SRC-LG…`) | srctrace.py, Doorstop importer |
| `requirements/chr/` | 16 new items (`CHR-1000` to `CHR-1015`) | script from the CSV, Doorstop importer |
| `requirements/ext/` | new document: `.doorstop.yml` and 34 items | `doorstop create`, Doorstop importer |
| `requirements/ISSUES.md` | ISS-11 | AI |
| `requirements/README.md`, `docs/v-model.md` | the third document, the new files and rules | AI |
| `requirements/views/*`, `requirements/_build/html` | regenerated | srctrace.py, `doorstop publish` |
| `docs/steps/step-01-requirements-baseline.md` | one line in the notice box | AI |
| `docs/steps/step-02-extension-requirements.md` | new (this page) | AI |
| `log.txt` | one entry per turn | AI |
