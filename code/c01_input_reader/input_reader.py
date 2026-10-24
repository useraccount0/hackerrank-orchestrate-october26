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
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeVar

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
RecordType = TypeVar("RecordType")

STEP_FIELDS = ("step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id")


class BadValueError(Exception):
    pass


def read_dataset(dataset_dir: Path) -> Dataset:
    problems: list[InputProblem] = []
    requests, unreadable_case_ids = read_table(dataset_dir / "deletion_requests.csv", "case_id",
                                               make_request, problems)
    sample_requests, _ = read_table(dataset_dir / "sample_deletion_requests.csv", "case_id", make_request, problems)
    sample_answers, _ = read_table(dataset_dir / "sample_output.csv", "case_id", make_answer, problems)
    identities, _ = read_table(dataset_dir / "user_identities.csv", "user_id", make_identity, problems)
    identity_changes, _ = read_table(dataset_dir / "user_audit_log.csv", "audit_id", make_identity_change, problems)
    activities, _ = read_table(dataset_dir / "system_activity.csv", "activity_id", make_activity, problems)
    rules, _ = read_table(dataset_dir / "deletion_rules.csv", "rule_id", make_rule, problems)
    evidence_files, _ = read_table(dataset_dir / "evidence_files.csv", "file_id",
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


def read_table(path: Path, id_column: str, make_record: Callable[[Row], RecordType],
               problems: list[InputProblem]) -> tuple[tuple[RecordType, ...], tuple[str, ...]]:
    """Returns the records that passed their checks, and the ids of the rows that did not."""
    records: list[RecordType] = []
    seen_ids: set[str] = set()
    failed_ids: set[str] = set()
    for location, header, values in read_csv(path, problems):
        row = dict(zip(header, values, strict=False))
        row_id = row.get(id_column, "")
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


def read_csv(path: Path, problems: list[InputProblem]) -> Iterator[tuple[str, list[str], list[str]]]:
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
        values = [value.strip() for value in next(csv.reader([line]), [])]
        if not values:
            continue
        if header is None:
            header = values
        else:
            yield f"line {line_number}", header, values
    if header is None:
        problems.append(InputProblem(path.name, "file", "is empty"))


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
        request_text=optional(row, "request_text"),
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
        name=optional(row, "name"),
        email=required(row, "email"),
        phone=optional(row, "phone"),
        email_hash=optional(row, "email_hash"),
        updated_at=utc_time(row, "updated_at"),
    )


def make_identity_change(row: Row) -> IdentityChange:
    return IdentityChange(
        audit_id=required(row, "audit_id"),
        user_id=required(row, "user_id"),
        changed_at=utc_time(row, "event_time"),
        field_name=required(row, "field_name"),
        old_value=optional(row, "old_value"),
        new_value=optional(row, "new_value"),
    )


def make_activity(row: Row) -> Activity:
    return Activity(
        activity_id=required(row, "activity_id"),
        event_time=utc_time(row, "event_time"),
        event_type=required(row, "event_type"),
        source_system=optional(row, "source_system"),
        target_system=optional(row, "target_system"),
        resource_id=required(row, "resource_id"),
        reported_result=optional(row, "reported_result"),
        details=optional(row, "details"),
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
        origin=optional(row, "origin"),
        captured_at=utc_time(row, "captured_at"),
    )


def is_evidence_file(dataset_dir: Path, file_path: str) -> bool:
    evidence_dir = (dataset_dir / "evidence").resolve()
    # resolve() follows ".." and links, so a path cannot lead to files outside dataset/ (CHR-504).
    target = (dataset_dir / file_path).resolve()
    return target.is_relative_to(evidence_dir) and target.is_file()


def optional(row: Row, column: str) -> str:
    if column not in row:
        raise BadValueError(f"has no {column} column")
    return row[column]


def required(row: Row, column: str) -> str:
    value = optional(row, column)
    if not value:
        raise BadValueError(f"{column} is empty")
    return value


def one_of(row: Row, column: str, allowed: Collection[str]) -> str:
    value = required(row, column)
    if value not in allowed:
        raise BadValueError(f"{column} is not one of {', '.join(allowed)}")
    return value


def utc_time(row: Row, column: str) -> datetime:
    value = required(row, column)
    try:
        # Python 3.10 does not read the "Z" (UTC) ending that the dataset uses.
        moment = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        raise BadValueError(f"{column} is not a time") from None
    if moment.tzinfo is None:
        raise BadValueError(f"{column} has no time zone")
    return moment.astimezone(timezone.utc)
