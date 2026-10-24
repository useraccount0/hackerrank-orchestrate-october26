"""ARC-03_evidence_reader: CHR-218, CHR-220, CHR-221, CHR-308, CHR-310, CHR-311, EXT-406, EXT-501, EXT-502,
REV-001, REV-005."""

import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from c00_interfaces.components import ModelError
from c00_interfaces.fakes import FakeModelGateway
from c00_interfaces.records import EvidenceFile, ModelQuestion
from c01_input_reader.input_reader import read_dataset
from c03_evidence_reader.evidence_reader import read_evidence
from c03_evidence_reader.json_records import records_in_json
from c03_evidence_reader.log_lines import records_in_log
from c03_evidence_reader.record_fields import RecordSeen, found_in, identifiers_in, observation_from
from c03_evidence_reader.sql_snapshots import records_in_sql
from c03_evidence_reader.text_documents import records_in_text

REAL_DATASET = Path(__file__).resolve().parents[2] / "dataset"
NOON = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
HASH = "d4e1f59abcf9a1e0cfdc7c27ad6c07ed4ff88b326a16ed5eed5ec6bc31618c93"


def refuse(question: ModelQuestion) -> str:
    raise ModelError("no model in tests")


def evidence(file_id: str, file_path: str) -> EvidenceFile:
    return EvidenceFile(file_id, file_path, "test_origin", NOON)


class IdentifiersAndExistence(unittest.TestCase):
    def test_identifiers_are_recognized_by_their_shape_wherever_they_are(self) -> None:
        found = identifiers_in({"resource_id": "support_001", "message_text": "Send it to Ana.Lima@Example.com today",
                                "subject_reference": "user_26", "lookup_value": HASH.upper(),
                                "owner_phone": "+55 41 90257-9346", "full_name": "Ana Lima"})
        self.assertEqual(found, {"email": frozenset({"ana.lima@example.com"}), "user_ref": frozenset({"user_26"}),
                                 "email_hash": frozenset({HASH}), "phone": frozenset({"+55 41 90257-9346"}),
                                 "name": frozenset({"Ana Lima"})})

    def test_a_file_checksum_is_not_an_email_hash(self) -> None:
        self.assertEqual(identifiers_in({"integrity_seal": "sha256:" + HASH}), {})

    def test_one_record_can_hold_several_emails(self) -> None:
        found = identifiers_in({"lookup_key": "old@example.com", "correlation_key": "new@example.com"})
        self.assertEqual(found, {"email": frozenset({"old@example.com", "new@example.com"})})

    def test_existence_follows_the_fields_and_a_missing_signal_wins(self) -> None:
        self.assertIs(found_in({"status_code": "404"}, None), False)
        self.assertIs(found_in({"result": "NOT_FOUND"}, None), False)
        self.assertIs(found_in({"rows": "0", "http_status": "200"}, None), False)
        self.assertIs(found_in({"result": "IDENTIFIABLE"}, None), True)
        self.assertIs(found_in({"hits.total": "1"}, None), True)
        self.assertIs(found_in({"enabled": "false"}, True), True)
        self.assertIsNone(found_in({"event": "message_pii_scan"}, None))

    def test_identifier_fields_become_identifiers_and_the_rest_facts(self) -> None:
        record = RecordSeen("customer_profiles", NOON, {"resource_id": "account_001", "email": "A@EXAMPLE.COM",
                                                        "account_status": "ACTIVE", "record_type": "USER_PROFILE"})
        observation = observation_from(record, evidence("evidence_01", "evidence/databases/x.sql"))
        self.assertEqual(observation.identifiers, {"email": frozenset({"a@example.com"})})
        self.assertEqual(observation.facts, {"account_status": "ACTIVE", "record_type": "USER_PROFILE"})
        self.assertEqual(observation.category, "USER_PROFILE")


class SqlSnapshots(unittest.TestCase):
    SNAPSHOT = """BEGIN TRANSACTION;
CREATE TABLE customer_profiles (resource_id TEXT PRIMARY KEY, email TEXT, account_status TEXT);
INSERT INTO customer_profiles VALUES('account_001', 'a@example.com', 'ACTIVE');
CREATE TABLE customer_data_primary (resource_id TEXT, record_json TEXT CHECK (json_valid(record_json)));
INSERT INTO customer_data_primary VALUES('analytics_7',
    '{"resource_id": "analytics_7", "user_id": "user_7", "metrics": {"sessions": 3}}');
COMMIT;
"""

    def test_every_row_is_a_record_and_every_table_a_complete_listing(self) -> None:
        contents = records_in_sql(self.SNAPSHOT, NOON)
        self.assertEqual([(record.store, record.fields["resource_id"], record.found) for record in contents.records],
                         [("customer_data_primary", "analytics_7", True), ("customer_profiles", "account_001", True)])
        self.assertEqual(contents.records[0].fields["metrics.sessions"], "3")
        self.assertEqual({listing.store: listing.resource_ids for listing in contents.listings},
                         {"customer_data_primary": {"analytics_7"}, "customer_profiles": {"account_001"}})

    def test_a_snapshot_cannot_make_sqlite_write_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "written.db"
            contents = records_in_sql(f"ATTACH DATABASE '{target}' AS other;\n" + self.SNAPSHOT, NOON)
            self.assertFalse(target.exists())
        self.assertEqual(len(contents.records), 2)
        self.assertIn("not authorized", contents.problems[0][1])

    def test_a_statement_that_fails_costs_only_itself(self) -> None:
        broken = self.SNAPSHOT.replace("COMMIT;", "INSERT INTO missing_table VALUES(1);\nCOMMIT;")
        contents = records_in_sql(broken, NOON)
        self.assertEqual(len(contents.records), 2)
        self.assertEqual(len(contents.problems), 1)


class JsonRecords(unittest.TestCase):
    def test_a_snapshot_collection_is_a_complete_listing_at_its_own_time(self) -> None:
        bundle = {"exported_at": "2026-09-17T12:00:00Z", "snapshots": [
            {"captured_at": "2026-09-09T12:00:00Z", "data_store": "account_service", "collection": "customer_profiles",
             "records": [{"resource_id": "account_5", "email": "e@example.com"}]}]}
        contents = records_in_json(bundle, NOON)
        record = contents.records[0]
        self.assertEqual((record.store, record.observed_at, record.found),
                         ("account_service/customer_profiles", datetime(2026, 9, 9, 12, tzinfo=UTC), True))
        self.assertEqual(contents.listings[0].resource_ids, {"account_5"})

    def test_lookups_say_whether_a_record_exists_and_hits_keep_their_store(self) -> None:
        export = {"service_exports": {
            "account_service": {"profile_lookups": [
                {"observed_at": "2026-09-15T09:31:40Z", "profile": None, "resource_id": "account_9",
                 "status_code": 404}]},
            "search_service": {"index_queries": [
                {"query": "n@example.com", "resource_id": "search_3", "hits": {"total": 1, "documents": [
                    {"resource_id": "search_3", "email": "n@example.com"}]}}]}}}
        records = records_in_json(export, NOON).records
        self.assertEqual([(record.store, record.fields["resource_id"]) for record in records],
                         [("account_service/profile_lookups", "account_9"),
                          ("search_service/index_queries", "search_3"), ("search_service/index_queries", "search_3")])
        self.assertIs(found_in(records[0].fields, records[0].found), False)
        self.assertIs(found_in(records[1].fields, records[1].found), True)

    def test_a_ledger_of_lookup_results_is_not_a_listing(self) -> None:
        ledger = {"records": [{"recorded_at": "2026-08-12T09:00:00Z", "system": "account_service",
                               "resource_id": "account_1", "result": "NOT_FOUND",
                               "subject_reference": "x@example.com"}]}
        contents = records_in_json(ledger, NOON)
        self.assertEqual(contents.listings, [])
        self.assertIsNone(contents.records[0].found)
        self.assertEqual(contents.records[0].store, "account_service")


class LogLines(unittest.TestCase):
    def test_a_lookup_key_reaches_the_resource_found_by_the_same_trace(self) -> None:
        log = ("2026-09-15T08:51:45Z level=DEBUG service=search_service trace_id=tr-1 event=index_query_started "
               "match_key=\"Old@Example.com\"\n"
               "2026-09-15T08:51:55Z level=DEBUG service=search_service trace_id=tr-1 event=cache_lookup result=miss\n"
               "2026-09-15T08:51:57Z level=INFO service=search_service trace_id=tr-1 resource_id=search_8 "
               "event=index_query_completed rows=1\n"
               "2026-09-15T08:52:00Z level=INFO service=search_service trace_id=tr-2 resource_id=search_9 rows=0\n")
        records = records_in_log(log, "default").records
        self.assertEqual([record.fields["resource_id"] for record in records], ["search_8", "search_9"])
        self.assertEqual(identifiers_in(records[0].fields), {"email": frozenset({"old@example.com"})})
        self.assertIs(found_in(records[0].fields, None), True)
        self.assertIs(found_in(records[1].fields, None), False)

    def test_every_line_format_gives_its_named_values(self) -> None:
        lines = [
            '2026-06-08T06:52:09Z requestId=tr-3 level=INFO function=search_service '
            'message="resource_id=\\"search_021\\" result=\\"hit\\""',
            '2026-09-10T08:56:20Z {"service":"account_service","trace_id":"tr-4","resource_id":"account_6633",'
            '"http_status":"200"}',
            '2026-07-28T05:51:21Z [INFO] [account_service] [tr-5] profile_lookup_completed: resource_id="account_7947" '
            'http_status="404"',
            '2026-07-03T07:51:32Z | DEBUG | security_service | tr-6 | audit_record_read_completed | '
            'resource_id="audit_record_4413" rows="1"',
            '2026-08-22T10:51:17Z <15>1 node-1 account_service tr-7 - - level=DEBUG resource_id="account_1785" '
            'rows="1"',
        ]
        records = records_in_log("\n".join(lines), "default").records
        read = [(record.store, record.fields["resource_id"], found_in(record.fields, None)) for record in records]
        self.assertEqual(read,
                         [("search_service", "search_021", True), ("account_service", "account_6633", True),
                          ("account_service", "account_7947", False), ("security_service", "audit_record_4413", True),
                          ("account_service", "account_1785", True)])

    def test_a_line_without_a_time_is_reported(self) -> None:
        contents = records_in_log("continued text without a time\n", "default")
        self.assertEqual(contents.problems, [("line 1", "has no time at its start; skipped")])


class TextDocuments(unittest.TestCase):
    def test_a_handover_line_is_read_by_its_columns(self) -> None:
        text = "- 2026-10-01T12:00:00Z | search_service | search_052 | SEARCH_INDEX_ENTRY | FOUND | n@example.com\n"
        record = records_in_text(text, "handover", NOON).records[0]
        self.assertEqual((record.store, record.fields["record_type"], record.fields["result"]),
                         ("search_service", "SEARCH_INDEX_ENTRY", "FOUND"))

    def test_a_document_about_one_resource_gives_it_every_identifier(self) -> None:
        text = "DELIVERY CORRECTION\nreference CS-4827 / support_001\nPriya Raman\npriya@example.com\n+91 98765 73142"
        record = records_in_text(text, "support_platform", NOON).records[0]
        self.assertEqual(record.fields["resource_id"], "support_001")
        self.assertEqual(identifiers_in(record.fields), {"email": frozenset({"priya@example.com"}),
                                                         "phone": frozenset({"+91 98765 73142"})})

    def test_each_resource_of_a_table_gets_the_identifiers_of_its_own_rows(self) -> None:
        text = ("Customer-platform archives\nbackup_9291 blue@example.com ap-southeast-1\n"
                "backup_9287 areed@example.com eu-west-1\nAccount areed@example.com")
        records = records_in_text(text, "backup_service", NOON).records
        self.assertEqual({record.fields["resource_id"]: identifiers_in(record.fields)["email"] for record in records},
                         {"backup_9291": {"blue@example.com"}, "backup_9287": {"areed@example.com"}})
        self.assertTrue(records[0].fields["text"].startswith("Customer-platform archives"))


class EvidenceFiles(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        (self.folder / "evidence").mkdir()

    def write(self, name: str, content: str | bytes) -> EvidenceFile:
        path = self.folder / "evidence" / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return evidence(f"evidence_{name.split('.')[0]}", f"evidence/{name}")

    def test_a_file_that_cannot_be_read_is_reported_and_the_others_are_read(self) -> None:
        files = [self.write("1.json", "{not json"), self.write("2.json", json.dumps({"resource_id": "account_1"})),
                 self.write("3.csv", "a,b"), self.write("4.png", b"not a png")]
        reading = read_evidence(files, self.folder, FakeModelGateway(refuse))
        self.assertEqual([observation.resource_id for observation in reading.observations], ["account_1"])
        self.assertEqual([problem.source for problem in reading.problems],
                         ["evidence/1.json", "evidence/3.csv", "evidence/4.png"])

    def test_a_screenshot_is_read_from_the_text_the_model_wrote_down(self) -> None:
        screenshot = self.write("5.png", b"\x89PNG\r\n\x1a\nimage bytes")
        gateway = FakeModelGateway(lambda question: "Customer page\nuser_11 · account_5762\nEmail h@example.com")
        reading = read_evidence([screenshot], self.folder, gateway)
        read = [(observation.resource_id, dict(observation.identifiers)) for observation in reading.observations]
        self.assertEqual(read, [("account_5762", {"user_ref": frozenset({"user_11"}),
                                                  "email": frozenset({"h@example.com"})})])
        self.assertEqual(gateway.questions[0].image_png, b"\x89PNG\r\n\x1a\nimage bytes")

    def test_a_model_that_cannot_answer_costs_only_its_screenshot(self) -> None:
        reading = read_evidence([self.write("6.png", b"\x89PNG\r\n\x1a\n")], self.folder, FakeModelGateway(refuse))
        self.assertEqual([problem.message for problem in reading.problems], ["cannot be read: no model in tests"])

    def test_an_empty_table_proves_absence_for_the_kinds_its_store_holds_elsewhere(self) -> None:
        table = "CREATE TABLE customer_profiles (resource_id TEXT);\n"
        files = [self.write("7.sql", table + "INSERT INTO customer_profiles VALUES('account_1');\n"),
                 self.write("8.sql", table)]
        listings = read_evidence(files, self.folder, FakeModelGateway(refuse)).listings
        self.assertEqual([(listing.evidence_id, listing.resource_kind, listing.resource_ids) for listing in listings],
                         [("evidence_7", "account", {"account_1"}), ("evidence_8", "account", frozenset())])


@unittest.skipUnless(REAL_DATASET.is_dir(), "dataset/ is not part of code.zip")
class ReadsTheRealEvidence(unittest.TestCase):
    def test_every_evidence_citation_of_the_sample_answers_is_explained_by_the_reading(self) -> None:
        dataset = read_dataset(REAL_DATASET)
        reading = read_evidence(dataset.evidence_files, REAL_DATASET, FakeModelGateway(refuse))
        self.assertEqual({problem.source.rsplit(".", 1)[1] for problem in reading.problems}, {"png"})
        seen = {(observation.evidence_id, observation.resource_id) for observation in reading.observations}
        proves_absence = {(listing.evidence_id, listing.resource_kind) for listing in reading.listings}
        unexplained = [
            (answer.case_id, step.resource_id, step.evidence_id)
            for answer in dataset.sample_answers for step in answer.steps if step.evidence_id
            and (step.evidence_id, step.resource_id) not in seen
            and not (step.state == "ABSENT"
                     and (step.evidence_id, step.resource_id.rsplit("_", 1)[0]) in proves_absence)
        ]
        self.assertEqual(unexplained, [])

    def test_the_text_of_a_pdf_is_read_with_pypdf(self) -> None:
        dataset = read_dataset(REAL_DATASET)
        pdf = [file for file in dataset.evidence_files if file.file_id == "evidence_58"]
        observation = read_evidence(pdf, REAL_DATASET, FakeModelGateway(refuse)).observations[0]
        self.assertEqual((observation.resource_id, observation.identifiers["email"]),
                         ("support_001", frozenset({"priya.raman@gmail.com"})))


if __name__ == "__main__":
    unittest.main()
