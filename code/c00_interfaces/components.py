"""The call signature of every component.

The audit pipeline receives the components as a Components bundle instead of importing them, so a
test can hand it fakes; the same holds for the model gateway inside the evidence reader and the
request classifier.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

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
    Scores,
)


@runtime_checkable
class DatasetReader(Protocol):
    def __call__(self, dataset_dir: Path) -> Dataset: ...


@runtime_checkable
class ModelGateway(Protocol):
    def ask(self, question: ModelQuestion) -> str: ...

    def calls(self) -> tuple[ModelCall, ...]: ...


@runtime_checkable
class EvidenceReader(Protocol):
    def __call__(self, files: Sequence[EvidenceFile], dataset_dir: Path,
                 gateway: ModelGateway) -> EvidenceReading: ...


@runtime_checkable
class RequestClassifier(Protocol):
    def __call__(self, requests: Sequence[Request],
                 gateway: ModelGateway) -> Mapping[str, RequestDecision]: ...


@runtime_checkable
class IdentityResolver(Protocol):
    def __call__(self, email: str, identities: Sequence[IdentityRecord],
                 changes: Sequence[IdentityChange], audit_at: datetime) -> Identity | None: ...


@runtime_checkable
class ResourceFinder(Protocol):
    def __call__(self, identity: Identity, request: Request, observations: Sequence[Observation],
                 activities: Sequence[Activity]) -> tuple[Resource, ...]: ...


@runtime_checkable
class StateReconstructor(Protocol):
    def __call__(self, resources: Sequence[Resource], evidence: EvidenceReading,
                 activities: Sequence[Activity], audit_at: datetime) -> tuple[ResourceState, ...]: ...


@runtime_checkable
class PolicyChecker(Protocol):
    def __call__(self, case_id: str, states: Sequence[ResourceState], rules: Sequence[DeletionRule],
                 audit_at: datetime) -> CaseVerdict: ...


@runtime_checkable
class StepPlanner(Protocol):
    def __call__(self, verdict: CaseVerdict) -> CaseAnswer: ...


@runtime_checkable
class Evaluator(Protocol):
    def __call__(self, predicted: Mapping[str, CaseAnswer],
                 expected: Mapping[str, CaseAnswer]) -> Scores: ...


@dataclass(frozen=True)
class Components:
    read_dataset: DatasetReader
    gateway: ModelGateway
    read_evidence: EvidenceReader
    classify_requests: RequestClassifier
    resolve_identity: IdentityResolver
    find_resources: ResourceFinder
    reconstruct_states: StateReconstructor
    check_policy: PolicyChecker
    plan_steps: StepPlanner
