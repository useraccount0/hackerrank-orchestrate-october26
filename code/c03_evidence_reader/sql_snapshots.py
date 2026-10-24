"""Reads an SQL snapshot export: every table is a complete listing of its store at capture time."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from c03_evidence_reader.json_records import flat_fields
from c03_evidence_reader.record_fields import FileContents, ListingSeen, RecordSeen, text_of

# Loading a snapshot needs only these actions. Everything else is refused, because the file is
# data (EXT-502): an ATTACH, for example, could make SQLite write a file anywhere on disk.
LOADING_ACTIONS = (sqlite3.SQLITE_CREATE_TABLE, sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_INSERT,
                   sqlite3.SQLITE_UPDATE, sqlite3.SQLITE_READ, sqlite3.SQLITE_TRANSACTION, sqlite3.SQLITE_REINDEX)


def allow_only_loading(action: int, first: str | None, second: str | None, database: str | None,
                       trigger: str | None) -> int:
    if (action in LOADING_ACTIONS
            or (action == sqlite3.SQLITE_PRAGMA and first == "foreign_keys")
            or (action == sqlite3.SQLITE_FUNCTION and second == "json_valid")):
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def records_in_sql(text: str, captured_at: datetime) -> FileContents:
    contents = FileContents()
    database = sqlite3.connect(":memory:", autocommit=True)
    try:
        load_snapshot(database, text, contents)
        for table in table_names(database):
            read_table(database, table, captured_at, contents)
    finally:
        database.close()
    return contents


def load_snapshot(database: sqlite3.Connection, text: str, contents: FileContents) -> None:
    database.set_authorizer(allow_only_loading)
    statement = ""
    # Statement by statement, so that one statement that fails costs only itself.
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        statement += line
        if not sqlite3.complete_statement(statement):
            continue
        try:
            database.execute(statement)
        except sqlite3.Error as error:
            contents.problems.append((f"line {line_number}", f"statement skipped ({error})"))
        statement = ""
    database.set_authorizer(None)


def table_names(database: sqlite3.Connection) -> list[str]:
    return [name for (name,) in database.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")]


def read_table(database: sqlite3.Connection, table: str, captured_at: datetime, contents: FileContents) -> None:
    quoted_name = '"' + table.replace('"', '""') + '"'
    cursor = database.execute(f"SELECT * FROM {quoted_name}")
    columns = [description[0] for description in cursor.description]
    if "resource_id" not in columns:
        return
    resource_ids = set()
    for row in cursor:
        fields = {column: text for column, value in zip(columns, row, strict=True)
                  if (text := text_of(value)) is not None}
        if "record_json" in fields:
            try:
                fields = fields | flat_fields(json.loads(fields.pop("record_json")))
            except (ValueError, RecursionError):
                contents.problems.append((f"table {table}", "a record_json value is not JSON; its row is skipped"))
                continue
        if fields.get("resource_id"):
            resource_ids.add(fields["resource_id"])
            contents.records.append(RecordSeen(table, captured_at, fields, found=True))
    contents.listings.append(ListingSeen(table, captured_at, frozenset(resource_ids)))
