from __future__ import annotations

from typing import Any, Dict

from .approval_contract import validate_approval_contract
from .execution_boundary_guard import execution_boundary_guard
from .expiration_guard import expiration_guard
from .hashing import stable_hash
from .input_contract import validate_input_contract
from .lineage_guard import lineage_guard
from .outputs import blocked_output, pending_output
from .scope_guard import scope_guard


def _finalize(output: Dict[str, Any], input_data: Dict[str, Any], approval: Dict[str, Any] | None) -> Dict[str, Any]:
    output["input_hash"] = stable_hash(input_data)
    output["approval_hash"] = stable_hash(approval or {})
    output["scope_hash"] = stable_hash((approval or {}).get("approved_items", []))
    output["lineage_hash"] = stable_hash(
        {
            "input_hash": input_data.get("input_hash", ""),
            "risk_hash": input_data.get("risk_hash", ""),
            "decision_hash": input_data.get("decision_hash", ""),
        }
    )
    output["intent_hash"] = stable_hash((approval or {}).get("approval_intent", ""))
    output["authorization_hash"] = stable_hash(output.get("decision", ""))
    output["config_hash"] = stable_hash({"version": "G-E_v1.3"})
    output["output_hash"] = stable_hash(output)
    return output


def run_g_e(input_data: Dict[str, Any], approval: Dict[str, Any] | None = None, now_iso: str | None = None) -> Dict[str, Any]:
    ok, reason = validate_input_contract(input_data)
    if not ok:
        return _finalize(blocked_output(reason), input_data, approval)

    if input_data["status"] == "BLOCKED" or input_data["decision"] == "BLOCK":
        return _finalize(blocked_output("SOURCE_BLOCKED"), input_data, approval)

    if input_data["decision"] in {"QUARANTINE", "REVIEW_REQUIRED"}:
        return _finalize(pending_output("SOURCE_REQUIRES_REVIEW"), input_data, approval)

    if input_data["decision"] != "ALLOW_REVIEW":
        return _finalize(pending_output("NO_AUTHORIZATION_AVAILABLE"), input_data, approval)

    ok, reason = validate_approval_contract(approval)
    if not ok:
        if reason in {"AMBIGUOUS_APPROVAL", "APPROVAL_MISSING", "HUMAN_APPROVAL_NOT_TRUE", "APPROVAL_STATEMENT_TOO_WEAK"}:
            return _finalize(pending_output(reason), input_data, approval)
        return _finalize(blocked_output(reason), input_data, approval)

    for guard in (execution_boundary_guard,):
        ok, reason = guard(approval)
        if not ok:
            return _finalize(blocked_output(reason), input_data, approval)

    ok, reason = expiration_guard(approval, now_iso)
    if not ok:
        return _finalize(blocked_output(reason), input_data, approval)

    ok, reason = lineage_guard(input_data, approval)
    if not ok:
        return _finalize(blocked_output(reason), input_data, approval)

    ok, reason = scope_guard(input_data, approval)
    if not ok:
        return _finalize(blocked_output(reason), input_data, approval)

    authorized = [
        item for item in input_data["approved_for_review"]
        if item.get("recommendation_id") in set(approval["approved_items"])
    ]

    output = {
        "phase": "G",
        "subphase": "G-E",
        "status": "AUTHORIZED_FOR_CONTROLLED_PLAN",
        "authorized_items": authorized,
        "pending_items": [],
        "blocked_items": [],
        "approval_summary": {
            "approved_by": approval["approved_by"],
            "approval_scope": approval["approval_scope"],
            "authorization_boundary": "CONTROLLED_PLAN_ONLY_NOT_EXECUTION",
        },
        "decision": "AUTHORIZED_FOR_CONTROLLED_PLAN",
        "deterministic": True,
    }

    return _finalize(output, input_data, approval)
