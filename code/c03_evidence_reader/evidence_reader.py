"""ARC-03_evidence_reader: turns every evidence file into observations and store listings.

A file that cannot be read is reported and skipped, so one bad file never stops the run (EXT-501).
Which records belong to a case, and what state they are in at audit_at, is decided later (ARC-06,
ARC-07); this component only says what each file shows.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path

from c00_interfaces.components import ModelError, ModelGateway
from c00_interfaces.records import EvidenceFile, EvidenceReading, InputProblem, Observation, StoreListing
from c03_evidence_reader.document_text import text_of_pdf, text_of_screenshot
from c03_evidence_reader.json_records import records_in_json
from c03_evidence_reader.log_lines import records_in_log
from c03_evidence_reader.record_fields import FileContents, ListingSeen, observation_from, resource_kind
from c03_evidence_reader.sql_snapshots import records_in_sql
from c03_evidence_reader.text_documents import records_in_text


def read_evidence(files: Sequence[EvidenceFile], dataset_dir: Path, gateway: ModelGateway) -> EvidenceReading:
    observations: list[Observation] = []
    listings_seen: list[tuple[EvidenceFile, ListingSeen]] = []
    problems: list[InputProblem] = []
    for evidence in files:
        try:
            contents = contents_of(evidence, dataset_dir, gateway)
        # ValueError includes text that is not UTF-8 and JSON that does not parse.
        except (OSError, ValueError, RecursionError, sqlite3.Error, ModelError) as error:
            problems.append(InputProblem(evidence.file_path, "file", f"cannot be read: {error}"))
            continue
        problems += [InputProblem(evidence.file_path, location, message) for location, message in contents.problems]
        observations += [observation_from(record, evidence) for record in contents.records]
        listings_seen += [(evidence, listing) for listing in contents.listings]
    return EvidenceReading(tuple(observations), store_listings(listings_seen, observations), tuple(problems))


def contents_of(evidence: EvidenceFile, dataset_dir: Path, gateway: ModelGateway) -> FileContents:
    path = dataset_dir / evidence.file_path
    match path.suffix.lower():
        case ".sql":
            return records_in_sql(path.read_text(encoding="utf-8"), evidence.captured_at)
        case ".json":
            return records_in_json(json.loads(path.read_text(encoding="utf-8")), evidence.captured_at)
        case ".log":
            return records_in_log(path.read_text(encoding="utf-8"), evidence.origin)
        case ".txt":
            return records_in_text(path.read_text(encoding="utf-8"), evidence.origin, evidence.captured_at)
        case ".pdf":
            return records_in_text(text_of_pdf(path), evidence.origin, evidence.captured_at)
        case ".png":
            return records_in_text(text_of_screenshot(path, gateway), evidence.origin, evidence.captured_at)
    raise ValueError(f"has a format that no reader knows ({path.suffix})")


def store_listings(listings_seen: list[tuple[EvidenceFile, ListingSeen]],
                   observations: list[Observation]) -> tuple[StoreListing, ...]:
    """One listing per kind of record that its store holds. The kinds of a store are learned from
    every file, so that a table that is empty in one snapshot still proves absence (REV-005)."""
    kinds_by_store: dict[str, set[str]] = {}
    for observation in observations:
        kinds_by_store.setdefault(observation.store, set()).add(resource_kind(observation.resource_id))
    return tuple(
        StoreListing(evidence.file_id, evidence.captured_at, listing.observed_at, listing.store, kind,
                     frozenset(resource_id for resource_id in listing.resource_ids
                               if resource_kind(resource_id) == kind))
        for evidence, listing in listings_seen
        for kind in sorted(kinds_by_store.get(listing.store, set()))
    )
