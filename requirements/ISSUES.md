# Open issues found while converting the challenge files

While turning the five challenge files into requirements, some statements turned out to
disagree with each other, to be unclear, or to clash with facts in `dataset/`.
They are listed here instead of being silently "fixed" inside a requirement.

- Each issue names the exact source units (`SRC-…` = file and line, see [README.md](README.md))
  and the affected requirements (`CHR-…`). The affected requirements also carry the issue ID
  in their `issues` attribute.
- **Status** is `open` until you decide. The *proposal* is only a suggestion. A `resolved` issue
  stays in this list as a record of what happened.

| ID | Short title | Affects | Status |
|---|---|---|---|
| [ISS-01](#iss-01) | Where the evaluation reports go | CHR-607, CHR-608, CHR-609 | open |
| [ISS-02](#iss-02) | Remediation order: dependency or sorting? | CHR-329, CHR-416 | open |
| [ISS-03](#iss-03) | Sort `case_id` as text or as a number? | CHR-405 | open |
| [ISS-04](#iss-04) | "row" accuracy vs "step-level" accuracy | CHR-611 | open |
| [ISS-05](#iss-05) | `agent-trace.zip` is missing from the submission lists | CHR-601, CHR-901 | open |
| [ISS-06](#iss-06) | Submission URL starts with `wwww` | CHR-836 | resolved: the organizers fixed AGENTS.md |
| [ISS-07](#iss-07) | Unclear sentence about evidence in COMPLETE cases | CHR-435, CHR-436 | open |
| [ISS-08](#iss-08) | `python3` does not work on this Windows machine | CHR-512 | open |
| [ISS-09](#iss-09) | The lists of evidence formats differ | CHR-220 | open |
| [ISS-10](#iss-10) | `README.md` is both an input and a deliverable | CHR-606 | open |

---

## ISS-01

**Where the evaluation reports go**

- AGENTS.md and problem_statement.md say `code.zip` must include `evaluation/evaluation_report.md`
  and `evaluation/usage_report.md` (SRC-AG0331, SRC-AG0333, SRC-AG0338, SRC-AG0346, SRC-PS0133,
  SRC-PS0152, SRC-PS0154).
- README.md says `code/evaluation/evaluation_report.md` and `code/evaluation/usage_report.md`
  (SRC-RM0089, SRC-RM0091, SRC-RM0099, SRC-RM0145, SRC-RM0155). Its packaging commands zip
  `README.md` and `code/`, so inside the zip the reports sit at `code/evaluation/…`, not at
  `evaluation/…`. README.md also allows a top-level `evaluation/` folder if it is added to the
  zip command (SRC-RM0145).

**Why it matters:** a check that looks for `evaluation/…` at the top of the zip would not find
`code/evaluation/…`, and the other way round.

**Options:** (a) only `code/evaluation/` (README.md); (b) only a top-level `evaluation/`, added
to the zip command; (c) both places, identical copies.

**Proposal:** (a). The most recent organizer commit that touched this topic (`11576c9 docs: align
evaluation report paths with code.zip packaging in README`) points to README.md being the intended
reading. Option (c) is a cheap safety net.

## ISS-02

**Remediation order: dependency or sorting?**

- SRC-AG0303: "Within remediation, disable data flows and block unsafe restores before changing
  dependent records. Process downstream copies before their source records when the dependency
  requires it."
- SRC-PS0126 and SRC-RM0075: inside each phase, follow the operation order of the
  allowed-operations table, then sort by `system_id` and `resource_id` ascending.

The first sentence of SRC-AG0303 agrees with the table: `DISABLE_DATA_FLOW` and `BLOCK_RESTORE`
come first. The second sentence can clash with sorting: if a downstream copy's `system_id` sorts
*after* its source's `system_id`, sorting puts the source first.

**Options:** (a) always the sort order; (b) dependency order wins where a dependency exists;
(c) find out from the 32 sample answers which rule the official answers follow.

**Proposal:** (c), in a later step. `dataset/sample_output.csv` is the only evidence of what the
grader expects.

## ISS-03

**Sort `case_id` as text or as a number?**

- SRC-AG0237, SRC-PS0073, SRC-RM0075, SRC-RM0151: rows must be "sorted by `case_id`".
- Fact from `dataset/deletion_requests.csv`: the IDs run from `case_33` to `case_550` and have
  2 or 3 digits (no leading zeros). Sorted as text, `case_100` comes before `case_33`. Sorted as
  a number, `case_33` comes first. The input file itself is in number order. The sample IDs
  (`case_01` … `case_32`) sort the same way both ways, so the sample does not settle it.

**Options:** (a) text order; (b) number order (the same as the input file's order).

**Proposal:** no evidence yet; ask the organizers, or choose one and record the choice here.
If the grader matches rows by `case_id`, the order may not change the score, but the stated
rule still has to be met.

## ISS-04

**"row" accuracy vs "step-level" accuracy**

- SRC-RM0096: the evaluation report must cover "case, row, field, and sequence accuracy".
- SRC-AG0340, SRC-AG0341, SRC-AG0342, SRC-PS0135, SRC-PS0136, SRC-PS0137: "case-level status
  accuracy", "step-level and field-level accuracy", "sequence accuracy".

"row" most likely means one step (one element of `steps_json`), so it is the same as step-level.

**Proposal:** report case-level, step-level (= row-level), field-level, and sequence accuracy,
and use both names in the report.

## ISS-05

**`agent-trace.zip` is missing from the submission lists**

- agent_trace_instructions.md asks for `agent-trace.zip` "with your challenge submission"
  (SRC-AT0003, SRC-AT0013, SRC-AT0130).
- The submission tables list only `code.zip`, `output.csv`, `chat_transcript`, and the AI
  interview (SRC-AG0359 to SRC-AG0366, SRC-PS0145 to SRC-PS0148, SRC-RM0122 to SRC-RM0125).
  No file says where `agent-trace.zip` is uploaded.

**Proposal:** prepare `agent-trace.zip` anyway, and look for an upload slot on the submission
page.

## ISS-06

**Submission URL starts with `wwww`**

**Resolved (2026-10-24, step 1.1):** the organizers fixed the URL in commit `0eddbbd`
("Update AGENTS.md"). AGENTS.md line 94 now reads
`https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists`.
The baseline moved to that commit; SRC-AG0094 and CHR-836 were updated, and CHR-836 no longer
lists this issue. See [step 1.1](../docs/steps/step-01.1-rebaseline-agents-url-fix.md).
The text below is the original description.

- SRC-AG0094 (old baseline `acb3dfc`): `https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists`
  has four `w`s.
- AGENTS.md requires giving "this exact URL" (SRC-AG0096, SRC-AG0100 to SRC-AG0103).

It may be a typo for `www`, or deliberate.

**Proposal:** always give the URL exactly as written (that is the requirement, CHR-836/837), and
point out once that the host name looks unusual. No change unless the organizers correct it.

## ISS-07

**Unclear sentence about evidence in COMPLETE cases**

- SRC-PS0127: "Findings and verification steps for `COMPLETE` cases must cite a `file_id`,
  `activity_id`, or `audit_id`."
- But a COMPLETE case has no findings at all; it has only verification steps (SRC-PS0091,
  SRC-AG0258).
- AGENTS.md is clearer: every finding cites evidence (SRC-AG0313), and verification steps of a
  COMPLETE case cite evidence (SRC-AG0314).

**Reading used:** findings (which only occur in INCOMPLETE cases) cite evidence (CHR-435), and
verification steps of COMPLETE cases cite evidence (CHR-436).

**Proposal:** keep this reading.

## ISS-08

**`python3` does not work on this Windows machine**

- SRC-RM0036: run the starter with `python3 code/main.py`.
- On this Windows machine, `python3` starts the Microsoft Store shortcut instead of Python;
  `python` (Python 3.15.0) works.

**Proposal:** our README must give a command that works on Windows too (for example
`python code/main.py` or `py code/main.py`) next to `python3 code/main.py` for macOS/Linux.

## ISS-09

**The lists of evidence formats differ**

- SRC-PS0047 lists PDFs, images, logs, JSON, and SQL: no plain text.
- SRC-AG0202 and SRC-RM0059 also list plain text, and `dataset/evidence/records/` does contain a
  `.txt` file.

**Reading used:** the union of all lists, so plain text is included (CHR-220).

**Proposal:** keep this reading (only confirm).

## ISS-10

**`README.md` is both an input and a deliverable**

- README.md is one of the organizer files converted into requirements.
- The submission needs *our own* README.md with setup and run instructions (SRC-AG0326,
  SRC-RM0127), and the packaging commands zip the root README.md (SRC-RM0133, SRC-RM0139).

**Consequence (already handled):** the root README.md will be rewritten later. So the baseline
is read from git, at the commit recorded in [sources.yml](sources.yml), not from the working
tree, and the requirements stay traceable to the original text. Once README.md is edited, `srctrace.py check` will report
"CHANGED since the baseline" for it. That is expected, not an error.

**Decision needed later:** keep the organizers' README text somewhere (for example in `docs/`)
or replace it completely.
