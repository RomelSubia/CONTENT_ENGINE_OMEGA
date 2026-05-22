from __future__ import annotations

from typing import Any

from .runtime_contracts import PASS

def build_runtime_audit_bundle(envelope: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": PASS,
        "canonical_json_required": True,
        "hash_algorithm": "sha256",
        "runtime_request_snapshot": envelope.get("runtime_request_id"),
        "runtime_precheck_report": True,
        "runtime_decision_report": True,
        "runtime_no_side_effect_report": True,
        "runtime_failure_report": envelope.get("output", {}).get("status") != PASS,
        "runtime_traceability_report": True,
        "runtime_manifest": True,
        "runtime_seal": True,
        "runtime_human_review_marker": True,
        "productive_effect_claims": False,
    }
