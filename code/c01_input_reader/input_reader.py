"""Reads the CSV files of dataset/ into records, checking every value where it enters (EXT-503).

A row that fails a check is skipped and reported, never repaired by guessing; the rest of the
solution relies on the records it gets. Of a skipped request row, the case_id is still passed on,
because every case needs an output row (REV-006).
"""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Callable, Collection, Iterator
from datetime import UTC, datetime
from pathlib import Path

from c00_interfaces.records import (
    DELETION_STATUSES,
    OPERATIONS,
    REPORTED_STATUSES,
    RULE_ACTIONS,
    Activity,
    CaseAnswer,
    Dataset,
    DeletionRule,
    EvidenceFile,
    IdentityChange,
    IdentityRecord,
    InputProblem,
    Request,
    Step,
)

Row = dict[str, str]

# The columns of each file, as problem_statement.md and the files name them; the first one
# identifies a row.
REQUEST_COLUMNS = ("case_id", "email", "requested_at", "reported_status", "reported_at", "audit_at", "request_text")
ANSWER_COLUMNS = ("case_id", "deletion_status", "steps_json")
IDENTITY_COLUMNS = ("user_id", "name", "email", "phone", "email_hash", "updated_at")
IDENTITY_CHANGE_COLUMNS = ("audit_id", "user_id", "event_time", "field_name", "old_value", "new_value")
ACTIVITY_COLUMNS = ("activity_id", "event_time", "event_type", "source_system", "target_system", "resource_id",
                    "reported_result", "details")
RULE_COLUMNS = ("rule_id", "data_category", "condition", "required_action")
EVIDENCE_FILE_COLUMNS = ("file_id", "file_path", "origin", "captured_at")

STEP_FIELDS = ("step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id")


class BadValueError(Exception):
    pass


def read_dataset(dataset_dir: Path) -> Dataset:
    problems: list[InputProblem] = []
    requests, unreadable_case_ids = read_table(dataset_dir / "deletion_requests.csv", REQUEST_COLUMNS,
                                               make_request, problems)
    sample_requests, _ = read_table(dataset_dir / "sample_deletion_requests.csv", REQUEST_COLUMNS,
                                    make_request, problems)
    sample_answers, _ = read_table(dataset_dir / "sample_output.csv", ANSWER_COLUMNS, make_answer, problems)
    identities, _ = read_table(dataset_dir / "user_identities.csv", IDENTITY_COLUMNS, make_identity, problems)
    identity_changes, _ = read_table(dataset_dir / "user_audit_log.csv", IDENTITY_CHANGE_COLUMNS,
                                     make_identity_change, problems)
    activities, _ = read_table(dataset_dir / "system_activity.csv", ACTIVITY_COLUMNS, make_activity, problems)
    rules, _ = read_table(dataset_dir / "deletion_rules.csv", RULE_COLUMNS, make_rule, problems)
    evidence_files, _ = read_table(dataset_dir / "evidence_files.csv", EVIDENCE_FILE_COLUMNS,
                                   lambda row: make_evidence_file(row, dataset_dir), problems)
    return Dataset(
        requests=requests,
        unreadable_case_ids=unreadable_case_ids,
        sample_requests=sample_requests,
        sample_answers=sample_answers,
        identities=identities,
        identity_changes=identity_changes,
        activities=activities,
        rules=rules,
        evidence_files=evidence_files,
        problems=tuple(problems),
    )


def read_table[RecordType](path: Path, columns: tuple[str, ...], make_record: Callable[[Row], RecordType],
                           problems: list[InputProblem]) -> tuple[tuple[RecordType, ...], tuple[str, ...]]:
    """Returns the records that passed their checks, and the ids of the rows that did not."""
    id_column = columns[0]
    records: list[RecordType] = []
    seen_ids: set[str] = set()
    failed_ids: set[str] = set()
    for location, header, values in read_csv(path, columns, problems):
        row = dict.fromkeys(columns, "") | dict(zip(header, values, strict=False))
        row_id = row[id_column]
        try:
            if len(values) != len(header):
                raise BadValueError(f"has {len(values)} values, but the header has {len(header)} columns")
            record = make_record(row)
        except BadValueError as error:
            problems.append(InputProblem(path.name, location, str(error)))
            failed_ids.add(row_id)
            continue
        if row_id in seen_ids:
            problems.append(InputProblem(path.name, location, f"repeats {id_column} {row_id}; the first row is kept"))
            continue
        seen_ids.add(row_id)
        records.append(record)
    unreadable_ids = sorted(row_id for row_id in failed_ids - seen_ids if row_id)
    return tuple(records), tuple(unreadable_ids)


def read_csv(path: Path, columns: tuple[str, ...],
             problems: list[InputProblem]) -> Iterator[tuple[str, list[str], list[str]]]:
    """Yields (location, header, values) for every data row, with spaces trimmed from the values."""
    text = read_text(path, problems)
    if text is None:
        return
    # Python's default limit (128 Ki characters) would stop the whole run at one long value.
    csv.field_size_limit(max(csv.field_size_limit(), len(text)))
    header: list[str] | None = None
    # Each line is read as one row, so that a stray quote cannot swallow the rows after it; no
    # file in dataset/ has a value with a line break.
    for line_number, line in enumerate(io.StringIO(text, newline=""), start=1):
        values = [value.strip() for value in next(csv.reader([line], skipinitialspace=True), [])]
        if not values:
            continue
        if header is None:
            header = values
            check_header(path, f"line {line_number}", header, columns, problems)
        else:
            yield f"line {line_number}", header, values
    if header is None:
        problems.append(InputProblem(path.name, "file", "is empty"))


def check_header(path: Path, location: str, header: list[str], columns: tuple[str, ...],
                 problems: list[InputProblem]) -> None:
    missing = [column for column in columns if column not in header]
    if missing:
        problems.append(InputProblem(path.name, location, f"has no column {', '.join(missing)}; "
                                                          "its values count as empty"))
    repeated = sorted({column for column in header if header.count(column) > 1})
    if repeated:
        problems.append(InputProblem(path.name, location, f"repeats column {', '.join(repeated)}; "
                                                          "only the last copy is read"))


def read_text(path: Path, problems: list[InputProblem]) -> str | None:
    try:
        data = path.read_bytes()
    except OSError as error:
        problems.append(InputProblem(path.name, "file", f"cannot be read: {error.strerror or type(error).__name__}"))
        return None
    try:
        # utf-8-sig also accepts the byte-order mark that spreadsheet programs write.
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        problems.append(InputProblem(path.name, f"byte {error.start}", "is not UTF-8; unreadable bytes were replaced"))
        # Replacing keeps the readable rows, so one bad byte does not cost every case in the file.
        return data.decode("utf-8-sig", errors="replace")


def make_request(row: Row) -> Request:
    request = Request(
        case_id=required(row, "case_id"),
        email=required(row, "email"),
        requested_at=utc_time(row, "requested_at"),
        reported_status=one_of(row, "reported_status", REPORTED_STATUSES),
        reported_at=utc_time(row, "reported_at"),
        audit_at=utc_time(row, "audit_at"),
        request_text=row["request_text"],
    )
    if request.audit_at < request.requested_at:
        raise BadValueError("audit_at is before requested_at")
    return request


def make_answer(row: Row) -> CaseAnswer:
    case_id = required(row, "case_id")
    deletion_status = one_of(row, "deletion_status", DELETION_STATUSES)
    steps_text = required(row, "steps_json")
    # Deeply nested arrays make the JSON parser run out of recursion depth instead of failing.
    try:
        steps_json = json.loads(steps_text)
    except (ValueError, RecursionError):
        raise BadValueError("steps_json is not valid JSON") from None
    if not isinstance(steps_json, list):
        raise BadValueError("steps_json is not a JSON array")
    steps = tuple(make_step(fields) for fields in steps_json)
    if [step.step_no for step in steps] != list(range(1, len(steps) + 1)):
        raise BadValueError("steps are not numbered 1, 2, 3, ...")
    return CaseAnswer(case_id, deletion_status, steps)


def make_step(fields: object) -> Step:
    if not isinstance(fields, dict) or sorted(fields) != sorted(STEP_FIELDS):
        raise BadValueError(f"a step does not have exactly the fields {', '.join(STEP_FIELDS)}")
    # In Python, true and false are also integers, and neither is a step number.
    if type(fields["step_no"]) is not int:
        raise BadValueError("a step_no is not a whole number")
    if not all(isinstance(fields[name], str) for name in STEP_FIELDS if name != "step_no"):
        raise BadValueError(f"step {fields['step_no']} has a field that is not text")
    step = Step(**fields)
    if OPERATIONS.get(step.operation) != (step.phase, step.state):
        raise BadValueError(f"step {step.step_no} combines operation, phase and state in a way that is not allowed")
    return step


def make_identity(row: Row) -> IdentityRecord:
    return IdentityRecord(
        user_id=required(row, "user_id"),
        name=row["name"],
        email=required(row, "email"),
        phone=row["phone"],
        email_hash=row["email_hash"],
        updated_at=utc_time(row, "updated_at"),
    )


def make_identity_change(row: Row) -> IdentityChange:
    return IdentityChange(
        audit_id=required(row, "audit_id"),
        user_id=required(row, "user_id"),
        changed_at=utc_time(row, "event_time"),
        field_name=required(row, "field_name"),
        old_value=row["old_value"],
        new_value=row["new_value"],
    )


def make_activity(row: Row) -> Activity:
    return Activity(
        activity_id=required(row, "activity_id"),
        event_time=utc_time(row, "event_time"),
        event_type=required(row, "event_type"),
        source_system=row["source_system"],
        target_system=row["target_system"],
        resource_id=required(row, "resource_id"),
        reported_result=row["reported_result"],
        details=row["details"],
    )


def make_rule(row: Row) -> DeletionRule:
    return DeletionRule(
        rule_id=required(row, "rule_id"),
        data_category=required(row, "data_category"),
        condition=required(row, "condition"),
        required_action=one_of(row, "required_action", RULE_ACTIONS),
    )


def make_evidence_file(row: Row, dataset_dir: Path) -> EvidenceFile:
    file_path = required(row, "file_path")
    if not is_evidence_file(dataset_dir, file_path):
        raise BadValueError("file_path is not a file inside the evidence folder")
    return EvidenceFile(
        file_id=required(row, "file_id"),
        file_path=file_path,
        origin=row["origin"],
        captured_at=utc_time(row, "captured_at"),
    )


def is_evidence_file(dataset_dir: Path, file_path: str) -> bool:
    evidence_dir = (dataset_dir / "evidence").resolve()
    # resolve() follows ".." and links, so a path cannot lead to files outside dataset/ (CHR-504).
    target = (dataset_dir / file_path).resolve()
    return target.is_relative_to(evidence_dir) and target.is_file()


def required(row: Row, column: str) -> str:
    if not row[column]:
        raise BadValueError(f"{column} is empty")
    return row[column]


def one_of(row: Row, column: str, allowed: Collection[str]) -> str:
    value = required(row, column)
    if value not in allowed:
        raise BadValueError(f"{column} is not one of {', '.join(allowed)}")
    return value


def utc_time(row: Row, column: str) -> datetime:
    value = required(row, column)
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        raise BadValueError(f"{column} is not a time") from None
    if moment.tzinfo is None:
        raise BadValueError(f"{column} has no time zone")
    # A time at the edge of the calendar can leave it when moved to UTC (year 1 with a positive offset).
    try:
        return moment.astimezone(UTC)
    except OverflowError:
        raise BadValueError(f"{column} is not a possible time in UTC") from None
