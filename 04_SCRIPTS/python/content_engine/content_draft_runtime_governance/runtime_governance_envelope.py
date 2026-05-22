from __future__ import annotations

from typing import Any

from .runtime_decision import decide_runtime_governance
from .runtime_output import make_runtime_output
from .runtime_no_side_effect_guard import assert_no_side_effects

def build_runtime_governance_envelope(request: dict[str, Any], preview_text: str = "") -> dict[str, Any]:
    decision = decide_runtime_governance(request, preview_text=preview_text)
    output = make_runtime_output(decision)
    no_side_effect = assert_no_side_effects()
    return {
        "runtime_envelope_required": True,
        "runtime_request_id": request.get("runtime_request_id"),
        "runtime_mode": request.get("runtime_mode"),
        "request_status": "RECEIVED",
        "decision_status": decision.get("decision_status", "RUNTIME_DECISION_FAILED_CLOSED"),
        "preview_allowed": output.get("status") == "PASS",
        "side_effects_allowed": False,
        "human_review_required": True,
        "evidence_required": True,
        "traceability_required": True,
        "manifest_required": True,
        "seal_required": True,
        "decision": decision,
        "output": output,
        "no_side_effect": no_side_effect,
    }
