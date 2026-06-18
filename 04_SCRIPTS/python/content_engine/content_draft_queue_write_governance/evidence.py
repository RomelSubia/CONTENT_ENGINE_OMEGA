from __future__ import annotations

from .models import QueueWriteGovernanceEvidence, REQUIRED_UPSTREAM_STATUS, is_valid_sha256


def validate_evidence(evidence: QueueWriteGovernanceEvidence) -> tuple[str, ...]:
    errors: list[str] = []

    required_text = {
        "queue_governance_reference": evidence.queue_governance_reference,
        "queue_governance_manifest_reference": evidence.queue_governance_manifest_reference,
        "source_draft_reference": evidence.source_draft_reference,
        "finalization_reference": evidence.finalization_reference,
    }

    for field_name, value in required_text.items():
        if not value:
            errors.append(f"MISSING_{field_name.upper()}")

    for field_name, value in {
        "queue_governance_sha256": evidence.queue_governance_sha256,
        "source_draft_sha256": evidence.source_draft_sha256,
        "finalization_sha256": evidence.finalization_sha256,
    }.items():
        if not is_valid_sha256(value):
            errors.append(f"INVALID_{field_name.upper()}")

    if evidence.queue_governance_status != REQUIRED_UPSTREAM_STATUS:
        errors.append("UPSTREAM_QUEUE_GOVERNANCE_STATUS_INVALID")

    return tuple(errors)
