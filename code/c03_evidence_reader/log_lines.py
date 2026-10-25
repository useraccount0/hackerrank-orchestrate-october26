"""Reads log evidence. The services write several line formats, but every line is a time followed
by named values; lines that share a trace id belong to one request, such as a lookup started with
an email address and completed with the resource it found.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from c03_evidence_reader.record_fields import FileContents, RecordSeen, is_identifier_value, text_of, utc_time

KEY_VALUE = re.compile(r'(\w+)=("(?:[^"\\]|\\.)*"|\S+)')
# Formats that name the level, service, trace, and event by position instead of by name.
POSITIONAL_HEADERS = (
    (re.compile(r"^\[(\w+)\] \[([\w-]+)\] \[([\w-]+)\] (\w+):"), ("level", "service", "trace_id", "event")),
    (re.compile(r"^\| (\w+) \| ([\w-]+) \| ([\w-]+) \| (\w+) \|"), ("level", "service", "trace_id", "event")),
    (re.compile(r"^<\d+>\d+ \S+ ([\w-]+) ([\w-]+) "), ("service", "trace_id")),
)
STORE_NAMES = ("system", "service", "function", "logger")


@dataclass(frozen=True)
class LogLine:
    number: int
    text: str
    fields: dict[str, str]


def records_in_log(text: str, default_store: str) -> FileContents:
    contents = FileContents()
    requests: dict[str, list[LogLine]] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        time_text, _, rest = line.partition(" ")
        if utc_time(time_text) is None:
            contents.problems.append((f"line {number}", "has no time at its start; skipped"))
            continue
        fields = {"time": time_text} | line_fields(rest)
        trace = fields.get("trace_id") or fields.get("requestId") or f"line {number}"
        requests.setdefault(trace, []).append(LogLine(number, line, fields))
    for lines in requests.values():
        contents.records += records_of_request(lines, default_store)
    return contents


def records_of_request(lines: list[LogLine], default_store: str) -> list[RecordSeen]:
    """One record per resource the request names; the identifiers it was looked up by come along."""
    lookup_values = {name: value for line in lines for name, value in line.fields.items() if is_identifier_value(value)}
    fields_by_resource: dict[str, dict[str, str]] = {}
    last_line: dict[str, LogLine] = {}
    for line in lines:
        resource_id = line.fields.get("resource_id")
        if resource_id:
            fields_by_resource[resource_id] = fields_by_resource.get(resource_id, {}) | line.fields
            last_line[resource_id] = line
    records = []
    for resource_id, own_fields in fields_by_resource.items():
        fields = {name: value for name, value in lookup_values.items() if name not in own_fields} | own_fields
        store = next((fields[name] for name in STORE_NAMES if fields.get(name)), default_store)
        observed_at = utc_time(fields["time"])
        # A lookup that was only started shows that someone looked, not that the record exists.
        only_started = all(line.fields.get("event", "").endswith("_started") for line in lines
                           if line.fields.get("resource_id") == resource_id)
        if observed_at is not None:
            records.append(RecordSeen(store, observed_at, fields, found=None if only_started else True,
                                      excerpt=last_line[resource_id].text))
    return records


def line_fields(rest: str) -> dict[str, str]:
    if rest.startswith("{"):
        try:
            document = json.loads(rest)
        except (ValueError, RecursionError):
            document = None
        if isinstance(document, dict):
            return {str(name): text for name, value in document.items()
                    if not isinstance(value, (dict, list)) and (text := text_of(value)) is not None}
    fields: dict[str, str] = {}
    for header, names in POSITIONAL_HEADERS:
        if match := header.match(rest):
            fields |= dict(zip(names, match.groups(), strict=True))
            break
    return fields | named_values(rest)


def named_values(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for name, value in KEY_VALUE.findall(text):
        if value.startswith('"'):
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        if value == "null":
            continue
        # The cloud runtime export puts all of a line's named values into one quoted message value.
        inner = named_values(value) if name == "message" else {}
        fields |= inner or {name: value}
    return fields
