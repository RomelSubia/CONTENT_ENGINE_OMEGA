from __future__ import annotations

from .contracts import SafePreviewRequest, SafePreviewResult
from .guard import validate_safe_preview_request


BLOCKED_PRODUCTIVE_FLAGS: dict[str, bool] = {
    "runtime_execution_started": False,
    "draft_creation_started": False,
    "content_generation_started": False,
    "queue_write_performed": False,
    "publishing_started": False,
    "automation_started": False,
    "n8n_started": False,
    "webhook_started": False,
    "capa9_started": False,
    "manual_current_mutation_performed": False,
    "brain_write_performed": False,
    "reports_brain_write_performed": False,
    "argos_bridge_build_performed": False,
}


def build_safe_preview(request: SafePreviewRequest) -> SafePreviewResult:
    validated = validate_safe_preview_request(request)
    return SafePreviewResult(
        request_id=validated.request_id,
        candidate_id=validated.candidate_id,
        domain_id=validated.domain_id,
        preview_text=validated.preview_text,
        classification=validated.classification,
        preview_label="INTERNAL_SAFE_PREVIEW_NON_FINAL",
        human_review_required=True,
        evidence_refs=tuple(validated.evidence_refs),
        traceability_refs=tuple(validated.traceability_refs),
        blocked_productive_flags=dict(BLOCKED_PRODUCTIVE_FLAGS),
    )
