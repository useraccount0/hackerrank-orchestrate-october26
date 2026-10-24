# Step 4: the interfaces between the components

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, waiting for your review; then the components are implemented one at a time (EXT-610) |
| Goal | Define how the components talk to each other, so that every component can be tested alone with fakes (EXT-609) |
| Not in this step | Any component's logic |

## What was made

A new component, `ARC-00_interfaces` (`code/c00_interfaces/`), listed first:

| File | Holds |
|---|---|
| `records.py` | The plain data records the components exchange: Request, IdentityRecord, IdentityChange, Activity, DeletionRule, EvidenceFile, Dataset; Observation (one record seen in one evidence item); StoreListing (all records of one store at one time); Identity, Resource, ResourceState, Judgement, CaseVerdict; Step, CaseAnswer, CaseResult; ModelQuestion, ModelCall; Scores; and the allowed operations, phases, and statuses |
| `components.py` | The call signature of every component, and the `Components` bundle the audit pipeline receives |
| `fakes.py` | `FakeModelGateway` (answers with whatever a test tells it, and records the questions) and a typed do-nothing fake for every component |
| `test_interfaces.py` | 5 tests: fakes stand in for every component; records cannot be changed and stay hashable; the operations table equals the one in `problem_statement.md` |

How data flows, with the signature of each component:

```text
01 input_reader        dataset_dir                                   -> Dataset
02 model_gateway       ModelQuestion                                 -> answer text (+ ModelCall records)
03 evidence_reader     evidence files, dataset_dir, gateway          -> Observations + StoreListings
04 request_classifier  Requests, gateway                             -> RequestDecision per case
05 identity_resolver   email, identities, identity changes, audit_at -> Identity
06 resource_finder     Identity, Request, Observations, Activities   -> Resources
07 state_reconstructor Resources, EvidenceReading, Activities, audit_at -> ResourceStates
08 policy_checker      case_id, ResourceStates, DeletionRules, audit_at -> CaseVerdict (one Judgement per resource)
09 step_planner        CaseVerdict                                   -> CaseAnswer (ordered Steps)
10 audit_pipeline      Components bundle, dataset_dir                -> output.csv + explanation per case
11 evaluator           predicted and expected CaseAnswers            -> Scores
```

Why this makes components testable alone (EXT-602): every component is a function of plain
records. A test builds the input records by hand and checks the output records; it never needs
another component. The audit pipeline gets all components as one bundle, so its test can pass
fakes. The two components that need the AI model (03 for screenshots, 04) get the gateway as a
parameter, so their tests pass `FakeModelGateway`.

Every ARC item's `interface` attribute now names its exact signature; see
[views/ARC.md](../../requirements/views/ARC.md).

## Your instructions, recorded

| ID | Says |
|---|---|
| EXT-609 | Interfaces first, so that tests can replace any component by a fake |
| EXT-610 | Components implemented one at a time, each started with your go-ahead |
| EXT-611 | The component that calls an AI model (`ARC-02_model_gateway`) is implemented last |

Planned order: 01 input_reader, 03 evidence_reader, 04 request_classifier, 05 identity_resolver,
06 resource_finder, 07 state_reconstructor, 08 policy_checker, 09 step_planner, 10 audit_pipeline,
11 evaluator, and last 02 model_gateway. Until then, 03 and 04 are tested with the fake gateway.

They link to your words after your next commit (Doorstop shows 3 expected warnings until then).

## A mistake on the way, and its repair

The first script that updated the ARC items saved them before Doorstop had loaded them (Doorstop
loads items lazily), which wrote 12 items nearly empty. `doorstop -F -W` and `srctrace.py check`
reported it at once. The 12 files were restored from your commit "Step3" with `git restore`, and the
update was run again with every item loaded first. Afterwards: `srctrace.py check` PASS, and
Doorstop shows only the 3 expected warnings.

## Recheck of c00 (your request "recheck c00")

Your own edit (imports from `collections.abc` instead of `typing`) is correct and kept. The
recheck compared the interfaces with the 32 sample answers again and with the requirements, and
found four problems. All are fixed:

| # | Problem | Fix |
|---|---|---|
| 1 | **A record's absence could not be proven.** 4 sample answers prove ABSENT with evidence that never names the record: a complete snapshot table without it (case_01, 02, 04: `evidence_54`; case_31: `evidence_51`). An Observation only describes records that are there. Found with a script that checks whether each cited evidence file contains the step's resource ID | New revealed requirement **REV-005**; new record `StoreListing` (all records of one store at one time) in `EvidenceReading`; the state reconstructor now receives the whole `EvidenceReading`. Linked from ARC-00, ARC-03, ARC-07 |
| 2 | **The policy checker had no audit time**, but rule_12 ("within the supplied retention period") and rule_13 ("legal hold is active") must be judged at `audit_at` (CHR-1012, CHR-1013, CHR-313) | `PolicyChecker` now receives `audit_at`. No new requirement: the requirement existed, the design had missed it |
| 3 | **Records with a dict field could not be hashed** (`Observation`, `ResourceState`), so putting them in a set would crash | The dict fields are left out of the hash (`hash=False`); a test proves it |
| 4 | **The old test proved little**: `isinstance` with these signatures only checks that something is callable | Typed fakes for every component in `fakes.py`, checked by **mypy** (open-source type checker, strict mode) against the signatures. A deliberately broken fake (missing `audit_at`) was rejected by mypy, so the check works |

Added as part of the contract: the allowed-operations table (`OPERATIONS`, in the order that
CHR-416 sorts by), `PHASES`, and `DELETION_STATUSES`. A test reads the table from
`problem_statement.md` and checks that it is identical, row by row.

New tools, both open source, in a project environment `.venv` (not in git), pinned in
`code/requirements-dev.txt`: **mypy** (type checker) and **ruff** (linter). Their settings and the
minimum Python version (3.10) are in `code/pyproject.toml`.

After your commit "Step4", your interface instructions became source unit SRC-LG0584, and
EXT-609 to EXT-611 now link to it. Doorstop shows no warnings.

## How to check

```powershell
python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK (5 tests)
cd code; ..\.venv\Scripts\python -m mypy c00_interfaces; ..\.venv\Scripts\ruff check c00_interfaces; cd ..
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```

One-time setup of the tools: `python -m venv .venv` then
`.venv\Scripts\python -m pip install -r code\requirements-dev.txt`.
