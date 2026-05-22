from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PASS = "PASS"
FAILED_BLOCKED = "FAILED_BLOCKED"

ALLOWED_RUNTIME_MODES = frozenset({
    "PREVIEW_ONLY",
    "DRY_RUN_ONLY",
    "VALIDATION_ONLY",
    "NO_OP_AUDIT_ONLY",
})

BLOCKED_RUNTIME_MODES = frozenset({
    "CREATE_DRAFT",
    "GENERATE_CONTENT",
    "WRITE_QUEUE",
    "PUBLISH",
    "AUTOMATE",
})

RUNTIME_STATES = frozenset({
    "RUNTIME_NOT_STARTED",
    "RUNTIME_REQUEST_RECEIVED",
    "RUNTIME_PRECHECKED",
    "RUNTIME_PREVIEW_READY",
    "RUNTIME_PREVIEW_BLOCKED",
    "RUNTIME_REQUIRES_HUMAN_REVIEW",
    "RUNTIME_FAILED_CLOSED",
    "RUNTIME_SEALED_NO_OP",
})

PRODUCTIVE_FLAGS = (
    "side_effects_performed",
    "draft_creation_performed",
    "content_generation_performed",
    "queue_write_performed",
    "publishing_performed",
    "automation_performed",
)

REQUIRED_REQUEST_FIELDS = frozenset({
    "runtime_request_id",
    "draft_candidate_id",
    "channel_or_domain_id",
    "runtime_mode",
    "requested_action",
    "maturity_level",
    "evidence_refs",
    "traceability_refs",
    "human_review_required",
    "actor_context",
    "created_at",
    "schema_version",
})

SUPPORTED_DOMAINS = frozenset({
    "finca_san_mateo",
    "cacao",
    "arriendos",
    "bravi",
    "bramviss",
    "digital_a",
    "digital_b",
    "digital_c",
    "digital_d",
    "websites",
    "future_business_or_brand",
})

BLOCKED_PREVIEW_PATTERNS = tuple(s.lower() for s in (
    "final caption",
    "final script",
    "final cta",
    "platform-ready metadata",
    "publish now",
    "texto listo para publicar",
    "hashtags finales",
    "asset final",
    "publication link",
    "guion final",
    "caption final",
    "cta final",
))

def hard_false_flags() -> dict[str, bool]:
    return {name: False for name in PRODUCTIVE_FLAGS}
