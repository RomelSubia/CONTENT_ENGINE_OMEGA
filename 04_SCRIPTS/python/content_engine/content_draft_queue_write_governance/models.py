from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Mapping

SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")

REQUIRED_UPSTREAM_STATUS = "READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY"
READY_STATUS = "READY_FOR_QUEUE_WRITE_EXECUTION_GOVERNANCE_PLAN_ONLY"
FAILED_STATUS = "FAILED_CLOSED"

ALLOWED_DECISIONS = frozenset({
    "AUTHORIZE_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY",
    "REQUEST_REVISION_BEFORE_QUEUE_WRITE",
    "REJECT_QUEUE_WRITE_READINESS",
    "HOLD_QUEUE_WRITE_READINESS",
    "ESCALATE_QUEUE_WRITE_REVIEW",
})

FORBIDDEN_DECISIONS = frozenset({
    "WRITE_QUEUE_NOW",
    "CREATE_QUEUE_ITEM_NOW",
    "UPDATE_QUEUE_ITEM_NOW",
    "PUBLISH_NOW",
    "AUTOMATE_NOW",
    "TRIGGER_N8N_NOW",
    "TRIGGER_WEBHOOK_NOW",
    "TRIGGER_CAPA9_NOW",
    "MUTATE_MANUAL_CURRENT_NOW",
    "WRITE_BRAIN_NOW",
    "WRITE_REPORTS_BRAIN_NOW",
    "BUILD_ARGOS_BRIDGE_NOW",
})


def is_valid_sha256(value: str) -> bool:
    return bool(SHA256_RE.fullmatch(value or ""))


@dataclass(frozen=True)
class QueueWriteGovernanceEvidence:
    queue_governance_reference: str
    queue_governance_sha256: str
    queue_governance_status: str
    queue_governance_manifest_reference: str
    source_draft_reference: str
    source_draft_sha256: str
    finalization_reference: str
    finalization_sha256: str


@dataclass(frozen=True)
class QueueWriteIntent:
    target_queue: str
    write_intent: str
    idempotency_key: str
    result_is_plan_only: bool = True
    queue_write_performed: bool = False
    queue_item_created: bool = False
    queue_item_updated: bool = False
    target_queue_mutated: bool = False


@dataclass(frozen=True)
class QueueWriteGovernanceRequest:
    request_id: str
    operator_identity: str
    policy_version: str
    timestamp: str
    target_queue: str
    write_intent: str
    idempotency_key: str
    decision: str
    evidence: QueueWriteGovernanceEvidence
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class QueueWriteGovernanceResult:
    request_id: str
    queue_write_governance_status: str
    decision: str
    errors: tuple[str, ...] = ()
    next_allowed_step_for_queue_write_execution_governance_only: bool = False
    result_is_plan_only: bool = True
    queue_write_performed: bool = False
    queue_item_created: bool = False
    queue_item_updated: bool = False
    target_queue_mutated: bool = False
    publishing_started: bool = False
    automation_started: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "queue_write_governance_status": self.queue_write_governance_status,
            "decision": self.decision,
            "errors": list(self.errors),
            "next_allowed_step_for_queue_write_execution_governance_only": self.next_allowed_step_for_queue_write_execution_governance_only,
            "result_is_plan_only": self.result_is_plan_only,
            "queue_write_performed": self.queue_write_performed,
            "queue_item_created": self.queue_item_created,
            "queue_item_updated": self.queue_item_updated,
            "target_queue_mutated": self.target_queue_mutated,
            "publishing_started": self.publishing_started,
            "automation_started": self.automation_started,
        }
