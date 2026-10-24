# Step 5: component c01, the input reader

| | |
|---|---|
| Date | 2026-10-25 |
| State | Done, waiting for your review; the next component (c03, evidence reader) starts with your go-ahead (EXT-610) |
| Goal | Read the CSV files of `dataset/` into the records of c00, check every value where it enters (EXT-503), and never stop on bad input (EXT-501) |
| Not in this step | Reading the evidence files themselves (c03); any decision about a case |

## What was made

`ARC-01_input_reader` in `code/c01_input_reader/`:

| File | Holds |
|---|---|
| `input_reader.py` | `read_dataset(dataset_dir)`: reads the 8 CSV files and returns one `Dataset` with every problem it found |
| `test_input_reader.py` | 20 tests: the real dataset, and a small made-up dataset broken in one way per test |

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
| A spreadsheet's byte-order mark, Windows line endings, spaces around values | Accepted |
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

## How to check

```powershell
python -m unittest discover -s code -t code -p "test_*.py"     # must end with OK (26 tests)
cd code; ..\.venv\Scripts\python -m mypy c00_interfaces c01_input_reader; ..\.venv\Scripts\ruff check c00_interfaces c01_input_reader; cd ..
.venv-req\Scripts\python requirements\tools\srctrace.py check   # must end with RESULT: PASS
```
