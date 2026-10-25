"""The rules that turn the fields of one record into an Observation, the same for every format.

Identifiers are recognized by the shape of their values, wherever they are, because the formats
name the same identifier in many ways (email, customer_email, lookup_key, a sentence in a message).
Names have no recognizable shape, so they are taken only from fields that are called a name.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from c00_interfaces.records import EvidenceFile, Observation

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# A hash right after "sha256:" is a checksum of a file, not of an email address.
EMAIL_HASH = re.compile(r"(?<![\w:])[0-9a-fA-F]{64}(?!\w)")
USER_REF = re.compile(r"(?<!\w)user_\d+(?!\w)")
PHONE = re.compile(r"\+\d[\d ()-]{5,}\d")
NAME_FIELDS = ("name", "full_name", "display_name", "requester_name")

# Ids of the dataset's own files and tables look like resource ids but never name a resource, and
# neither does a file name such as customer_export_7364.zip.
RESOURCE_ID = re.compile(
    r"(?<!\w)(?!(?:user|case|evidence|activity|audit|rule)_\d)[a-z]+(?:_[a-z]+)*_\d+(?!\w)(?!\.\w)")

NOT_FOUND_RESULTS = ("NOT_FOUND", "MISS")
FOUND_RESULTS = ("FOUND", "HIT", "IDENTIFIABLE", "ANONYMIZED", "REDACTED", "ACTIVE", "DISABLED", "BLOCKED")
STATUS_FIELDS = ("status_code", "http_status")
COUNT_FIELDS = ("rows", "total", "hits.total", "total_hits")
PRESENCE_FIELDS = ("archive_present", "available")
EXCERPT_LENGTH = 600


@dataclass(frozen=True)
class RecordSeen:
    """One record as a format reader found it. A source that shows a record's content shows that
    the record exists, so found is True unless the format cannot tell (a lookup that was only
    started); the record's own fields can still say that it is missing."""

    store: str
    observed_at: datetime
    fields: Mapping[str, str] = field(hash=False)
    found: bool | None = True
    excerpt: str = ""


@dataclass(frozen=True)
class ListingSeen:
    store: str
    observed_at: datetime
    resource_ids: frozenset[str]


@dataclass
class FileContents:
    records: list[RecordSeen] = field(default_factory=list)
    listings: list[ListingSeen] = field(default_factory=list)
    problems: list[tuple[str, str]] = field(default_factory=list)  # (location, message)


def observation_from(record: RecordSeen, evidence: EvidenceFile) -> Observation:
    return Observation(
        evidence_id=evidence.file_id,
        captured_at=evidence.captured_at,
        observed_at=record.observed_at,
        store=record.store,
        resource_id=record.fields["resource_id"],
        found=found_in(record.fields, record.found),
        category=record.fields.get("record_type") or None,
        identifiers=identifiers_in(record.fields),
        facts={name: value for name, value in record.fields.items()
               if name != "resource_id" and not is_identifier(name, value)},
        excerpt=(record.excerpt or "; ".join(f"{name}={value}" for name, value in record.fields.items()))[
            :EXCERPT_LENGTH],
    )


def identifiers_in(fields: Mapping[str, str]) -> dict[str, frozenset[str]]:
    found: dict[str, set[str]] = {}
    for name, value in fields.items():
        if name == "resource_id":
            continue
        if name.rsplit(".", 1)[-1] in NAME_FIELDS and value.strip():
            found.setdefault("name", set()).add(value.strip())
        for kind, pattern in (("email", EMAIL), ("email_hash", EMAIL_HASH), ("user_ref", USER_REF),
                              ("phone", PHONE)):
            for match in pattern.findall(value):
                found.setdefault(kind, set()).add(match.lower() if kind in ("email", "email_hash") else match)
    return {kind: frozenset(values) for kind, values in found.items()}


def is_identifier(name: str, value: str) -> bool:
    return name.rsplit(".", 1)[-1] in NAME_FIELDS or is_identifier_value(value)


def is_identifier_value(value: str) -> bool:
    return any(pattern.fullmatch(value) for pattern in (EMAIL, EMAIL_HASH, USER_REF, PHONE))


def found_in(fields: Mapping[str, str], found_by_format: bool | None) -> bool | None:
    """Whether the fields say that the record exists; a record that is said to be missing anywhere
    in its fields counts as missing."""
    signals = [found_by_format]
    result = fields.get("result", "").upper()
    signals.append(False if result in NOT_FOUND_RESULTS else True if result in FOUND_RESULTS else None)
    for name in STATUS_FIELDS:
        status = fields.get(name, "")
        signals.append(False if status in ("404", "410") else True if status == "200" else None)
    for name in COUNT_FIELDS:
        count = fields.get(name, "")
        signals.append((int(count) > 0) if count.isdigit() else None)
    for name in PRESENCE_FIELDS:
        presence = fields.get(name, "").lower()
        signals.append(True if presence == "true" else False if presence == "false" else None)
    if False in signals:
        return False
    return True if True in signals else None


def text_of(value: object) -> str | None:
    """A field value as text, or None when the evidence leaves it empty."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def utc_time(text: str) -> datetime | None:
    try:
        moment = datetime.fromisoformat(text.strip())
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    try:
        return moment.astimezone(UTC)
    except OverflowError:
        return None


def resource_kind(resource_id: str) -> str:
    return resource_id.rsplit("_", 1)[0]
