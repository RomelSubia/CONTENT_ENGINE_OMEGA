from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FinalizationStatus(str, Enum):
    READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY = "READY_FOR_QUEUE_GOVERNANCE_PLAN_ONLY"
    REQUEST_REVISION_BEFORE_FINALIZATION = "REQUEST_REVISION_BEFORE_FINALIZATION"
    REJECTED = "REJECTED"
    HOLD = "HOLD"
    ESCALATED = "ESCALATED"


class FinalizationDecision(str, Enum):
    FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY = "FINALIZE_FOR_QUEUE_GOVERNANCE_PLAN_ONLY"
    REQUEST_REVISION_BEFORE_FINALIZATION = "REQUEST_REVISION_BEFORE_FINALIZATION"
    REJECT_FINALIZATION = "REJECT_FINALIZATION"
    HOLD_FINALIZATION = "HOLD_FINALIZATION"
    ESCALATE_FINALIZATION_REVIEW = "ESCALATE_FINALIZATION_REVIEW"


@dataclass(frozen=True)
class FinalizationEvidence:
    human_review_reference: str
    human_review_sha256: str
    human_review_manifest_reference: str
    safe_preview_reference: str
    safe_preview_sha256: str
    safe_preview_manifest_reference: str
    draft_reference: str
    draft_sha256: str
    draft_manifest_reference: str


@dataclass(frozen=True)
class FinalizationRequest:
    request_id: str
    operator_identity: str
    policy_version: str
    timestamp: str
    intent: str
    decision: FinalizationDecision
    evidence: FinalizationEvidence
