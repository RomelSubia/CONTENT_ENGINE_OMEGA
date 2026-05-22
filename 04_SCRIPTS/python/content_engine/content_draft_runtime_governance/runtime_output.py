from __future__ import annotations

from typing import Any

from .runtime_contracts import PASS, hard_false_flags

def make_runtime_output(decision: dict[str, Any]) -> dict[str, Any]:
    status = decision.get("status", PASS)
    return {
        "status": status,
        "reason": decision.get("decision_reason") or decision.get("reason") or "runtime_governance_decision",
        "runtime_state": decision.get("runtime_state", "RUNTIME_FAILED_CLOSED" if status != PASS else "RUNTIME_PREVIEW_READY"),
        "runtime_mode": decision.get("allowed_runtime_mode"),
        "preview_only": decision.get("preview_only", status == PASS),
        "non_publishable": True,
        "human_review_required": True,
        "evidence_refs": list(decision.get("evidence_refs", [])),
        "traceability_refs": list(decision.get("traceability_refs", [])),
        "manifest_refs": [],
        "seal_refs": [],
        **hard_false_flags(),
    }
