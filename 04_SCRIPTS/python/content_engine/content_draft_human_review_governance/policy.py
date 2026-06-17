from __future__ import annotations

ALLOWED_DECISIONS = {
    "APPROVE_FOR_FINALIZATION_PLAN_ONLY",
    "REQUEST_REVISION",
    "REJECT",
    "HOLD",
    "ESCALATE",
}

FORBIDDEN_DECISIONS = {
    "APPROVE_FOR_PUBLICATION",
    "APPROVE_FOR_QUEUE_WRITE",
    "APPROVE_FOR_AUTOMATION",
    "APPROVE_FOR_N8N",
    "APPROVE_FOR_WEBHOOK",
    "APPROVE_FOR_CAPA9",
}

APPROVAL_DECISION = "APPROVE_FOR_FINALIZATION_PLAN_ONLY"


def is_allowed_decision(decision: str | None) -> bool:
    return bool(decision) and decision in ALLOWED_DECISIONS


def is_forbidden_decision(decision: str | None) -> bool:
    return bool(decision) and decision in FORBIDDEN_DECISIONS


def decision_fail_reason(decision: str | None) -> str | None:
    if not decision:
        return "missing_review_decision"
    if is_forbidden_decision(decision):
        return "forbidden_review_decision"
    if not is_allowed_decision(decision):
        return "decision_not_allowlisted"
    return None
