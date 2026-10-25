# Step 3: what the data shows, and the proposed design

| | |
|---|---|
| Date | 2026-10-24 |
| State | Analysis done for the main patterns; component design (updated after your design-process requirements, EXT section 6) approved by you on 2026-10-25 ([step 7.1](step-07.1-review.md)) |
| Goal | Learn from the dataset (by tools, read-only) how a case is decided, then propose the architecture |
| Not in this step | Solution code |

## What the data shows (found with scripts, read-only)

Every fact below was found by a script over `dataset/` or checked against the 32 official sample
answers. Nothing was taken from organizer-only files (CHR-505).

| # | Finding | How it was checked |
|---|---|---|
| F1 | The 32 samples are 10 COMPLETE and 22 INCOMPLETE cases, **no NOT_APPLICABLE**. The request classifier therefore cannot be checked on the samples; our own evaluation cases must cover it (CHR-613) | count of `sample_output.csv` |
| F2 | `email_hash` is the SHA-256 of the lower-case email. Old emails, phones, and hashes are in `user_audit_log.csv`. Evidence links a record to a person through the current **or an old** email (also in upper case), phone, name, `user_id`, or email hash. Example: case_12 links `analytics_9914` only through the hash of the old email | hash recomputed; samples traced |
| F3 | 94 evidence files in 6 formats: 24 SQL snapshots (loadable with Python's built-in `sqlite3`), 26 logs (`key=value` lines), 28 JSON files (several layouts), 1 text handover (pipe-separated, with explicit category and state), 4 PDFs (with a text layer), 11 PNG screenshots (need OCR or a vision model) | file listing; one example of each read |
| F4 | Each resource prefix belongs to one system: `account`→account_service, `search`→search_service, `analytics`→analytics_platform, `support`→support_platform, `export`→export_service, `data_flow`→integration_service, `backup`→backup_service, `audit_record`→security_service, `tombstone`→identity_service | all steps of the 32 answers |
| F5 | **COMPLETE**: only verification steps, each citing evidence. **INCOMPLETE**: a finding for each violation, a remediation for each, then verification for **every** relevant resource (also the ones that were already fine, and the retained ones), with empty `evidence_id` | all 32 answers |
| F6 | The deletion worker's activity rows are claims: case_02 says PARTIAL but is COMPLETE; case_05 says SUCCESS but a failover replica still holds the profile | samples traced |
| F7 | Treatments seen in the answers: profile, search entry, export, support attachment → delete; analytics profile → anonymize; support message, tombstone → redact; security audit record → retained (VERIFY_RECORD_PRESENT); data flow → disable; restorable backup → block restore | all 32 answers |
| F8 | Some records are only visible in PDFs or screenshots (case_07: the support attachment `support_001` is in a PDF) | samples traced |

## Proposed design

A Python program (`code/main.py`) with a **deterministic core** and an AI model only where code
cannot decide (EXT-401):

```text
dataset/ ──> 1 read and check inputs ──> 2 evidence readers ──> observations
                                          (SQL, log, JSON, text, PDF; PNG via vision model, cached)
request  ──> 3 request classifier (AI model, cached) ── not a deletion ──> NOT_APPLICABLE, []
         ──> 4 identity resolver (current + old emails, phones, hashes, user_id)
         ──> 5 resource finder (observations and activity linked to the identity)
         ──> 6 state at audit_at (latest evidence captured at or before audit_at)
         ──> 7 policy check (deletion_rules.csv: category -> required treatment)
         ──> 8 step builder (findings, remediation, verification; fixed order) ──> output.csv
evaluation/ ──> 9 sample scorer (case, step, field, sequence accuracy)  10 usage recorder (calls, tokens, cost)
```

| Component | Main requirements |
|---|---|
| 1 Read and check inputs | CHR-201, CHR-204, CHR-505, EXT-501, EXT-503 |
| 2 Evidence readers | CHR-218, CHR-220, CHR-308, EXT-502 |
| 3 Request classifier | CHR-301, CHR-303, CHR-408, EXT-502 |
| 4–6 Identity, resources, state | CHR-223, CHR-304, CHR-307, CHR-309, CHR-312 to CHR-314 |
| 7 Policy check | CHR-317 to CHR-322, CHR-1001 to CHR-1015 |
| 8 Step builder and writer | CHR-402 to CHR-405, CHR-433 to CHR-439, CHR-507, EXT-202, EXT-203, EXT-402, EXT-404 |
| 9–10 Scorer and usage recorder | CHR-607 to CHR-614, EXT-201, EXT-403 |

**Right side of the V:** every test names the requirement IDs it proves; the system test is the
score on the 32 samples; a small script lists each requirement with its tests and their last
result (EXT-104).

## Your design-process requirements, and how the design meets them

You added EXT-601 to EXT-607: meaningful components, each tested on its own and traceable up the
V; a new requirement touches only the components it affects; problems found later become
requirements of a separate type and are fixed from the top of the V.

### The components

Each component is one folder under `code/`, with its own unit tests. Components exchange only
plain data records (observation, identity, resource state, step), never each other's internals.
So every component can be tested alone, with small hand-made records as input (EXT-602).

You approved this design on 2026-10-24 and asked for meaningful names, then for a number in each
name so that the components are listed in the order the pipeline uses them (EXT-608). The
components are the items of the Doorstop document `ARC`
([views/ARC.md](../../requirements/views/ARC.md)). Their code folders carry the same number after
the letter `c`, because a Python package name cannot start with a digit:

| Component (ARC item) | Code folder | Does | Uses |
|---|---|---|---|
| `ARC-01_input_reader` | `code/c01_input_reader/` | Reads and checks the CSV files of `dataset/` | — |
| `ARC-02_model_gateway` | `code/c02_model_gateway/` | The only place that calls an AI model: any provider by settings, cache, usage records, answer checks | — |
| `ARC-03_evidence_reader` | `code/c03_evidence_reader/` | Turns each evidence file into observations (one reader per format; PDF with pypdf) | 02 for screenshots |
| `ARC-04_request_classifier` | `code/c04_request_classifier/` | Decides whether a request text authorizes deletion | 02 |
| `ARC-05_identity_resolver` | `code/c05_identity_resolver/` | Finds the subject and all current and old identifiers | 01 |
| `ARC-06_resource_finder` | `code/c06_resource_finder/` | Finds the subject's records, flows, and backups | 03, 05 |
| `ARC-07_state_reconstructor` | `code/c07_state_reconstructor/` | Decides each record's state at `audit_at`, and the evidence that proves it | 03, 06 |
| `ARC-08_policy_checker` | `code/c08_policy_checker/` | Maps each record to its rule and judges whether it complies | 01, 07 |
| `ARC-09_step_planner` | `code/c09_step_planner/` | Builds the ordered findings, remediation, and verification, and the JSON | 08 |
| `ARC-10_audit_pipeline` | `code/c10_audit_pipeline/` (started by `code/main.py`) | Runs the components for every case, writes `output.csv` and the per-case explanations | all |
| `ARC-11_evaluator` | `code/c11_evaluator/` | Scores against the samples; computes the numbers of both reports | output, usage records |
| `ARC-12_delivery_process` | — | Not code: logging, traceability tools, packaging, agent trace | — |

Every normative requirement (CHR, EXT, REV: 259 in total) is linked from at least one component.
Doorstop checks this for CHR, and `srctrace.py check` for EXT and REV. The code-quality and
component rules (EXT-504 to EXT-506, EXT-601 to EXT-603) are linked from every code component,
so a change to them flags all of them.

### How the V-model carries them

- **A new Doorstop document `ARC`** holds one item per component (C1 to C11, P1), with its
  responsibility and interface. Each item links to the requirements it implements (CHR, EXT,
  REV), so every component is traceable up the V (EXT-603). Doorstop already reports any CHR
  requirement that no component covers; a short check in `srctrace.py` does the same for EXT and
  REV.
- **A change from the top** (EXT-604): when a requirement changes, Doorstop marks exactly the
  links of the components that implement it as suspect. Only those are redesigned,
  reimplemented, and retested; the others are not touched.
- **A problem found later** (EXT-605 to EXT-607): it becomes a new item in the new document
  **`REV`** (requirements revealed during analysis, implementation, or testing). REV items are
  marked `derived`, and their rationale says what revealed them. Each one is linked to the
  affected component, then the fix flows down: design, code, tests. REV holds 4 items already,
  found in this step's analysis:

| ID | Requirement revealed by the analysis |
|---|---|
| REV-001 | Emails are matched without regard to case |
| REV-002 | The hash of an old email also links a record to the subject |
| REV-003 | An INCOMPLETE case verifies every relevant record, including the ones that already comply |
| REV-004 | Steps name the service that owns the resource, also when the copy sits in a replica |

- **Tests** are named after the component and requirement IDs they prove. A small script lists
  each requirement → component → tests → last result (EXT-104).

## Decisions needed from you

Your answers of 2026-10-24: the design is good (with names, done above); it must work with any
AI model (now EXT-405: provider and model are settings); use pypdf (now EXT-406). Still open:
which model access to use for our runs (point 1): you choose later between an API key and your
Claude subscription (through the Claude Code CLI); the components that need no model come first.

1. **AI model and key.** There is no model API key on this machine. Proposal: Anthropic, with a
   small model for the 518 request texts (batched) and a vision model for the 11 screenshots (once,
   cached). You put the key in an uncommitted `.env` file (CHR-508). Coding can start without it.
2. **PDF text:** use `pypdf` (open source, pure Python) instead of a model.
3. ~~Lighter V-model from here~~: replaced by the component design above, which your design-process
   requirements call for. To approve: the 11 components plus P1, the documents `ARC` and `REV`,
   and the 4 REV items.

## After your commit "Step3"

The baseline moved to your commit `2076651` (only log.txt had grown). Your 5 newer prompts became
source units SRC-LG0453 to SRC-LG0541; the 3 that carry instructions now link to EXT-405, EXT-406,
and EXT-601 to EXT-608. `srctrace.py check`: PASS (1446 lines). `doorstop -F -W`: no warnings.
118 items wait for your review.
