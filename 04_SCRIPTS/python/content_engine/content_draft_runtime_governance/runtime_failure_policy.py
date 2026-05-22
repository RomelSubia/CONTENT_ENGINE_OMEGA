from __future__ import annotations

from typing import Any

from .runtime_contracts import FAILED_BLOCKED, hard_false_flags

BLOCKED_REASON_CODES = frozenset({
    "UNSUPPORTED_DOMAIN_OR_CHANNEL",
    "MISSING_EVIDENCE",
    "MISSING_TRACEABILITY",
    "INVALID_MATURITY_LEVEL",
    "FINAL_OUTPUT_RISK",
    "QUEUE_WRITE_RISK",
    "PUBLISHING_RISK",
    "AUTOMATION_RISK",
    "ARGOS_DEPENDENCY_RISK",
    "PROTECTED_ROOT_TOUCH_RISK",
    "EXTERNAL_IO_RISK",
    "NON_CANONICAL_OUTPUT_RISK",
    "HUMAN_REVIEW_MISSING",
    "RUNTIME_STATE_DRIFT",
    "RUNTIME_MODE_BLOCKED",
    "REQUEST_FIELD_MISSING",
})

def fail_closed(reason: str, *, evidence_refs: list[str] | None = None, traceability_refs: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": FAILED_BLOCKED,
        "reason": reason,
        "runtime_state": "RUNTIME_FAILED_CLOSED",
        "runtime_mode": None,
        "preview_only": False,
        "non_publishable": True,
        "human_review_required": True,
        "blocked_reason_code": reason if reason in BLOCKED_REASON_CODES else "RUNTIME_STATE_DRIFT",
        "evidence_refs": list(evidence_refs or []),
        "traceability_refs": list(traceability_refs or []),
        "manifest_refs": [],
        "seal_refs": [],
        **hard_false_flags(),
    }
