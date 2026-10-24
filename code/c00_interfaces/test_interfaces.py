"""ARC-00_interfaces: EXT-602, EXT-609, REV-005, CHR-416 to CHR-432."""

import dataclasses
import re
import unittest
from datetime import datetime, timezone
from pathlib import Path

from c00_interfaces.fakes import FakeModelGateway, fake_components
from c00_interfaces.records import OPERATIONS, PHASES, CaseAnswer, CaseVerdict, ModelQuestion, Observation

PROBLEM_STATEMENT = Path(__file__).resolve().parents[2] / "problem_statement.md"
NOON = datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)


class InterfacesCanBeMocked(unittest.TestCase):
    def test_fake_model_gateway_answers_and_records_the_question(self) -> None:
        gateway = FakeModelGateway(lambda question: f"answer for {question.purpose}")
        self.assertEqual(gateway.ask(ModelQuestion("classify", "instructions", "data")), "answer for classify")
        self.assertEqual([call.purpose for call in gateway.calls()], ["classify"])

    def test_a_bundle_of_fakes_stands_in_for_every_component(self) -> None:
        components = fake_components()
        verdict = components.check_policy("case_01", (), (), NOON)
        self.assertEqual(components.plan_steps(verdict), CaseAnswer("case_01", "COMPLETE", ()))


class RecordsAreSafeToShare(unittest.TestCase):
    def test_a_record_cannot_be_changed_after_it_is_made(self) -> None:
        verdict = CaseVerdict("case_01", "COMPLETE", ())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            verdict.deletion_status = "INCOMPLETE"  # type: ignore[misc]

    def test_records_with_identifiers_and_facts_stay_hashable(self) -> None:
        seen = Observation("evidence_01", NOON, NOON, "customer_profiles", "account_001", True,
                           identifiers={"email": "a@example.com"}, facts={"account_status": "ACTIVE"})
        same = Observation("evidence_01", NOON, NOON, "customer_profiles", "account_001", True,
                           identifiers={"email": "a@example.com"}, facts={"account_status": "ACTIVE"})
        self.assertEqual(len({seen, same}), 1)


class OperationsMatchTheProblemStatement(unittest.TestCase):
    def test_operations_phases_states_and_their_order_are_the_published_table(self) -> None:
        row = re.compile(r"^\| `(\w+)` \| `(\w+)` \| `(\w+)` \|")
        table = [match.groups() for line in PROBLEM_STATEMENT.read_text(encoding="utf-8").splitlines()
                 if (match := row.match(line))]
        self.assertEqual(table, [(phase, operation, state) for operation, (phase, state) in OPERATIONS.items()])
        self.assertEqual(tuple(dict.fromkeys(phase for phase, _ in OPERATIONS.values())), PHASES)


if __name__ == "__main__":
    unittest.main()
