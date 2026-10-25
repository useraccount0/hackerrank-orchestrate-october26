# Step 5: component c01, the input reader

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, approved by you on 2026-10-25 ([step 7.1](step-07.1-review.md)) |
| Goal | Read the CSV files of `dataset/` into the records of c00, check every value where it enters (EXT-503), and never stop on bad input (EXT-501) |
| Not in this step | Reading the evidence files themselves (c03); any decision about a case |

## What was made

`ARC-01_input_reader` in `code/c01_input_reader/`:

| File | Holds |
|---|---|
| `input_reader.py` | `read_dataset(dataset_dir)`: reads the 8 CSV files and returns one `Dataset` with every problem it found |
| `test_input_reader.py` | 24 tests: the real dataset, and a small made-up dataset broken in one way per test |

How it is built, top to bottom: `read_dataset` calls `read_table` once per file; `read_table`
turns rows into records and keeps the first of a repeated id; `read_csv` and `read_text` read
the file; one `make_...` function per record type does the checks of that file.

## What a row must pass

A row that fails a check is skipped and reported (file, line, what is wrong). It is never
repaired by guessing, so the later components can rely on every record they get.

| Check | Why |
|---|---|
| The row has as many values as the header has columns | A missing quote around a text with a comma shifts every value after it |
| The id is not empty, nor is any value the record has no meaning without (for example a request's email, an activity's resource_id) | Other values may be empty; an empty value means "not given" and never matches another empty value (now written in `records.py`) |
| Times carry a time zone, and are stored as UTC | A time without a zone cannot be compared with `audit_at` without guessing |
| `audit_at` is not before `requested_at` | An audit of a request that did not exist yet is misleading |
| `reported_status`, `required_action`, `deletion_status`, and every sample step use only the published values | The lists are now in `records.py` (`REPORTED_STATUSES`, `RULE_ACTIONS`); the step check uses the allowed-operations table |
| An evidence path leads to an existing file inside `dataset/evidence/` | A path such as `../..` must not make the solution read files outside `dataset/` (CHR-504, CHR-505) |

Protection for the file as a whole:

| Risk | What happens instead |
|---|---|
| A stray quote swallows all later rows into one value, silently (Python's CSV reader does this) | Each line is read as one row; no file in `dataset/` has a value with a line break |
| A value longer than 128 Ki characters stops Python's CSV reader with an error | The limit is raised to the file's length |
| A byte that is not UTF-8 | Reported; only that character is replaced, the rows stay |
| A spreadsheet's byte-order mark, Windows line endings, spaces around values (also before a quoted value) | Accepted |
| A column the header lacks | Reported once; its values count as empty, so a missing column that may be empty costs no rows |
| A column the header repeats | Reported once; only its last copy is read |
| A missing or empty file | Reported; the other files are still read |

## A revealed requirement, fixed from the top (EXT-605, EXT-607)

Skipping a bad row, as for the other files, would drop its case from `output.csv` without a
trace, and a submission without that row breaks CHR-403. This became **REV-006**: of a request
row that fails its checks, the `case_id` is still passed on. The fix followed your process, top
down:

1. REV-006 written, derived from CHR-403, CHR-503, and EXT-501.
2. ARC-00 (interfaces): `Dataset` got the field `unreadable_case_ids`.
3. ARC-01 (this component): implements it; a test proves it.
4. ARC-10 (audit pipeline, not built yet): its text now says that these cases get a row too.

No other component was touched (EXT-604).

## What the data showed

The real dataset is clean: all 8 files read without a single problem (518 requests, 32 sample
requests and answers, 850 identities, 306 identity changes, 4011 activities, 15 rules, 94
evidence files). All files use Windows line endings, and none has a byte-order mark or a value
with a line break. In every request, `requested_at` ≤ `reported_at` ≤ `audit_at`.

One fact for later components: case_33 and case_52 come from the same email address, a month
apart (audits on 2026-06-19 and 2026-07-19). Each case is judged at its own `audit_at`, so they
may get different answers.

## Traceability

After your commit "Step4++", the baseline moved to it (log.txt grew at its end only). Your two
"recheck c00" prompts became SRC-LG0607 and SRC-LG0630, classified as context: they ordered work
in this session and state no lasting requirement.

Results: 26 tests OK (c00 and c01); mypy (strict) and ruff clean; `doorstop -F -W` clean;
`srctrace.py check` PASS; 128 items wait for your review.

## Recheck of c01 (your request "recheck c01")

The recheck tried inputs the tests had not covered, checked every claim of this record, and
looked for what the tests could not catch. Found and fixed:

| # | Problem | Fix |
|---|---|---|
| 1 | **A time in year 1 or 9999 with an offset crashed the whole run** (`OverflowError` when moved to UTC), against EXT-501 | Such a time now fails its check like any bad value; a test proves the run goes on |
| 2 | **The same file could be read differently on different Python versions**: from 3.11 on, Python accepts time forms such as `20260904T100000Z` that 3.10 rejects, and `code/pyproject.toml` promises 3.10 | Times must have one written form, checked by the reader itself. New revealed requirement **REV-007** (same results on every supported Python version), linked from ARC-01 and ARC-12. Only Python 3.15 is installed here, so no test has run on 3.10 yet: **ISS-12**, waiting for your decision |
| 3 | **A missing column that may be empty cost every row of its file**: without the `details` column, all 4011 activities would have been dropped, each with its own problem | The header is checked once per file; a missing column counts as empty and is reported once |
| 4 | **A repeated column name went unnoticed**, so a second `audit_at` column could silently change every cutoff | Reported once per file |
| 5 | **"Spaces around values: accepted" was not fully true**: a space before a quoted value made the row unreadable | Fixed (`skipinitialspace`) |
| 6 | **No test checked that each value lands in the right field**: swapping, for example, `source_system` and `target_system` would have passed every test | A test now compares whole records for every file; with the two fields swapped on purpose, it fails, as it should |

The columns of every file are now written once, at the top of `input_reader.py`, which also
makes the expected file format readable in one place.

Fixes 1, 3, 4, and 5 follow requirements that existed already (EXT-501), so they needed no new
requirement; only the design note of ARC-01 changed. Fix 2 was a surprise that no requirement
covered, so it became REV-007 (EXT-605).

After your commit "Step5", the baseline moved to it, and your prompt "continue with c01" became
SRC-LG0652, classified as context (the go-ahead that EXT-610 asks for).

Results: 30 tests OK (24 for c01); mypy (strict) and ruff clean; `doorstop -F -W` clean;
`srctrace.py check` PASS.

## Your decision on ISS-12: Python 3.15 only

You decided that only Python 3.15 is used for this project. Recorded as **EXT-407**, implemented
by ARC-12 (delivery). What changed, top down:

| Level | Change |
|---|---|
| EXT | New EXT-407; it links to your words after your next commit (until then Doorstop shows 1 expected warning) |
| REV | REV-007 stays: with one supported version it holds without extra code (note added). Doorstop flagged ARC-12's link to it as suspect; after review it was confirmed |
| ARC | ARC-01 no longer links to REV-007, because it has no code for it any more; its note was updated |
| Code | `code/pyproject.toml` declares Python 3.15 only, and mypy and ruff check against 3.15. In c01, the own written form for times and the 3.10 workaround for `Z` were removed: times are read by Python's own ISO 8601 reader, must carry a time zone, and a time that leaves the calendar in UTC is still caught. Two newer idioms replace older ones (`datetime.UTC`; type parameters instead of `TypeVar`) |

Results: 30 tests OK; mypy (strict) and ruff clean; `srctrace.py check` PASS.

## How to check

```powershell
python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK (30 tests)
cd code; ..\.venv\Scripts\python -m mypy c00_interfaces c01_input_reader; ..\.venv\Scripts\ruff check c00_interfaces c01_input_reader; cd ..
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```
