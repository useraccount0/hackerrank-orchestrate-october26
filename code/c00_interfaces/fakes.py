"""Stand-ins for tests, so that no test needs a real AI model or another component's code.

The fake components have the exact signatures of components.py; the type checker (mypy) proves
that they fit, so a test that uses them also proves that the interfaces can be mocked.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path

from c00_interfaces.components import Components, ModelGateway
from c00_interfaces.records import (
    Activity,
    CaseAnswer,
    CaseVerdict,
    Dataset,
    DeletionRule,
    EvidenceFile,
    EvidenceReading,
    Identity,
    IdentityChange,
    IdentityRecord,
    ModelCall,
    ModelQuestion,
    Observation,
    Request,
    RequestDecision,
    Resource,
    ResourceState,
)


class FakeModelGateway:
    def __init__(self, answer_for: Callable[[ModelQuestion], str]):
        self.answer_for = answer_for
        self.questions: list[ModelQuestion] = []

    def ask(self, question: ModelQuestion) -> str:
        self.questions.append(question)
        return self.answer_for(question)

    def recorded_calls(self) -> tuple[ModelCall, ...]:
        return tuple(ModelCall(question.purpose, "fake", "fake-model", 0, 0, 0.0, False)
                     for question in self.questions)


EMPTY_DATASET = Dataset((), (), (), (), (), (), (), (), ())


def read_empty_dataset(dataset_dir: Path) -> Dataset:
    return EMPTY_DATASET


def read_no_evidence(files: Sequence[EvidenceFile], dataset_dir: Path, gateway: ModelGateway) -> EvidenceReading:
    return EvidenceReading((), (), ())


def approve_every_request(requests: Sequence[Request], gateway: ModelGateway) -> Mapping[str, RequestDecision]:
    return {request.case_id: RequestDecision(request.case_id, True, "fake") for request in requests}


def resolve_nobody(email: str, identities: Sequence[IdentityRecord], changes: Sequence[IdentityChange],
                   audit_at: datetime) -> Identity | None:
    return None


def find_no_resources(identity: Identity, request: Request, observations: Sequence[Observation],
                      activities: Sequence[Activity]) -> tuple[Resource, ...]:
    return ()


def reconstruct_no_states(resources: Sequence[Resource], evidence: EvidenceReading, activities: Sequence[Activity],
                          audit_at: datetime) -> tuple[ResourceState, ...]:
    return ()


def judge_complete(case_id: str, states: Sequence[ResourceState], rules: Sequence[DeletionRule],
                   audit_at: datetime) -> CaseVerdict:
    return CaseVerdict(case_id, "COMPLETE", ())


def plan_no_steps(verdict: CaseVerdict) -> CaseAnswer:
    return CaseAnswer(verdict.case_id, verdict.deletion_status, ())


def fake_components(gateway: ModelGateway | None = None) -> Components:
    return Components(read_empty_dataset, gateway or FakeModelGateway(lambda question: ""), read_no_evidence,
                      approve_every_request, resolve_nobody, find_no_resources, reconstruct_no_states,
                      judge_complete, plan_no_steps)
