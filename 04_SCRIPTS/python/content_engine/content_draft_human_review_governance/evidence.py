from __future__ import annotations

import re
from .models import HumanReviewRequest

SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")

REQUIRED_FIELDS = (
    "safe_preview_reference",
    "safe_preview_sha256",
    "safe_preview_manifest_reference",
    "review_request_id",
    "reviewer_identity",
    "reviewer_role",
    "review_decision",
    "review_timestamp",
    "review_notes_or_reason",
)


def missing_required_fields(request: HumanReviewRequest) -> tuple[str, ...]:
    missing: list[str] = []
    for field_name in REQUIRED_FIELDS:
        value = getattr(request, field_name)
        if value is None or str(value).strip() == "":
            missing.append(field_name)
    return tuple(missing)


def validate_preview_hash(request: HumanReviewRequest) -> tuple[str, ...]:
    errors: list[str] = []
    if not request.safe_preview_sha256:
        errors.append("missing_safe_preview_hash")
    elif not SHA256_RE.match(request.safe_preview_sha256):
        errors.append("invalid_safe_preview_sha256")
    expected = request.review_evidence_manifest.get("safe_preview_sha256")
    if expected is not None and expected != request.safe_preview_sha256:
        errors.append("tampered_safe_preview_hash")
    stale = request.review_evidence_manifest.get("stale_preview")
    if stale is True:
        errors.append("stale_safe_preview_reference")
    return tuple(errors)
