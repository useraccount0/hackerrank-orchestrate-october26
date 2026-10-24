"""Reads JSON evidence. The files use several layouts, so one walk serves them all: every object
with a resource_id is a record; it takes the nearest time and store names from the objects around
it; and a collection with a list of records is a complete listing of that collection.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from c03_evidence_reader.record_fields import FileContents, ListingSeen, RecordSeen, text_of, utc_time

TIME_FIELDS = ("observed_at", "recorded_at", "captured_at")
STORE_FIELDS = ("data_store", "system", "collection")


def records_in_json(document: object, captured_at: datetime) -> FileContents:
    contents = FileContents()
    walk(document, captured_at, (), (), contents)
    return contents


def walk(node: object, observed_at: datetime, store_names: tuple[str, ...], path: tuple[str, ...],
         contents: FileContents, listed: bool = False) -> None:
    """listed is True for the items of a complete listing: they are in the collection."""
    if isinstance(node, list):
        for item in node:
            walk(item, observed_at, store_names, path, contents, listed)
        return
    if not isinstance(node, Mapping):
        return
    observed_at = own_time(node) or observed_at
    store_names = store_names + tuple(str(node[name]) for name in STORE_FIELDS if isinstance(node.get(name), str))
    store = "/".join(store_names) or "/".join(path[-2:])
    records = node.get("records")
    is_listing = isinstance(records, list) and ("collection" in node or "data_store" in node)
    if is_listing and isinstance(records, list):
        resource_ids = frozenset(str(item["resource_id"]) for item in records
                                 if isinstance(item, Mapping) and item.get("resource_id"))
        contents.listings.append(ListingSeen(store, observed_at, resource_ids))
    if node.get("resource_id"):
        contents.records.append(RecordSeen(store, observed_at, flat_fields(node), found=True if listed else None))
        # A record nested in another one, such as a search hit, belongs to the same store.
        store_names = (store,)
    for key, value in node.items():
        walk(value, observed_at, store_names, path + (str(key),), contents, listed=is_listing and key == "records")


def own_time(node: Mapping[str, object]) -> datetime | None:
    for name in TIME_FIELDS:
        value = node.get(name)
        if isinstance(value, str) and (moment := utc_time(value)):
            return moment
    return None


def flat_fields(node: Mapping[str, object], prefix: str = "") -> dict[str, str]:
    """The record's own values as text; values of a nested object get its name as a prefix, and a
    nested object with its own resource_id is a record of its own, so it is left out."""
    fields: dict[str, str] = {}
    for key, value in node.items():
        name = prefix + str(key)
        if isinstance(value, Mapping):
            if "resource_id" not in value:
                fields |= flat_fields(value, name + ".")
        elif isinstance(value, list):
            if value and all(not isinstance(item, (Mapping, list)) for item in value):
                fields[name] = ", ".join(str(text_of(item)) for item in value)
        elif (text := text_of(value)) is not None:
            fields[name] = text
    return fields
