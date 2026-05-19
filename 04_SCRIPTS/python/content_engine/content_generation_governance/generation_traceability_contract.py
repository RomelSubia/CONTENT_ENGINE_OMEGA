"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


REQUIRED_TRACE = {
    "construction_core_ref": "CLOSED_VALIDATED",
    "strategy_foundation_ref": "CLOSED_VALIDATED",
    "prompt_governance_ref": "CLOSED_VALIDATED",
    "queue_governance_ref": "CLOSED_VALIDATED",
}

def validate_generation_traceability(candidate: dict) -> dict:
    trace = candidate.get("traceability", {})
    missing = [key for key in REQUIRED_TRACE if key not in trace]
    invalid = {key: trace.get(key) for key, expected in REQUIRED_TRACE.items() if trace.get(key) != expected}
    if missing or invalid:
        return {"status": "BLOCK", "reason": "GENERATION_TRACEABILITY_INVALID", "missing": missing, "invalid": invalid}
    if not candidate.get("queue_item_id"):
        return {"status": "BLOCK", "reason": "ANONYMOUS_CANDIDATE_BLOCKED"}
    return {"status": "PASS", "reason": "GENERATION_TRACEABILITY_VALID"}
