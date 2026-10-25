"""ARC-04_request_classifier: CHR-301, CHR-302, CHR-303, EXT-501, EXT-502."""

import unittest
from datetime import UTC, datetime
from pathlib import Path

from c00_interfaces.components import ModelError, RequestClassifier
from c00_interfaces.fakes import FakeModelGateway
from c00_interfaces.records import ModelQuestion, Request
from c01_input_reader.input_reader import read_dataset
from c04_request_classifier.request_classifier import CLASSIFICATION_INSTRUCTIONS, classify_requests

REAL_DATASET = Path(__file__).resolve().parents[2] / "dataset"
NOON = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
DELETE = "Please erase the account linked to this email address."
OPT_OUT = "Please stop the promotional emails. I still need the account, so I am not asking for deletion."
KOREAN = "이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다."


def request(case_id: str, text: str) -> Request:
    return Request(case_id, "ana@example.com", NOON, "COMPLETE", NOON, NOON, text)


def answer_by_text(question: ModelQuestion) -> str:
    if question.data == OPT_OUT:
        return '{"asks_for_deletion": false, "request_in_english": "Stop promotional emails, keep the account."}'
    return '{"asks_for_deletion": true, "request_in_english": "Delete my account."}'


def answer_with(text: str) -> FakeModelGateway:
    return FakeModelGateway(lambda question: text)


class Decisions(unittest.TestCase):
    def test_the_model_decides_and_its_reading_is_recorded_as_the_reason(self) -> None:
        decisions = classify_requests([request("case_1", DELETE), request("case_2", OPT_OUT)],
                                      FakeModelGateway(answer_by_text))
        self.assertTrue(decisions["case_1"].authorizes_deletion)
        self.assertFalse(decisions["case_2"].authorizes_deletion)
        self.assertEqual(decisions["case_2"].reason,
                         "the model reads it as: Stop promotional emails, keep the account.")

    def test_each_distinct_text_is_asked_once_on_its_own_and_only_as_data(self) -> None:
        gateway = FakeModelGateway(answer_by_text)
        decisions = classify_requests([request("case_1", DELETE), request("case_2", OPT_OUT),
                                       request("case_3", f"  {DELETE}\n"), request("case_4", KOREAN)], gateway)
        self.assertEqual([question.data for question in gateway.questions], [DELETE, OPT_OUT, KOREAN])
        for question in gateway.questions:
            self.assertEqual(question.instructions, CLASSIFICATION_INSTRUCTIONS)
            self.assertIsNone(question.image_png)
        self.assertEqual(list(decisions), ["case_1", "case_2", "case_3", "case_4"])
        self.assertEqual(decisions["case_3"].reason, decisions["case_1"].reason)

    def test_the_json_object_is_found_inside_a_code_fence_or_a_sentence(self) -> None:
        for answer in ('```json\n{"asks_for_deletion": false, "request_in_english": "A copy."}\n```',
                       'Here it is: {"asks_for_deletion": false, "request_in_english": "A copy."} Done.'):
            decision = classify_requests([request("case_1", DELETE)], answer_with(answer))["case_1"]
            self.assertFalse(decision.authorizes_deletion, answer)

    def test_an_empty_text_asks_for_nothing_and_needs_no_model(self) -> None:
        gateway = FakeModelGateway(answer_by_text)
        decision = classify_requests([request("case_1", " \n ")], gateway)["case_1"]
        self.assertFalse(decision.authorizes_deletion)
        self.assertEqual(gateway.questions, [])


class NoUsableAnswer(unittest.TestCase):
    def test_an_unusable_answer_audits_the_request_as_a_deletion_and_says_so(self) -> None:
        for answer in ("Yes, this is a deletion request.", '{"asks_for_deletion": "true", "request_in_english": "x"}',
                       '{"asks_for_deletion": false}', '{"asks_for_deletion": false, "request_in_english": " "}',
                       "[true]", '{"asks_for_deletion": tru'):
            decision = classify_requests([request("case_1", OPT_OUT)], answer_with(answer))["case_1"]
            self.assertTrue(decision.authorizes_deletion, answer)
            self.assertIn("no usable answer from the model", decision.reason)

    def test_a_failed_model_call_costs_only_its_own_text(self) -> None:
        def fail_on_korean(question: ModelQuestion) -> str:
            if question.data == KOREAN:
                raise ModelError("HTTP 503")
            return answer_by_text(question)

        decisions = classify_requests([request("case_1", KOREAN), request("case_2", OPT_OUT)],
                                      FakeModelGateway(fail_on_korean))
        self.assertTrue(decisions["case_1"].authorizes_deletion)
        self.assertIn("HTTP 503", decisions["case_1"].reason)
        self.assertFalse(decisions["case_2"].authorizes_deletion)

    def test_a_long_reading_is_cut_so_that_the_record_stays_small(self) -> None:
        answer = '{"asks_for_deletion": true, "request_in_english": "' + "very " * 200 + 'long"}'
        decision = classify_requests([request("case_1", DELETE)], answer_with(answer))["case_1"]
        self.assertLessEqual(len(decision.reason), len("the model reads it as: ") + 300)


class RealRequests(unittest.TestCase):
    def test_every_real_request_gets_one_decision_from_one_question_per_distinct_text(self) -> None:
        requests = read_dataset(REAL_DATASET).requests
        gateway = FakeModelGateway(answer_by_text)
        decisions = classify_requests(requests, gateway)
        self.assertEqual(sorted(decisions), sorted(request.case_id for request in requests))
        self.assertEqual(len(gateway.questions), 375)

    def test_the_classifier_fits_its_interface(self) -> None:
        classifier: RequestClassifier = classify_requests
        self.assertIsInstance(classifier, RequestClassifier)


if __name__ == "__main__":
    unittest.main()
