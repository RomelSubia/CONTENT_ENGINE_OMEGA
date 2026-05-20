from __future__ import annotations

def evaluate_maturity_gate(payload: dict[str, object]) -> dict[str, object]:
    level = int(payload.get("maturity_level", 0))
    evidence_refs = payload.get("evidence_refs") or []
    metrics_ready = bool(payload.get("metrics_ready", False))
    recovery_ready = bool(payload.get("recovery_ready", False))

    can_promote = level > 0 and bool(evidence_refs) and metrics_ready and recovery_ready
    return {
        "current_level": level,
        "promotion_allowed": can_promote,
        "draft_creation_allowed": False,
        "autonomy_escalation_allowed": False,
        "reason": "MATURITY_HELD_FOR_EVIDENCE" if not can_promote else "MATURITY_REVIEW_REQUIRED",
    }
