from __future__ import annotations

from typing import Any

from .runtime_contracts import PASS
from .runtime_request import validate_runtime_request
from .runtime_preview_guard import inspect_preview_text
from .runtime_no_side_effect_guard import assert_no_side_effects

def decide_runtime_governance(request: dict[str, Any], preview_text: str = "") -> dict[str, Any]:
    request_result = validate_runtime_request(request)
    if request_result.get("status") != PASS:
        return request_result

    preview_result = inspect_preview_text(preview_text)
    if preview_result.get("status") != PASS:
        return preview_result

    side_effects = assert_no_side_effects()
    if side_effects.get("status") != PASS:
        return side_effects

    return {
        "status": PASS,
        "decision_status": "RUNTIME_DECISION_ALLOWED_PREVIEW_ONLY",
        "decision_reason": "Preview-only runtime governance allowed; productive actions remain blocked.",
        "allowed_runtime_mode": request.get("runtime_mode"),
        "runtime_state": "RUNTIME_PREVIEW_READY",
        "preview_only": True,
        "non_publishable": True,
        "human_review_required": True,
        "blocked_reason_code": None,
        "risk_flags": [],
        "evidence_refs": list(request.get("evidence_refs", [])),
        "traceability_refs": list(request.get("traceability_refs", [])),
    }
