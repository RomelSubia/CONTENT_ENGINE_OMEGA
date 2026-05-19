"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


FORBIDDEN_HISTORY_ROOTS = ("07_DATA", "05_REPORTS", "14_EXPORTS", "09_PUBLICATION", "08_ASSETS", "12_LOGS", "13_BACKUPS")

def concept_hash(candidate: dict) -> str:
    material = "|".join([
        str(candidate.get("channel_id", "")),
        str(candidate.get("pillar_id", "")),
        str(candidate.get("idea_title", "")).strip().lower(),
        str(candidate.get("idea_summary", "")).strip().lower(),
    ])
    import hashlib
    return hashlib.sha256(material.encode("utf-8")).hexdigest()

def validate_duplication_governance(candidate: dict, provided_comparison_payload: list[dict] | None = None) -> dict:
    combined = " ".join(str(value) for value in candidate.values())
    for root in FORBIDDEN_HISTORY_ROOTS:
        if root.lower() in combined.lower():
            return {"status": "BLOCK", "reason": "REAL_HISTORY_OR_FILE_REFERENCE_BLOCKED"}
    current_hash = concept_hash(candidate)
    for item in provided_comparison_payload or []:
        if concept_hash(item) == current_hash:
            return {"status": "BLOCK", "reason": "DUPLICATION_BLOCKED", "concept_hash": current_hash}
    return {"status": "PASS", "reason": "DUPLICATION_CLEAR_FOR_REVIEW", "concept_hash": current_hash}
