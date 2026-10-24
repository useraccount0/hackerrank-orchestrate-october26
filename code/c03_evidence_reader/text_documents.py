"""Reads text evidence: handover lines with fixed columns, and free text such as the text of a PDF
or of a screenshot, where a resource is only mentioned.
"""

from __future__ import annotations

from datetime import datetime

from c03_evidence_reader.record_fields import RESOURCE_ID, FileContents, RecordSeen, utc_time

HANDOVER_COLUMNS = ("time", "system", "resource_id", "record_type", "result", "reference")


def records_in_text(text: str, store: str, observed_at: datetime) -> FileContents:
    contents = FileContents()
    free_lines = []
    for line in text.splitlines():
        columns = [column.strip() for column in line.strip().removeprefix("-").split("|")]
        time = utc_time(columns[0])
        if len(columns) == len(HANDOVER_COLUMNS) and RESOURCE_ID.fullmatch(columns[2]) and time:
            fields = dict(zip(HANDOVER_COLUMNS, columns, strict=True))
            contents.records.append(RecordSeen(fields["system"], time, fields, excerpt=line.strip()))
        elif line.strip():
            free_lines.append(line.strip())
    contents.records += records_in_free_text(free_lines, store, observed_at)
    return contents


def records_in_free_text(lines: list[str], store: str, observed_at: datetime) -> list[RecordSeen]:
    """A record for every resource the text mentions. Its text is the lines from its mention up to
    the next mention of another resource, after the lines before the first mention, which are
    the document's heading; a document that mentions one resource is entirely about it."""
    mentions = [RESOURCE_ID.findall(line) for line in lines]
    resource_ids = list(dict.fromkeys(resource_id for found in mentions for resource_id in found))
    if len(resource_ids) == 1:
        return [free_text_record(resource_ids[0], lines, store, observed_at)]
    heading: list[str] = []
    blocks: dict[str, list[str]] = {}
    current: list[str] = []
    for line, found in zip(lines, mentions, strict=True):
        current = found or current
        if not current:
            heading.append(line)
        for resource_id in current:
            blocks.setdefault(resource_id, list(heading)).append(line)
    return [free_text_record(resource_id, block, store, observed_at) for resource_id, block in blocks.items()]


def free_text_record(resource_id: str, lines: list[str], store: str, observed_at: datetime) -> RecordSeen:
    text = "\n".join(lines)
    return RecordSeen(store, observed_at, {"resource_id": resource_id, "text": text}, excerpt=text)
