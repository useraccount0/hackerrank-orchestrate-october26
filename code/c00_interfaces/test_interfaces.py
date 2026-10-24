"""ARC-00_interfaces, EXT-602, EXT-609: every component can be replaced by a fake."""

import unittest

from c00_interfaces.components import (
    Components,
    DatasetReader,
    EvidenceReader,
    IdentityResolver,
    ModelGateway,
    PolicyChecker,
    RequestClassifier,
    ResourceFinder,
    StateReconstructor,
    StepPlanner,
)
from c00_interfaces.fakes import FakeModelGateway
from c00_interfaces.records import CaseAnswer, CaseVerdict, ModelQuestion


def plan_no_steps(verdict: CaseVerdict) -> CaseAnswer:
    return CaseAnswer(verdict.case_id, verdict.deletion_status, ())


class FakesFitTheInterfaces(unittest.TestCase):
    def test_fake_model_gateway_answers_and_records_the_question(self):
        gateway = FakeModelGateway(lambda question: f"answer for {question.purpose}")
        self.assertIsInstance(gateway, ModelGateway)
        self.assertEqual(gateway.ask(ModelQuestion("classify", "instructions", "data")), "answer for classify")
        self.assertEqual([call.purpose for call in gateway.calls()], ["classify"])

    def test_plain_functions_can_stand_in_for_every_component(self):
        stand_in = lambda *args: None  # noqa: E731 - any callable fits a call signature
        components = Components(stand_in, FakeModelGateway(str), stand_in, stand_in, stand_in, stand_in,
                                stand_in, stand_in, plan_no_steps)
        for signature, component in [
            (DatasetReader, components.read_dataset), (EvidenceReader, components.read_evidence),
            (RequestClassifier, components.classify_requests), (IdentityResolver, components.resolve_identity),
            (ResourceFinder, components.find_resources), (StateReconstructor, components.reconstruct_states),
            (PolicyChecker, components.check_policy), (StepPlanner, components.plan_steps)]:
            self.assertIsInstance(component, signature)
        verdict = CaseVerdict("case_01", "COMPLETE", ())
        self.assertEqual(components.plan_steps(verdict), CaseAnswer("case_01", "COMPLETE", ()))


if __name__ == "__main__":
    unittest.main()
