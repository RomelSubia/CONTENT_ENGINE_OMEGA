from __future__ import annotations

from .classification import is_allowed_classification, is_blocked_classification
from .contracts import SafePreviewError, SafePreviewRequest
from .evidence import require_non_empty_refs, require_text

PRODUCTIVE_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "final_text",
        "platform_ready_metadata",
        "queue_payload",
        "queue_ready_payload",
        "publishable_asset",
        "publication_payload",
        "automation_payload",
        "n8n_payload",
        "webhook_payload",
        "capa9_payload",
        "external_api_request",
        "manual_current_write",
        "brain_write",
        "reports_brain_write",
        "argos_bridge_build",
        "runtime_execution",
        "draft_creation",
        "content_generation",
        "queue_write",
        "publishing",
        "automation",
    }
)


def validate_safe_preview_request(request: SafePreviewRequest) -> SafePreviewRequest:
    require_text(request.request_id, "request_id")
    require_text(request.candidate_id, "candidate_id")
    require_text(request.domain_id, "domain_id")
    require_text(request.preview_text, "preview_text")

    if request.human_review_required is not True:
        raise SafePreviewError("human_review_required_must_be_true")

    require_non_empty_refs(request.evidence_refs, "evidence_refs")
    require_non_empty_refs(request.traceability_refs, "traceability_refs")

    if is_blocked_classification(request.classification):
        raise SafePreviewError(f"blocked_classification:{request.classification}")

    if not is_allowed_classification(request.classification):
        raise SafePreviewError(f"unsafe_classification:{request.classification}")

    metadata_keys = {str(key) for key in request.metadata.keys()}
    forbidden = sorted(metadata_keys & PRODUCTIVE_METADATA_KEYS)
    if forbidden:
        raise SafePreviewError(f"productive_metadata_forbidden:{','.join(forbidden)}")

    return request
