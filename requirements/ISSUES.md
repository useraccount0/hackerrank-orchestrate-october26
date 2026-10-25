# Open issues found while converting the challenge files

While turning the input files into requirements, some statements turned out to
disagree with each other, to be unclear, or to clash with facts in `dataset/`.
They are listed here instead of being silently "fixed" inside a requirement.

- Each issue names the exact source units (`SRC-…` = file and line, see [README.md](README.md))
  and the affected requirements (`CHR-…`). The affected requirements also carry the issue ID
  in their `issues` attribute.
- **Status:** `open` means waiting for your decision; the *proposal* is only a suggestion.
  `decided` means you decided; the decision and its date are in the entry and in the notes of the
  affected requirements. `resolved` means the cause went away (for example, the organizers fixed
  the file). Entries are never deleted, so the history stays visible.

| ID | Short title | Affects | Status |
|---|---|---|---|
| [ISS-01](#iss-01) | Where the evaluation reports go | CHR-607, CHR-608, CHR-609 | decided: (a) `code/evaluation/` |
| [ISS-02](#iss-02) | Remediation order: dependency or sorting? | CHR-329, CHR-416 | decided: (a) sort order |
| [ISS-03](#iss-03) | Sort `case_id` as text or as a number? | CHR-405 | decided: (b) number order |
| [ISS-04](#iss-04) | "row" accuracy vs "step-level" accuracy | CHR-611 | decided: "row" = step level |
| [ISS-05](#iss-05) | `agent-trace.zip` is missing from the submission lists | CHR-601, CHR-901 | decided (revised): follow agent_trace_instructions.md at the end |
| [ISS-06](#iss-06) | Submission URL starts with `wwww` | CHR-836 | resolved: the organizers fixed AGENTS.md |
| [ISS-07](#iss-07) | Unclear sentence about evidence in COMPLETE cases | CHR-435, CHR-436 | decided: reading confirmed |
| [ISS-08](#iss-08) | `python3` does not work on this Windows machine | CHR-512 | decided: use `python` as is for now |
| [ISS-09](#iss-09) | The lists of evidence formats differ | CHR-220 | decided: union of the lists |
| [ISS-10](#iss-10) | `README.md` is both an input and a deliverable | CHR-513, CHR-606, CHR-627 | decided: keep theirs; ours is `code/README.md` |
| [ISS-11](#iss-11) | A policy rule's condition does not hold: what then? | CHR-1005 to CHR-1008, CHR-1011 to CHR-1015 | decided: settle from the sample answers in c08 |
| [ISS-12](#iss-12) | The tests have run only on Python 3.15 | REV-007, ARC-12 | decided: Python 3.15 only |

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

**Decision (you, 2026-10-24): (a).** The reports go in `code/evaluation/`. Inside code.zip they
are `code/evaluation/evaluation_report.md` and `code/evaluation/usage_report.md`; there is no
top-level `evaluation/` folder. Recorded in the notes of CHR-607, CHR-608, and CHR-609.

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

**Evidence (2026-10-24, read-only check of `dataset/sample_output.csv`):** option (c) was done. In
all 32 sample answers, every phase with two or more steps (51 phase blocks) is in exact sort order
(operation order, then `system_id`, then `resource_id`), without a single exception. In case_16
and case_24, the source record (`account_service`) is deleted *before* its downstream search-index
copy (`search_service`): sorting wins over "downstream first".

**Proposal:** (a), always the sort order. The sample answers support it.

**Decision (you, 2026-10-24): (a), always the sort order.** Recorded in the notes of CHR-329 and
CHR-416.

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

**Decision (you, 2026-10-24): (b), number order.** Rows are sorted by the number after `case_`.
That is exactly the order of `dataset/deletion_requests.csv`. Checked: 518 unique IDs, all of the
form `case_<number>`, and the file is in number order; text order would differ. Recorded in the
note of CHR-405.

## ISS-04

**"row" accuracy vs "step-level" accuracy**

- SRC-RM0096: the evaluation report must cover "case, row, field, and sequence accuracy".
- SRC-AG0340, SRC-AG0341, SRC-AG0342, SRC-PS0135, SRC-PS0136, SRC-PS0137: "case-level status
  accuracy", "step-level and field-level accuracy", "sequence accuracy".

"row" most likely means one step (one element of `steps_json`), so it is the same as step-level.

**Proposal:** report case-level, step-level (= row-level), field-level, and sequence accuracy,
and use both names in the report.

**Decision (you, 2026-10-24):** proposal accepted. Recorded in the note of CHR-611.

## ISS-05

**`agent-trace.zip` is missing from the submission lists**

- agent_trace_instructions.md asks for `agent-trace.zip` "with your challenge submission"
  (SRC-AT0003, SRC-AT0013, SRC-AT0130).
- The submission tables list only `code.zip`, `output.csv`, `chat_transcript`, and the AI
  interview (SRC-AG0359 to SRC-AG0366, SRC-PS0145 to SRC-PS0148, SRC-RM0122 to SRC-RM0125).
  No file says where `agent-trace.zip` is uploaded.

**Proposal:** prepare `agent-trace.zip` anyway, and look for an upload slot on the submission
page.

**First decision (you, 2026-10-24), superseded below:** the agent trace is the root `log.txt`
that the organizers request as `chat_transcript`; no separate `agent-trace.zip` is planned.

**Consequence of the first decision (no longer applies):** CHR-901 to CHR-916, which come from
agent_trace_instructions.md, will not be carried out as written. That file asks for the raw session files (Claude Code JSONL files plus
the `/export` transcript) and says structured logs must not be replaced by summaries
(SRC-AT0005). `log.txt` is a summary log. If an upload slot for a trace ZIP turns up after all,
building one takes a few minutes (CHR-910, CHR-911).

**Decision, revised (you, 2026-10-24, later the same day):** agent_trace_instructions.md comes
from the organizers and will be followed at the end. The agent trace is prepared as
`agent-trace.zip` exactly as that file describes, and `log.txt` stays the `chat_transcript`.
CHR-901 to CHR-916 therefore apply, and the consequence above no longer holds. Where to upload
the ZIP is checked at the end. Recorded in the notes of CHR-601 and CHR-901.

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

**Evidence (2026-10-24, read-only check of `dataset/sample_output.csv`):** the 32 sample answers
follow exactly this reading. Findings cite evidence (41 of 41). Verification steps of COMPLETE
cases cite evidence (34 of 34). Remediation and verification steps of INCOMPLETE cases have an
empty `evidence_id` (41 of 41 and 77 of 77).

**Proposal:** keep this reading.

**Decision (you, 2026-10-24):** reading confirmed. Recorded in the notes of CHR-435 and CHR-436.

## ISS-08

**`python3` does not work on this Windows machine**

- SRC-RM0036: run the starter with `python3 code/main.py`.
- On this Windows machine, `python3` starts the Microsoft Store shortcut instead of Python;
  `python` (Python 3.15.0) works.

**Proposal:** our README must give a command that works on Windows too (for example
`python code/main.py` or `py code/main.py`) next to `python3 code/main.py` for macOS/Linux.

**Your question (2026-10-24): can `python3` be made to work on this machine?** Yes. Checked:

- `python3` currently reaches only the Microsoft Store shortcut (`WindowsApps\python3.exe`);
- PowerShell does not load profile scripts here (no execution policy is set, so the Windows
  default applies), so a PowerShell alias would need a security setting changed;
- `C:\Python315` can only be changed with admin rights.

The way that needs neither: a one-line file `python3.cmd`
(`@"C:\Python315\python.exe" %*`) in a personal folder placed at the front of your user PATH.
It is waiting for your go-ahead. The proposal for our README stays the same.

**Decision (you, 2026-10-24):** use `python` as it is on this machine for now; no `python3`
shim. The README part of the proposal stands: `code/README.md` will show both commands. Recorded
in the note of CHR-512.

## ISS-09

**The lists of evidence formats differ**

- SRC-PS0047 lists PDFs, images, logs, JSON, and SQL: no plain text.
- SRC-AG0202 and SRC-RM0059 also list plain text, and `dataset/evidence/records/` does contain a
  `.txt` file.

**Reading used:** the union of all lists, so plain text is included (CHR-220).

**Proposal:** keep this reading (only confirm).

**Decision (you, 2026-10-24):** confirmed. Recorded in the note of CHR-220.

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

**Decision (you, 2026-10-24):** keep the organizers' `README.md` unchanged at the root; our
README with setup and run instructions is `code/README.md`. Because the root README.md never
changes, `srctrace.py check` keeps reporting it as unchanged. Recorded in the notes of CHR-606
and CHR-627, and, added during the review of section 5, of CHR-513 (which also names "the
submitted README.md").

**Consequence for packaging (CHR-627):** the provided zip command packs `README.md` *and*
`code/`, so code.zip would hold the organizers' README at the top and ours at `code/README.md`,
and a reader might open the wrong one. To be decided at packaging time, for example by zipping
only `code/`.

## ISS-11

**A policy rule's condition does not hold: what then?**

Found in step 2, when `dataset/deletion_rules.csv` was added to the baseline.

- Each rule gives one required treatment for one data category under one condition
  (SRC-DR0002 to SRC-DR0016, CHR-1001 to CHR-1015).
- For 6 rules the condition is `Always`. For the other 9 it can be false, and the file does not
  say what applies then:

| Rule | Category | Condition | Treatment | Open case |
|---|---|---|---|---|
| rule_05 | SUPPORT_MESSAGE | conversation contains shared context that must be retained | REDACT | a message without such context |
| rule_06 | SUPPORT_ATTACHMENT | attachment belongs only to the deletion subject | DELETE | an attachment shared with others |
| rule_07, rule_08 | ANALYTICS_PROFILE, PRODUCT_TELEMETRY | record is still attributable to a user | ANONYMIZE | a record that is no longer attributable |
| rule_11 | EMAIL_DELIVERY_LOG | log contains a user email address | REDACT | a log without the email address |
| rule_12 | SECURITY_AUDIT_LOG | record is within the supplied retention period | RETAIN | a record after its retention period |
| rule_13 | LEGAL_HOLD_RECORD | a supplied legal hold is active | RETAIN | a hold that is no longer active |
| rule_14 | BACKUP_ARCHIVE | restore access can be blocked | RETAIN | a restore path that cannot be blocked |
| rule_15 | ACCOUNT_TOMBSTONE | account is deleted and only `user_id` is needed for references | REDACT | any other tombstone |

**Why it matters:** an audit that meets such a record must still decide whether it is compliant,
and which finding, remediation, and verification steps it needs.

**Reading used for now:** the requirements state only what the file says. For rule_07, rule_08,
and rule_11, a false condition most likely means the record already complies (nothing left to
anonymize or redact).

**Proposal:** settle it in step 3 (design) with evidence: find records of these categories in the
32 sample cases and see which steps the official sample answers contain for them, as was done for
ISS-02 and ISS-07.

**Decision (you, 2026-10-25):** "I agree with ISS-11 proposal". It is settled when c08
(ARC-08_policy_checker) is built: the sample answers show what applies, and the result is
recorded here, in the notes of the affected CHR items, and in that step's record.

## ISS-12

**The tests have run only on Python 3.15**

Found in step 5, in the recheck of c01.

- `code/pyproject.toml` declares Python 3.10 as the minimum (a design choice of step 4, so that
  the evaluators' Python is likely to be new enough).
- Python versions differ in details: `datetime.fromisoformat` accepts more forms from 3.11 on.
  REV-007 now asks for the same results on every supported version, and c01 no longer depends on
  that difference.
- The type checker (mypy) checks the code against the 3.10 library, but no test has run on 3.10:
  only Python 3.15 is installed here. Rancher Desktop (Docker) is installed but not running.

**Proposal:** before packaging (ARC-12), run all tests once on Python 3.10, in a `python:3.10`
container (Rancher Desktop must be started; the image is downloaded once, about 50 MB) or with a
second Python installed next to 3.15. If you prefer neither, the declared minimum can be raised
to the version that was actually tested.

**Decision (you, 2026-10-25):** "only python 3.15 will be used for this project". Recorded as
EXT-407. `code/pyproject.toml` now declares Python 3.15 only, and mypy and ruff check against
3.15. REV-007 stays, but with one supported version it holds without extra code, so c01's own
written form for times was removed again (its note says so).
