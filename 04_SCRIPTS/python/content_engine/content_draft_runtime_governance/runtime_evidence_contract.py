from __future__ import annotations

from .runtime_contracts import PASS
from .runtime_failure_policy import fail_closed

REQUIRED_EVIDENCE = frozenset({
    "runtime_request_snapshot",
    "runtime_precheck_report",
    "runtime_decision_report",
    "runtime_no_side_effect_report",
    "runtime_failure_report",
    "runtime_traceability_report",
    "runtime_manifest",
    "runtime_seal",
    "runtime_human_review_marker",
})

def validate_evidence_refs(refs: list[str] | None) -> dict[str, object]:
    if not refs:
        return fail_closed("MISSING_EVIDENCE")
    return {"status": PASS, "evidence_refs": list(refs), "canonical_json_required": True, "manifest_required": True, "seal_required": True}
