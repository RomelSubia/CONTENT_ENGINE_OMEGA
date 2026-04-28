from __future__ import annotations

from typing import Any, Dict

from .hashing import stable_hash
from .input_contract import validate_input_contract
from .plan_builder import (
    build_diff_preview,
    build_plan_id,
    build_review_package,
    build_rollback_plan,
    build_steps,
    build_validation_plan,
)
from .plan_validators import validate_review_package, validate_rollback_plan, validate_validation_plan
from .reason_registry import reason
from .step_validator import validate_steps


def _finalize(output: Dict[str, Any]) -> Dict[str, Any]:
    output["plan_hash"] = stable_hash(output.get("controlled_plan", {}))
    output["steps_hash"] = stable_hash(output.get("controlled_plan", {}).get("steps", []))
    output["diff_hash"] = stable_hash(output.get("controlled_plan", {}).get("diff_preview", {}))
    output["rollback_hash"] = stable_hash(output.get("rollback_plan", {}))
    output["validation_hash"] = stable_hash(output.get("validation_plan", {}))
    output["review_hash"] = stable_hash(output.get("review_package", {}))
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason_code: str) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-F",
        "status": "BLOCKED",
        "controlled_plan": {},
        "validation_plan": {},
        "rollback_plan": {},
        "review_package": {},
        "reason_registry": [reason(reason_code)],
        "decision": "BLOCK",
        "deterministic": True,
    }
    return _finalize(output)


def run_g_f(input_data: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason_code = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason_code)

    if any(item.get("risk_level") == "HIGH" for item in input_data["authorized_items"] if isinstance(item, dict)):
        return _blocked("HIGH_RISK_PLAN_BLOCKED")

    plan_id = build_plan_id(input_data)
    steps = build_steps(input_data)

    ok, reason_code = validate_steps(steps)
    if not ok:
        return _blocked(reason_code)

    diff_preview = build_diff_preview(steps)
    validation_plan = build_validation_plan()
    rollback_plan = build_rollback_plan()
    review_package = build_review_package(steps, diff_preview, validation_plan, rollback_plan)

    ok, reason_code = validate_validation_plan(validation_plan)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_rollback_plan(rollback_plan)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_review_package(review_package)
    if not ok:
        return _blocked(reason_code)

    controlled_plan = {
        "plan_id": plan_id,
        "plan_state": "FINALIZED",
        "plan_type": "CONTROLLED_PLAN",
        "source_authorization_hash": input_data["authorization_hash"],
        "source_approval_hash": input_data["approval_hash"],
        "authorized_items": input_data["authorized_items"],
        "allowed_scope": "READ_ONLY_ANALYSIS_AND_PLAN_ONLY",
        "execution_allowed": False,
        "steps": steps,
        "diff_preview": diff_preview,
        "validation_plan": validation_plan,
        "rollback_plan": rollback_plan,
        "review_package": review_package,
        "reason_registry": [],
    }

    output = {
        "phase": "G",
        "subphase": "G-F",
        "status": "PLAN_READY_FOR_REVIEW",
        "controlled_plan": controlled_plan,
        "validation_plan": validation_plan,
        "rollback_plan": rollback_plan,
        "review_package": review_package,
        "reason_registry": [],
        "decision": "PLAN_READY_FOR_REVIEW",
        "deterministic": True,
    }

    return _finalize(output)
