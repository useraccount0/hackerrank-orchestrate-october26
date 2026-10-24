"""ARC-01_input_reader: CHR-201 to CHR-218, CHR-504, EXT-501, EXT-503, REV-006."""

import csv
import dataclasses
import io
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from c00_interfaces.records import (
    Activity,
    CaseAnswer,
    Dataset,
    DeletionRule,
    EvidenceFile,
    IdentityChange,
    IdentityRecord,
    Request,
    Step,
)
from c01_input_reader.input_reader import read_dataset

REAL_DATASET = Path(__file__).resolve().parents[2] / "dataset"

REQUEST_HEADER = "case_id,email,requested_at,reported_status,reported_at,audit_at,request_text\n"
REQUEST_01 = ("case_01,ana@example.com,2026-08-18T09:14:00Z,COMPLETE,2026-08-20T16:42:00Z,2026-09-03T11:30:00Z,"
              "\"Delete it, please.\"\n")
REQUEST_02 = ("case_02,bo@example.com,2026-08-19T10:00:00Z,NOT_STARTED,2026-08-21T10:00:00Z,2026-09-04T10:00:00Z,"
              "Erase my data.\n")
VERIFY_STEP = Step(1, "VERIFICATION", "account_service", "account_001", "VERIFY_RECORD_ABSENT", "ABSENT", "evidence_01")
STEP = dataclasses.asdict(VERIFY_STEP)
EVIDENCE_HEADER = "file_id,file_path,origin,captured_at\n"


def utc(text: str) -> datetime:
    return datetime.fromisoformat(text).replace(tzinfo=UTC)


def answer_line(case_id: str, status: str, steps: object) -> str:
    line = io.StringIO()
    csv.writer(line, lineterminator="\n").writerow([case_id, status, json.dumps(steps)])
    return line.getvalue()


def evidence_line(file_id: str, file_path: str) -> str:
    return f"{file_id},{file_path},central_observability_export,2026-09-01T12:00:00Z\n"


SMALL_DATASET = {
    "deletion_requests.csv": REQUEST_HEADER + REQUEST_01 + REQUEST_02,
    "sample_deletion_requests.csv": REQUEST_HEADER + REQUEST_01,
    "sample_output.csv": "case_id,deletion_status,steps_json\n" + answer_line("case_01", "COMPLETE", [STEP]),
    "user_identities.csv": "user_id,name,email,phone,email_hash,updated_at\n"
                           "user_01,Ana Example,ana@example.com,+1 555 0100,0a1b2c,2026-05-28T04:03:00Z\n",
    "user_audit_log.csv": "audit_id,user_id,event_time,field_name,old_value,new_value\n"
                          "audit_01,user_01,2025-01-01T00:00:00Z,phone,+1 555 0199,+1 555 0100\n",
    "system_activity.csv": "activity_id,event_time,event_type,source_system,target_system,resource_id,"
                           "reported_result,details\n"
                           "activity_01,2026-08-20T16:40:00Z,DELETE_RECORD,deletion_worker,account_service,"
                           "account_001,SUCCESS,Deleted account_001.\n",
    "deletion_rules.csv": "rule_id,data_category,condition,required_action\nrule_01,USER_PROFILE,Always,DELETE\n",
    "evidence_files.csv": EVIDENCE_HEADER + evidence_line("evidence_01", "evidence/logs/events.log"),
}


def problem_texts(dataset: Dataset) -> list[str]:
    return [f"{problem.source} {problem.location}: {problem.message}" for problem in dataset.problems]


class ReadsTheRealDataset(unittest.TestCase):
    @unittest.skipUnless(REAL_DATASET.is_dir(), "dataset/ is not part of code.zip")
    def test_every_row_of_the_real_dataset_is_read_without_problems(self) -> None:
        dataset = read_dataset(REAL_DATASET)
        self.assertEqual(dataset.problems, ())
        self.assertEqual(dataset.unreadable_case_ids, ())
        counts = [len(dataset.requests), len(dataset.sample_requests), len(dataset.sample_answers),
                  len(dataset.identities), len(dataset.identity_changes), len(dataset.activities),
                  len(dataset.rules), len(dataset.evidence_files)]
        self.assertEqual(counts, [518, 32, 32, 850, 306, 4011, 15, 94])
        self.assertTrue(all(request.audit_at.tzinfo == UTC for request in dataset.requests))


class SmallDatasetTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        for name, text in SMALL_DATASET.items():
            (self.folder / name).write_text(text, encoding="utf-8")
        (self.folder / "evidence" / "logs").mkdir(parents=True)
        (self.folder / "evidence" / "logs" / "events.log").write_text("event\n", encoding="utf-8")

    def read_with(self, name: str, text: str) -> Dataset:
        (self.folder / name).write_text(text, encoding="utf-8")
        return read_dataset(self.folder)


class ReadsValuesIntoRecords(SmallDatasetTest):
    def test_each_value_lands_in_its_field(self) -> None:
        dataset = read_dataset(self.folder)
        self.assertEqual(dataset.problems, ())
        self.assertEqual(dataset.requests[0], Request("case_01", "ana@example.com", utc("2026-08-18T09:14:00"),
                                                      "COMPLETE", utc("2026-08-20T16:42:00"),
                                                      utc("2026-09-03T11:30:00"), "Delete it, please."))
        self.assertEqual(dataset.sample_requests, dataset.requests[:1])
        self.assertEqual(dataset.sample_answers, (CaseAnswer("case_01", "COMPLETE", (VERIFY_STEP,)),))
        self.assertEqual(dataset.identities, (IdentityRecord("user_01", "Ana Example", "ana@example.com", "+1 555 0100",
                                                             "0a1b2c", utc("2026-05-28T04:03:00")),))
        self.assertEqual(dataset.identity_changes, (IdentityChange("audit_01", "user_01", utc("2025-01-01T00:00:00"),
                                                                   "phone", "+1 555 0199", "+1 555 0100"),))
        self.assertEqual(dataset.activities, (Activity("activity_01", utc("2026-08-20T16:40:00"), "DELETE_RECORD",
                                                       "deletion_worker", "account_service", "account_001", "SUCCESS",
                                                       "Deleted account_001."),))
        self.assertEqual(dataset.rules, (DeletionRule("rule_01", "USER_PROFILE", "Always", "DELETE"),))
        self.assertEqual(dataset.evidence_files, (EvidenceFile("evidence_01", "evidence/logs/events.log",
                                                               "central_observability_export",
                                                               utc("2026-09-01T12:00:00")),))

    def test_times_become_utc_and_spaces_around_values_are_trimmed(self) -> None:
        row = (" case_03 , cy@example.com ,2026-08-18T11:14:00+02:00,COMPLETE,2026-08-20T16:42:00Z,"
               "2026-09-03T11:30:00Z,x\n")
        request = self.read_with("deletion_requests.csv", REQUEST_HEADER + row).requests[0]
        self.assertEqual((request.case_id, request.email), ("case_03", "cy@example.com"))
        self.assertEqual(request.requested_at, datetime(2026, 8, 18, 9, 14, tzinfo=UTC))

    def test_an_empty_request_text_is_kept_for_the_classifier_to_judge(self) -> None:
        row = REQUEST_02.replace("Erase my data.", "")
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + row)
        self.assertEqual(dataset.requests[0].request_text, "")
        self.assertEqual(dataset.problems, ())

    def test_a_byte_order_mark_and_windows_line_endings_are_accepted(self) -> None:
        (self.folder / "deletion_rules.csv").write_bytes(b"\xef\xbb\xbfrule_id,data_category,condition,"
                                                         b"required_action\r\nrule_01,USER_PROFILE,Always,DELETE\r\n")
        dataset = read_dataset(self.folder)
        self.assertEqual(dataset.problems, ())
        self.assertEqual(dataset.rules[0].required_action, "DELETE")

    def test_a_value_longer_than_the_csv_default_limit_is_read(self) -> None:
        row = REQUEST_02.replace("Erase my data.", "x" * 200_000)
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + row)
        self.assertEqual(len(dataset.requests[0].request_text), 200_000)


class SkipsAndReportsBadRows(SmallDatasetTest):
    def test_a_request_row_that_fails_a_check_still_passes_on_its_case(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + REQUEST_01
                                 + REQUEST_02.replace("2026-09-04T10:00:00Z", "soon"))
        self.assertEqual([request.case_id for request in dataset.requests], ["case_01"])
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))
        self.assertEqual(problem_texts(dataset), ["deletion_requests.csv line 3: audit_at is not a time"])

    def test_a_time_without_a_time_zone_is_not_guessed(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER
                                 + REQUEST_02.replace("2026-09-04T10:00:00Z", "2026-09-04T10:00:00"))
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))
        self.assertEqual(problem_texts(dataset), ["deletion_requests.csv line 2: audit_at has no time zone"])

    def test_a_time_that_leaves_the_calendar_in_utc_does_not_stop_the_run(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER
                                 + REQUEST_01.replace("2026-08-18T09:14:00Z", "0001-01-01T00:00:00+05:00")
                                 + REQUEST_02.replace("2026-09-04T10:00:00Z", "9999-12-31T23:59:59-05:00"))
        self.assertEqual(dataset.unreadable_case_ids, ("case_01", "case_02"))
        self.assertEqual([problem.message for problem in dataset.problems],
                         ["requested_at is not a possible time in UTC", "audit_at is not a possible time in UTC"])

    def test_an_unknown_reported_status_is_rejected(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + REQUEST_02.replace("NOT_STARTED", "DONE"))
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))

    def test_an_unknown_rule_action_is_rejected(self) -> None:
        dataset = self.read_with("deletion_rules.csv", "rule_id,data_category,condition,required_action\n"
                                                       "rule_01,USER_PROFILE,Always,KEEP_FOREVER\n")
        self.assertEqual(dataset.rules, ())
        self.assertEqual(problem_texts(dataset), ["deletion_rules.csv line 2: required_action is not one of "
                                                  "DELETE, REDACT, ANONYMIZE, RETAIN"])

    def test_an_audit_time_before_the_request_is_rejected(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER
                                 + REQUEST_02.replace("2026-09-04T10:00:00Z", "2026-08-01T10:00:00Z"))
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))

    def test_a_row_with_too_many_values_is_skipped_but_keeps_its_case(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + REQUEST_02.replace("Erase my", "Erase, my"))
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))
        self.assertEqual(problem_texts(dataset),
                         ["deletion_requests.csv line 2: has 8 values, but the header has 7 columns"])

    def test_a_space_before_a_quoted_value_is_accepted(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER
                                 + REQUEST_02.replace(",Erase my data.", ", \"Erase, my data.\""))
        self.assertEqual([request.request_text for request in dataset.requests], ["Erase, my data."])

    def test_a_stray_quote_cannot_swallow_the_rows_after_it(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER
                                 + REQUEST_01.replace("\"Delete it, please.\"", "\"Delete it") + REQUEST_02)
        self.assertEqual([request.case_id for request in dataset.requests], ["case_01", "case_02"])

    def test_a_repeated_id_keeps_the_first_row(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER + REQUEST_02
                                 + REQUEST_02.replace("bo@example.com", "eve@example.com"))
        self.assertEqual([request.email for request in dataset.requests], ["bo@example.com"])
        self.assertEqual(problem_texts(dataset),
                         ["deletion_requests.csv line 3: repeats case_id case_02; the first row is kept"])

    def test_a_missing_required_column_is_reported_and_its_cases_are_kept(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER.replace(",audit_at", "")
                                 + REQUEST_02.replace(",2026-09-04T10:00:00Z", ""))
        self.assertEqual(dataset.unreadable_case_ids, ("case_02",))
        self.assertEqual(problem_texts(dataset),
                         ["deletion_requests.csv line 1: has no column audit_at; its values count as empty",
                          "deletion_requests.csv line 2: audit_at is empty"])

    def test_a_missing_column_that_may_be_empty_costs_no_rows(self) -> None:
        header, row = SMALL_DATASET["system_activity.csv"].splitlines()
        dataset = self.read_with("system_activity.csv", header.replace(",details", "") + "\n"
                                 + row.replace(",Deleted account_001.", "") + "\n")
        self.assertEqual([(activity.activity_id, activity.details) for activity in dataset.activities],
                         [("activity_01", "")])
        self.assertEqual(problem_texts(dataset),
                         ["system_activity.csv line 1: has no column details; its values count as empty"])

    def test_a_repeated_column_is_reported(self) -> None:
        dataset = self.read_with("deletion_requests.csv", REQUEST_HEADER.replace("\n", ",audit_at\n")
                                 + REQUEST_02.replace("\n", ",2030-01-01T00:00:00Z\n"))
        self.assertEqual(problem_texts(dataset),
                         ["deletion_requests.csv line 1: repeats column audit_at; only the last copy is read"])

    def test_sample_answers_must_follow_the_published_step_format(self) -> None:
        broken_answers = [
            answer_line("case_02", "COMPLETE", [{**STEP, "operation": "DELETE_EVERYTHING"}]),
            answer_line("case_03", "COMPLETE", [{**STEP, "state": "PRESENT"}]),
            answer_line("case_04", "COMPLETE", [{**STEP, "step_no": True}]),
            answer_line("case_05", "COMPLETE", [{**STEP, "step_no": 2}]),
            answer_line("case_06", "COMPLETE", [{**STEP, "note": "extra field"}]),
            answer_line("case_07", "COMPLETE", {"steps": [STEP]}),
            "case_08,COMPLETE," + "[" * 100_000 + "]" * 100_000 + "\n",
            "case_09,COMPLETE,not json\n",
            answer_line("case_10", "MAYBE", []),
        ]
        dataset = self.read_with("sample_output.csv", SMALL_DATASET["sample_output.csv"] + "".join(broken_answers))
        self.assertEqual([answer.case_id for answer in dataset.sample_answers], ["case_01"])
        self.assertEqual(len(dataset.problems), len(broken_answers))


class ProtectsTheFiles(SmallDatasetTest):
    def test_evidence_paths_cannot_lead_outside_the_evidence_folder(self) -> None:
        (self.folder / "evidence" / "notes.txt").write_text("note\n", encoding="utf-8")
        paths = ["../deletion_rules.csv", "evidence/../deletion_rules.csv", str(self.folder / "deletion_rules.csv"),
                 "evidence/logs/missing.log", "evidence/logs", "evidence/notes.txt"]
        lines = [evidence_line(f"evidence_{number}", path) for number, path in enumerate(paths, start=1)]
        dataset = self.read_with("evidence_files.csv", EVIDENCE_HEADER + "".join(lines))
        self.assertEqual([file.file_path for file in dataset.evidence_files], ["evidence/notes.txt"])
        self.assertEqual(len(dataset.problems), 5)

    def test_a_missing_file_is_reported_and_the_other_files_are_still_read(self) -> None:
        (self.folder / "user_audit_log.csv").unlink()
        dataset = read_dataset(self.folder)
        self.assertEqual(dataset.identity_changes, ())
        self.assertEqual(len(dataset.requests), 2)
        self.assertEqual([problem.source for problem in dataset.problems], ["user_audit_log.csv"])

    def test_an_empty_file_is_reported(self) -> None:
        dataset = self.read_with("deletion_rules.csv", "")
        self.assertEqual(problem_texts(dataset), ["deletion_rules.csv file: is empty"])

    def test_bytes_that_are_not_utf8_cost_only_their_own_value(self) -> None:
        (self.folder / "deletion_requests.csv").write_bytes(
            (REQUEST_HEADER + REQUEST_01 + REQUEST_02).encode().replace(b"Erase", b"\xff"))
        dataset = read_dataset(self.folder)
        self.assertEqual([request.case_id for request in dataset.requests], ["case_01", "case_02"])
        self.assertEqual(dataset.requests[1].request_text, "� my data.")
        self.assertEqual([problem.message for problem in dataset.problems],
                         ["is not UTF-8; unreadable bytes were replaced"])


if __name__ == "__main__":
    unittest.main()
