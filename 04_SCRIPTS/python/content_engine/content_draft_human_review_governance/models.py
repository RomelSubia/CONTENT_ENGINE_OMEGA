from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class HumanReviewRequest:
    safe_preview_reference: str | None
    safe_preview_sha256: str | None
    safe_preview_manifest_reference: str | None
    review_request_id: str | None
    reviewer_identity: str | None
    reviewer_role: str | None
    review_decision: str | None
    review_timestamp: str | None
    review_notes_or_reason: str | None
    review_evidence_manifest: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HumanReviewResult:
    status: str
    state: str
    decision: str | None
    approved_for_finalization_plan_only: bool
    finalization_allowed_now: bool
    queue_write_allowed_now: bool
    publishing_allowed_now: bool
    automation_allowed_now: bool
    runtime_execution_allowed_now: bool
    draft_creation_allowed_now: bool
    content_generation_allowed_now: bool
    fail_closed_reason: str | None = None
    missing_fields: tuple[str, ...] = ()
    evidence_errors: tuple[str, ...] = ()
