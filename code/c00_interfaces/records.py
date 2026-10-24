"""The data records that components exchange.

Components depend only on these records and on the signatures in components.py, never on each
other's code, so each component can be tested alone with hand-made records.
All times are timezone-aware UTC datetimes.
The iteration order of a frozenset changes from run to run, so frozenset fields serve membership
tests only; whatever reaches output.csv or an explanation is sorted first (EXT-402).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime

IDENTIFIER_KINDS = ("user_ref", "email", "email_hash", "phone", "name")

DELETION_STATUSES = ("COMPLETE", "INCOMPLETE", "NOT_APPLICABLE")

PHASES = ("FINDING", "REMEDIATION", "VERIFICATION")

# The allowed-operations table of problem_statement.md, in its order: inside a phase, steps are
# sorted by this order first (CHR-416), so the order is part of the contract.
OPERATIONS = {
    "REPORT_REMAINING_RECORD": ("FINDING", "PRESENT"),
    "REPORT_EXPOSED_PII": ("FINDING", "PRESENT"),
    "REPORT_ACTIVE_DATA_FLOW": ("FINDING", "ACTIVE"),
    "REPORT_RESTORE_RISK": ("FINDING", "ACTIVE"),
    "DISABLE_DATA_FLOW": ("REMEDIATION", "DISABLED"),
    "BLOCK_RESTORE": ("REMEDIATION", "BLOCKED"),
    "DELETE_RECORD": ("REMEDIATION", "ABSENT"),
    "REDACT_RECORD": ("REMEDIATION", "REDACTED"),
    "ANONYMIZE_RECORD": ("REMEDIATION", "ANONYMIZED"),
    "VERIFY_RECORD_ABSENT": ("VERIFICATION", "ABSENT"),
    "VERIFY_RECORD_PRESENT": ("VERIFICATION", "PRESENT"),
    "VERIFY_RECORD_REDACTED": ("VERIFICATION", "REDACTED"),
    "VERIFY_RECORD_ANONYMIZED": ("VERIFICATION", "ANONYMIZED"),
    "VERIFY_DATA_FLOW_DISABLED": ("VERIFICATION", "DISABLED"),
    "VERIFY_RESTORE_BLOCKED": ("VERIFICATION", "BLOCKED"),
}


@dataclass(frozen=True)
class InputProblem:
    source: str
    location: str
    message: str


@dataclass(frozen=True)
class Request:
    case_id: str
    email: str
    requested_at: datetime
    reported_status: str
    reported_at: datetime
    audit_at: datetime
    request_text: str


@dataclass(frozen=True)
class IdentityRecord:
    user_id: str
    name: str
    email: str
    phone: str
    email_hash: str
    updated_at: datetime


@dataclass(frozen=True)
class IdentityChange:
    audit_id: str
    user_id: str
    changed_at: datetime
    field_name: str
    old_value: str
    new_value: str


@dataclass(frozen=True)
class Activity:
    activity_id: str
    event_time: datetime
    event_type: str
    source_system: str
    target_system: str
    resource_id: str
    reported_result: str
    details: str


@dataclass(frozen=True)
class DeletionRule:
    rule_id: str
    data_category: str
    condition: str
    required_action: str


@dataclass(frozen=True)
class EvidenceFile:
    file_id: str
    file_path: str
    origin: str
    captured_at: datetime


@dataclass(frozen=True)
class Step:
    step_no: int
    phase: str
    system_id: str
    resource_id: str
    operation: str
    state: str
    evidence_id: str


@dataclass(frozen=True)
class CaseAnswer:
    case_id: str
    deletion_status: str
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class Dataset:
    requests: tuple[Request, ...]
    sample_requests: tuple[Request, ...]
    sample_answers: tuple[CaseAnswer, ...]
    identities: tuple[IdentityRecord, ...]
    identity_changes: tuple[IdentityChange, ...]
    activities: tuple[Activity, ...]
    rules: tuple[DeletionRule, ...]
    evidence_files: tuple[EvidenceFile, ...]
    problems: tuple[InputProblem, ...]


@dataclass(frozen=True)
class Observation:
    """One record seen in one evidence item.

    found is None when the evidence does not say whether the record exists.
    identifiers holds only the personal identifiers present on the record, keyed by a kind from
    IDENTIFIER_KINDS; facts holds the other state facts as written in the evidence.
    """

    evidence_id: str
    captured_at: datetime
    observed_at: datetime
    store: str
    resource_id: str
    found: bool | None
    category: str | None = None
    # hash=False keeps the record hashable; a dict field would make hash() fail.
    identifiers: Mapping[str, str] = field(default_factory=dict, hash=False)
    facts: Mapping[str, str] = field(default_factory=dict, hash=False)
    excerpt: str = ""


@dataclass(frozen=True)
class StoreListing:
    """All records of one store at one time, such as a snapshot table: a record of resource_kind
    (the resource-id prefix the store holds, such as "account") that is not in resource_ids was
    absent from that store (REV-005)."""

    evidence_id: str
    captured_at: datetime
    store: str
    resource_kind: str
    resource_ids: frozenset[str]


@dataclass(frozen=True)
class EvidenceReading:
    observations: tuple[Observation, ...]
    listings: tuple[StoreListing, ...]
    problems: tuple[InputProblem, ...]


@dataclass(frozen=True)
class ModelQuestion:
    purpose: str
    instructions: str
    data: str
    image_png: bytes | None = None


@dataclass(frozen=True)
class ModelCall:
    purpose: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    from_cache: bool


@dataclass(frozen=True)
class RequestDecision:
    case_id: str
    authorizes_deletion: bool
    reason: str


@dataclass(frozen=True)
class Identity:
    """Emails are lower-case (REV-001); email_hashes include the hashes of old emails (REV-002)."""

    user_id: str
    emails: frozenset[str]
    email_hashes: frozenset[str]
    phones: frozenset[str]
    names: frozenset[str]
    history_ids: tuple[str, ...]


@dataclass(frozen=True)
class Resource:
    resource_id: str
    system_id: str
    linked_by_ids: tuple[str, ...]


@dataclass(frozen=True)
class ResourceState:
    """The state of one resource at audit_at.

    present is None, and proof_id is "", when nothing captured at or before audit_at shows the
    state; an activity result alone is only a claim (CHR-312), so the state is then unknown, not
    guessed. Otherwise proof_id is the evidence, activity, or audit id that shows the state.
    """

    resource: Resource
    category: str | None
    present: bool | None
    identifiers_present: frozenset[str]
    flow_enabled: bool | None
    restore_allowed: bool | None
    proof_id: str
    facts: Mapping[str, str] = field(default_factory=dict, hash=False)


@dataclass(frozen=True)
class Judgement:
    """What the policy requires for one resource; the operation fields hold names from the
    allowed-operations table, and finding and remediation are None when the resource complies."""

    state: ResourceState
    rule_id: str | None
    required_action: str
    complies: bool
    finding: str | None
    remediation: str | None
    verification: str
    reason: str


@dataclass(frozen=True)
class CaseVerdict:
    case_id: str
    deletion_status: str
    judgements: tuple[Judgement, ...]


@dataclass(frozen=True)
class CaseResult:
    answer: CaseAnswer
    explanation: tuple[str, ...]


@dataclass(frozen=True)
class Scores:
    cases: int
    status_accuracy: float
    step_accuracy: float
    field_accuracy: float
    sequence_accuracy: float
    failures: tuple[str, ...]
