from __future__ import annotations

import re

from .models import (
    REQUIRED_PUBLICATION_READINESS_MAP_STATUS,
    REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS,
    PublicationGovernanceEvidence,
)

SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


def is_sha256(value: str) -> bool:
    return bool(value and SHA256_RE.match(value))


def validate_evidence(evidence: PublicationGovernanceEvidence | None) -> tuple[bool, tuple[str, ...]]:
    if evidence is None:
        return False, ("MISSING_EVIDENCE",)

    errors: list[str] = []

    required_text_fields = [
        "queue_write_governance_gate_close_reference",
        "publication_readiness_map_reference",
        "safe_preview_reference",
        "human_review_reference",
        "finalization_reference",
    ]

    for field_name in required_text_fields:
        if not getattr(evidence, field_name, ""):
            errors.append(f"MISSING_{field_name.upper()}")

    hash_fields = [
        "queue_write_governance_gate_close_sha256",
        "publication_readiness_map_sha256",
        "safe_preview_sha256",
        "human_review_sha256",
        "finalization_sha256",
    ]

    for field_name in hash_fields:
        if not is_sha256(getattr(evidence, field_name, "")):
            errors.append(f"INVALID_{field_name.upper()}")

    if evidence.queue_write_governance_status != REQUIRED_QUEUE_WRITE_GOVERNANCE_STATUS:
        errors.append("STALE_OR_INVALID_QUEUE_WRITE_GOVERNANCE")

    if evidence.publication_readiness_map_status != REQUIRED_PUBLICATION_READINESS_MAP_STATUS:
        errors.append("STALE_OR_INVALID_PUBLICATION_READINESS_MAP")

    if evidence.safe_preview_status != "AVAILABLE_OR_EXPLICITLY_NOT_REQUIRED_BY_POLICY":
        errors.append("UNSAFE_PREVIEW")

    if evidence.human_review_status != "APPROVED_OR_ESCALATED_FOR_PUBLICATION_GOVERNANCE_ONLY":
        errors.append("MISSING_HUMAN_REVIEW")

    if evidence.finalization_status != "FINALIZATION_GOVERNANCE_CLOSED_OR_PLAN_ONLY_REFERENCE":
        errors.append("INVALID_FINALIZATION_REFERENCE")

    return not errors, tuple(errors)
