# Step 6: component c03, the evidence reader

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, approved by you on 2026-10-25 ([step 7.1](step-07.1-review.md)) |
| Goal | Turn each of the 94 evidence files into observations (which record, in which store, seen when, with which identifiers and facts) and listings (all records of a store at one time) |
| Not in this step | Which records belong to a case (c06) and their state at `audit_at` (c07); the real AI model (c02, last) |

## What the evidence looks like (found with scripts, read-only)

| Format | Files | What is inside |
|---|---|---|
| SQL snapshots | 24 | 4 table layouts: profile tables, primary/replica tables with a JSON column, an inventory of 8 tables, a search table. Every table is a complete copy of its store at capture time |
| JSON | 28 | 4 layouts: snapshot bundles (collections with their own capture times), service exports (lookups with HTTP status 404 or 200, search queries with hit counts), ledgers (lookup results: FOUND, NOT_FOUND, ANONYMIZED, DISABLED, ..., with the policy category), simple collections |
| Logs | 26 | About 8 line formats (`key=value`, JSON, syslog, bracketed, pipe-separated, cloud export with an escaped message). Most are request traces: the "started" line names the email it looks for, the "completed" line the resource it found, joined only by a trace id |
| Text handover | 1 | Fixed columns: time, system, resource, category, result, identifier |
| PDF | 4 | Business documents with a text layer; 2 name a resource, 2 name none |
| Screenshots | 11 | Admin pages with resource ids, emails, phones, names in tables and detail panels |

The 32 sample answers cite evidence 76 times, always an evidence file (never an activity or
audit id): service exports 36, trace logs 9, the handover 7, other logs 5, SQL 10, bundles 4,
others 5, screenshots 0.

## What was made

`ARC-03_evidence_reader` in `code/c03_evidence_reader/`:

| File | Does |
|---|---|
| `evidence_reader.py` | `read_evidence(files, dataset_dir, gateway)`: picks the reader by file type, reports a file that cannot be read and goes on, and builds the store listings |
| `record_fields.py` | The rules for all formats: which values are identifiers, whether a record exists, what goes into facts |
| `sql_snapshots.py` | Loads a snapshot into an in-memory SQLite database, statement by statement |
| `json_records.py` | One walk for all JSON layouts |
| `log_lines.py` | One line reader for all log formats; joins the lines of one trace |
| `text_documents.py` | Handover lines, and free text (from PDFs and screenshots) |
| `document_text.py` | The text of a PDF (pypdf) and of a screenshot (model gateway) |
| `test_evidence_reader.py` | 26 tests |

## The rules, and why

| Rule | Why |
|---|---|
| Identifiers are recognized by the **shape of their values**, wherever they are: email, 64-hex hash, `user_N`, phone with `+`. Names only from fields called a name | The formats name the same thing in many ways (`email`, `customer_email`, `lookup_key`, `subject_reference`), and emails also hide in message texts ("Please send the delivery update to ...") |
| Emails and hashes are lower-cased (REV-001) | Some evidence writes emails in upper case |
| A hash after `sha256:` is not an email hash | Integrity seals are file checksums |
| A source that shows a record's content shows that it exists. Explicit signals say that it is missing (HTTP 404, NOT_FOUND, `rows=0`, no hits), and a "missing" signal wins. A lookup that was only started proves nothing (unknown) | The reader says what a file shows and never guesses (changed in the recheck, see below) |
| Log lines with the same trace id are one request; the identifiers it looked up reach the resource it found | Otherwise the email and the resource of a lookup are never connected (case_10, case_12) |
| Every SQL table and JSON collection is a **complete listing**, for each kind of record its store holds in any file | Proves absence (REV-005); a table that is empty in one snapshot still proves that everything is gone |
| Free text: a document about one resource gives it all its identifiers; otherwise each resource gets the lines from its mention to the next one, after the document's heading | A PDF names the support record once and the customer's email lines below it (case_07); a screenshot table has one resource per row |
| The model only **writes down** the text of a screenshot; the same rules then read it | The judgment stays in code (EXT-401), and the model's answer is easy to check |
| SQLite may only do what loading a snapshot needs (create tables and indexes, insert, update, read, transactions, `PRAGMA foreign_keys`, `json_valid`); everything else is refused | A snapshot is data (EXT-502); an `ATTACH` could otherwise make SQLite write files anywhere. A test proves it: with the guard removed on purpose, the test fails |
| One failing SQL statement, one unreadable file, or one model failure costs only itself, and is reported | EXT-501 |

## Two interface gaps, fixed at the top (c00)

| Gap | Fix |
|---|---|
| A record can carry two values of one kind, such as the email it was looked up by and another one in its text, but `Observation.identifiers` held one value per kind | `identifiers: Mapping[str, frozenset[str]]` |
| A snapshot's own time can be earlier than the file's capture time (a bundle exported on 09-17 holds collections of 09-09 to 09-17). The capture time decides whether the file may be cited at `audit_at`; the snapshot time decides how recent the state is. `StoreListing` had only one time | `StoreListing.observed_at`, as `Observation` already had |

Both serve existing requirements (CHR-313, REV-005), so no new requirement was needed.

## A revealed requirement for a later component

Comparing every identifier the reader found with the identity data showed **decoy names** next to
the real ones: Priya Ramanathan next to Priya Raman (case_07), Jonas Berglund next to Jonas Berg
(case_06). A substring match would link them. This became **REV-008** (a name links a record only
when the whole name matches), derived from CHR-223 (decoys) and CHR-309 (matching), implemented
by ARC-06. Decoy emails (`....jr@gmail.com`) are already safe, because emails are compared whole.

## Results on the real evidence

- 2953 observations and 418 listings from the 83 files that need no model, in 1.4 seconds.
- **Every one of the 76 evidence citations in the 32 sample answers is explained** by the reading:
  the cited file shows the cited resource, or (for ABSENT) lists its store without it. This is
  now a test.
- Of 1,503 distinct identifier values found, 33 are unknown to the identity data: the decoys
  above and records of other people.
- 3 files give no observations: two PDFs name no resource (an order statement and a register of
  disputed orders), and one inventory snapshot is empty (it proves absence).
- The 11 screenshots wait for the model gateway (c02); until then the tests use a fake gateway.

## Also in this step

- pypdf 6.21.2 (BSD-3-Clause) installed in `.venv` and pinned in `code/requirements.txt`, the
  solution's first runtime dependency. Tests now run with `.venv\Scripts\python`, which has it.
- After your commit "Step5+", the baseline moved to it. Your "recheck c01" became SRC-LG0675
  (context) and "only python 3.15 will be used for this project" SRC-LG0697, which EXT-407 now
  links to.

Results: 53 tests OK; mypy (strict) and ruff clean; `doorstop -F -W` clean; `srctrace.py check`
PASS; 134 items wait for your review.

## Recheck of c03 (your request "recheck c03")

The recheck compared what the reader says about every cited record with what the 32 sample
answers say about it, and tried inputs the tests had not covered. Found and fixed:

| # | Problem | Fix |
|---|---|---|
| 1 | **About 40 cited records were "unknown"** although the answers treat them as existing (PRESENT, ANONYMIZED, DISABLED, ...): full records in service exports, and log lines that read or scan a record (`analytics_profile_read_completed`, `message_pii_scan`, `connector_heartbeat`). The rule "no explicit signal, no answer" was too strict | A source that shows a record's content shows that it exists; only a lookup that was only started stays unknown. Now every one of the 76 cited records agrees with the answers: the 6 ABSENT ones read as missing, the 70 others as existing |
| 2 | **A file name in free text became a resource**: `customer_export_7364.zip` gave a record of kind `customer_export`, which could have produced a wrong step | A name followed by a file extension is not a resource id |
| 3 | **Two ledger records are dated two days after their file was captured** (evidence_13, evidence_36). A case audited in between could use a record from its own future if only the file's capture time were checked | Kept as it is (the reader reports what the file says). New revealed requirement **REV-009**: a record counts only when both the file's capture time and the record's own time are at or before `audit_at`; implemented by ARC-07 (state reconstructor) |

Notes for later components: booleans are written `1`/`0` in SQL and `true`/`false` elsewhere
(c07); names stay in the text of free-text records and must match whole (REV-008, c06).

The screenshots could not be checked yet: their text comes from the model. The rules for free
text will be checked again on the real transcriptions in step 7 (c02).

Results: 56 tests OK; mypy (strict) and ruff clean; `doorstop -F -W` clean; `srctrace.py check`
PASS.

## How to check

```powershell
.venv\Scripts\python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK (56 tests)
cd code; ..\.venv\Scripts\python -m mypy c00_interfaces c01_input_reader c03_evidence_reader; ..\.venv\Scripts\ruff check .; cd ..
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```
