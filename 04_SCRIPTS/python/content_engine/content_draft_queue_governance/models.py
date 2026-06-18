from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class QueueGovernanceStatus(str, Enum):
    READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY = "READY_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY"
    REQUEST_REVISION_BEFORE_QUEUE = "REQUEST_REVISION_BEFORE_QUEUE"
    REJECTED = "REJECTED"
    HOLD = "HOLD"
    ESCALATED = "ESCALATED"


class QueueGovernanceDecision(str, Enum):
    PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY = "PREPARE_FOR_QUEUE_WRITE_GOVERNANCE_PLAN_ONLY"
    REQUEST_REVISION_BEFORE_QUEUE = "REQUEST_REVISION_BEFORE_QUEUE"
    REJECT_QUEUE_READINESS = "REJECT_QUEUE_READINESS"
    HOLD_QUEUE_READINESS = "HOLD_QUEUE_READINESS"
    ESCALATE_QUEUE_REVIEW = "ESCALATE_QUEUE_REVIEW"


@dataclass(frozen=True)
class QueueGovernanceEvidence:
    finalization_result_reference: str
    finalization_result_sha256: str
    finalization_manifest_reference: str
    draft_reference: str
    draft_sha256: str
    human_review_reference: str
    human_review_sha256: str
    safe_preview_reference: str
    safe_preview_sha256: str


@dataclass(frozen=True)
class QueueGovernanceRequest:
    request_id: str
    operator_identity: str
    policy_version: str
    timestamp: str
    intent: str
    evidence: QueueGovernanceEvidence
    decision: QueueGovernanceDecision
