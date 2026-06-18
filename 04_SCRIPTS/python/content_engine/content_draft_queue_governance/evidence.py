from __future__ import annotations

import re
from dataclasses import fields, is_dataclass
from typing import Any

from .models import QueueGovernanceEvidence

SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")

REQUIRED_EVIDENCE_FIELDS = [
    "finalization_result_reference",
    "finalization_result_sha256",
    "finalization_manifest_reference",
    "draft_reference",
    "draft_sha256",
    "human_review_reference",
    "human_review_sha256",
    "safe_preview_reference",
    "safe_preview_sha256",
]

SHA256_FIELDS = [
    "finalization_result_sha256",
    "draft_sha256",
    "human_review_sha256",
    "safe_preview_sha256",
]


class QueueGovernanceEvidenceError(ValueError):
    pass


def _get_value(evidence: Any, name: str) -> Any:
    if isinstance(evidence, dict):
        return evidence.get(name)
    return getattr(evidence, name, None)


def validate_sha256(value: str) -> None:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise QueueGovernanceEvidenceError("INVALID_SHA256")


def validate_queue_governance_evidence(evidence: QueueGovernanceEvidence | dict[str, Any]) -> QueueGovernanceEvidence | dict[str, Any]:
    missing = [
        name
        for name in REQUIRED_EVIDENCE_FIELDS
        if _get_value(evidence, name) in (None, "")
    ]
    if missing:
        raise QueueGovernanceEvidenceError("MISSING_QUEUE_GOVERNANCE_EVIDENCE")

    for name in SHA256_FIELDS:
        validate_sha256(str(_get_value(evidence, name)))

    if is_dataclass(evidence):
        evidence_field_names = {field.name for field in fields(evidence)}
        if not set(REQUIRED_EVIDENCE_FIELDS).issubset(evidence_field_names):
            raise QueueGovernanceEvidenceError("MISSING_QUEUE_GOVERNANCE_EVIDENCE")

    return evidence
