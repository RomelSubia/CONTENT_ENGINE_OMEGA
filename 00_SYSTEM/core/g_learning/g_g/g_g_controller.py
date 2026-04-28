from __future__ import annotations

from typing import Any, Dict

from .approval_guard import validate_final_approval
from .command_guard import contains_command_token
from .drift_guard import drift_guard
from .hashing import stable_hash
from .input_contract import validate_input_contract
from .plan_guards import validate_plan_integrity, validate_rollback_readiness, validate_validation_readiness
from .reason_registry import reason
from .repo_state_guard import validate_repo_state
from .snapshot_guard import validate_snapshot


def _finalize(output: Dict[str, Any]) -> Dict[str, Any]:
    output["gate_hash"] = stable_hash(output.get("execution_gate", {}))
    output["drift_hash"] = stable_hash(output.get("execution_gate", {}).get("drift_baseline", {}))
    output["snapshot_hash"] = stable_hash(output.get("execution_gate", {}).get("validated_snapshot", {}))
    output["validation_hash"] = stable_hash(output.get("execution_gate", {}).get("validated_validation", {}))
    output["rollback_hash"] = stable_hash(output.get("execution_gate", {}).get("validated_rollback", {}))
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason_code: str) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-G",
        "status": "BLOCKED",
        "execution_gate": {},
        "reason_registry": [reason(reason_code)],
        "decision": "BLOCK",
        "deterministic": True,
        "execution_permission": False,
    }
    return _finalize(output)


def _review_required(reason_code: str) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-G",
        "status": "REVIEW_REQUIRED",
        "execution_gate": {},
        "reason_registry": [reason(reason_code)],
        "decision": "REVIEW_REQUIRED",
        "deterministic": True,
        "execution_permission": False,
    }
    return _finalize(output)


def run_g_g(
    input_data: Dict[str, Any],
    final_approval: Dict[str, Any] | None = None,
    snapshot: Dict[str, Any] | None = None,
    repo_state: Dict[str, Any] | None = None,
    emergency_stop_status: str = "INACTIVE",
    now_iso: str | None = None,
) -> Dict[str, Any]:
    ok, reason_code = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason_code)

    if emergency_stop_status == "ACTIVE":
        return _blocked("EMERGENCY_STOP_ACTIVE")

    ok, reason_code = validate_plan_integrity(input_data)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_validation_readiness(input_data["validation_plan"])
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_rollback_readiness(input_data["rollback_plan"])
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_final_approval(final_approval, now_iso)
    if not ok:
        if reason_code in {"FINAL_APPROVAL_MISSING", "FINAL_APPROVAL_STATEMENT_TOO_WEAK", "FINAL_APPROVAL_NOT_TRUE"}:
            return _review_required(reason_code)
        return _blocked(reason_code)

    ok, reason_code = validate_snapshot(snapshot)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_repo_state(repo_state)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = drift_guard(input_data, final_approval, snapshot, repo_state)
    if not ok:
        return _blocked(reason_code)

    execution_gate_id = stable_hash(
        {
            "plan_hash": input_data["plan_hash"],
            "approval_hash": final_approval["final_approval_id"],
            "snapshot_hash": snapshot["snapshot_hash"],
            "repo_head": repo_state["repo_head"],
            "approval_statement": final_approval["approval_statement"],
        }
    )

    execution_gate = {
        "execution_gate_id": execution_gate_id,
        "status": "READY_FOR_FINAL_EXECUTION_REVIEW",
        "validated_plan": input_data["controlled_plan"],
        "validated_snapshot": snapshot,
        "validated_rollback": input_data["rollback_plan"],
        "validated_validation": input_data["validation_plan"],
        "drift_baseline": {
            "plan_hash": input_data["plan_hash"],
            "approval_hash": final_approval["final_approval_id"],
            "snapshot_hash": snapshot["snapshot_hash"],
            "repo_head": repo_state["repo_head"],
        },
        "execution_permission": False,
        "handoff_target": "G-H",
    }

    if contains_command_token(execution_gate):
        return _blocked("COMMAND_OUTPUT_DETECTED")

    output = {
        "phase": "G",
        "subphase": "G-G",
        "status": "READY_FOR_FINAL_EXECUTION_REVIEW",
        "execution_gate": execution_gate,
        "reason_registry": [reason("GATE_READY_REVIEW_ONLY", "Ready for final execution review. Execution permission remains false.")],
        "decision": "READY_FOR_FINAL_EXECUTION_REVIEW",
        "deterministic": True,
        "execution_permission": False,
    }

    return _finalize(output)
