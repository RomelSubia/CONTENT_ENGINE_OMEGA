from __future__ import annotations

import re

from .models import FinalizationEvidence

_SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")


def is_sha256(value: str) -> bool:
    return bool(_SHA256_RE.fullmatch(value or ""))


def validate_evidence(evidence: FinalizationEvidence) -> None:
    required_values = {
        "human_review_reference": evidence.human_review_reference,
        "human_review_sha256": evidence.human_review_sha256,
        "human_review_manifest_reference": evidence.human_review_manifest_reference,
        "safe_preview_reference": evidence.safe_preview_reference,
        "safe_preview_sha256": evidence.safe_preview_sha256,
        "safe_preview_manifest_reference": evidence.safe_preview_manifest_reference,
        "draft_reference": evidence.draft_reference,
        "draft_sha256": evidence.draft_sha256,
        "draft_manifest_reference": evidence.draft_manifest_reference,
    }

    missing = [key for key, value in required_values.items() if not value]
    if missing:
        raise ValueError(f"MISSING_FINALIZATION_EVIDENCE: {missing}")

    for key in ("human_review_sha256", "safe_preview_sha256", "draft_sha256"):
        if not is_sha256(required_values[key]):
            raise ValueError(f"INVALID_SHA256: {key}")
