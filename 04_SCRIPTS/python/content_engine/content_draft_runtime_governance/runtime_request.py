from __future__ import annotations

from typing import Any

from .runtime_contracts import ALLOWED_RUNTIME_MODES, BLOCKED_RUNTIME_MODES, REQUIRED_REQUEST_FIELDS, SUPPORTED_DOMAINS, PASS
from .runtime_failure_policy import fail_closed

def validate_runtime_request(request: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(field for field in REQUIRED_REQUEST_FIELDS if field not in request)
    if missing:
        return fail_closed("REQUEST_FIELD_MISSING")

    mode = request.get("runtime_mode")
    if mode in BLOCKED_RUNTIME_MODES or mode not in ALLOWED_RUNTIME_MODES:
        return fail_closed("RUNTIME_MODE_BLOCKED", evidence_refs=request.get("evidence_refs"), traceability_refs=request.get("traceability_refs"))

    if request.get("channel_or_domain_id") not in SUPPORTED_DOMAINS:
        return fail_closed("UNSUPPORTED_DOMAIN_OR_CHANNEL", evidence_refs=request.get("evidence_refs"), traceability_refs=request.get("traceability_refs"))

    if not request.get("evidence_refs"):
        return fail_closed("MISSING_EVIDENCE", traceability_refs=request.get("traceability_refs"))

    if not request.get("traceability_refs"):
        return fail_closed("MISSING_TRACEABILITY", evidence_refs=request.get("evidence_refs"))

    if request.get("human_review_required") is not True:
        return fail_closed("HUMAN_REVIEW_MISSING", evidence_refs=request.get("evidence_refs"), traceability_refs=request.get("traceability_refs"))

    if int(request.get("maturity_level", -1)) != 0:
        return fail_closed("INVALID_MATURITY_LEVEL", evidence_refs=request.get("evidence_refs"), traceability_refs=request.get("traceability_refs"))

    return {
        "status": PASS,
        "runtime_state": "RUNTIME_PRECHECKED",
        "runtime_mode": mode,
        "preview_only": True,
        "non_publishable": True,
        "human_review_required": True,
        "evidence_refs": list(request.get("evidence_refs", [])),
        "traceability_refs": list(request.get("traceability_refs", [])),
    }
