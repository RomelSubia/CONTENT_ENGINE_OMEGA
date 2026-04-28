from __future__ import annotations

from typing import Any, Dict

from .constraints_guard import validate_constraints
from .drift_guard import drift_guard
from .hashing import stable_hash
from .input_contract import validate_gate_integrity, validate_input_contract
from .output_guard import contains_side_effect_token
from .permission_contract import validate_permission_contract
from .permission_usage_guard import validate_permission_usage
from .reason_registry import reason
from .repo_state_guard import validate_repo_state
from .risk_guard import validate_risk_analysis
from .runner_guard import validate_runner_lock
from .snapshot_guard import validate_snapshot_declared
from .trace_guard import validate_trace_chain


def _finalize(output: Dict[str, Any]) -> Dict[str, Any]:
    output["permission_hash"] = stable_hash(output.get("permission_package", {}))
    output["constraints_hash"] = stable_hash(output.get("constraints", {}))
    output["trace_hash"] = stable_hash(output.get("trace_chain", {}))
    output["risk_hash"] = stable_hash(output.get("risk_analysis", {}))
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason_code: str) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-H",
        "status": "BLOCKED",
        "logical_execution_permission_ready": False,
        "execution_permission": False,
        "permission_package": {},
        "constraints": {},
        "trace_chain": {},
        "risk_analysis": {},
        "execution_runner_target": "NONE",
        "reason_registry": [reason(reason_code)],
        "decision": "BLOCK",
        "deterministic": True,
    }
    return _finalize(output)


def _review_required(reason_code: str) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-H",
        "status": "REVIEW_REQUIRED",
        "logical_execution_permission_ready": False,
        "execution_permission": False,
        "permission_package": {},
        "constraints": {},
        "trace_chain": {},
        "risk_analysis": {},
        "execution_runner_target": "NONE",
        "reason_registry": [reason(reason_code)],
        "decision": "REVIEW_REQUIRED",
        "deterministic": True,
    }
    return _finalize(output)


def run_g_h(
    input_data: Dict[str, Any],
    permission_contract: Dict[str, Any] | None = None,
    permission_usage: Dict[str, Any] | None = None,
    snapshot: Dict[str, Any] | None = None,
    repo_state: Dict[str, Any] | None = None,
    constraints: Dict[str, Any] | None = None,
    trace_chain: Dict[str, Any] | None = None,
    risk_analysis: Dict[str, Any] | None = None,
    execution_runner_target: str = "G-I",
    now_iso: str | None = None,
) -> Dict[str, Any]:
    ok, reason_code = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_gate_integrity(input_data)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_permission_contract(permission_contract, now_iso)
    if not ok:
        if reason_code in {"PERMISSION_MISSING", "PERMISSION_STATEMENT_TOO_WEAK"}:
            return _review_required(reason_code)
        return _blocked(reason_code)

    ok, reason_code = validate_permission_usage(permission_usage)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_snapshot_declared(snapshot)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_repo_state(repo_state)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_constraints(constraints)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_trace_chain(trace_chain)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_runner_lock(execution_runner_target)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_risk_analysis(risk_analysis)
    if not ok:
        if reason_code == "RISK_MEDIUM_REVIEW_REQUIRED":
            return _review_required(reason_code)
        return _blocked(reason_code)

    ok, reason_code = drift_guard(input_data, permission_contract, snapshot, repo_state)
    if not ok:
        return _blocked(reason_code)

    trace_chain_final = dict(trace_chain)
    trace_chain_final["g_h"] = stable_hash(permission_contract)

    permission_id = stable_hash(
        {
            "gate_hash": input_data["gate_hash"],
            "execution_gate_id": input_data["execution_gate"]["execution_gate_id"],
            "snapshot_hash": input_data["snapshot_hash"],
            "repo_head": repo_state["repo_head"],
            "constraints_hash": constraints["constraints_hash"],
            "trace_chain_id": trace_chain["trace_id"],
            "permission_statement": permission_contract["permission_statement"],
        }
    )

    if permission_contract["permission_id"] != permission_id:
        return _blocked("PERMISSION_ID_MISMATCH")

    permission_package = {
        "permission_id": permission_id,
        "status": "EXECUTION_PERMISSION_READY",
        "logical_execution_permission_ready": True,
        "execution_permission": False,
        "execution_runner_target": execution_runner_target,
        "immutable": True,
        "validated_gate": input_data["execution_gate"],
        "validated_snapshot": snapshot,
        "validated_rollback": input_data["execution_gate"]["validated_rollback"],
        "validated_validation": input_data["execution_gate"]["validated_validation"],
        "permission_usage": permission_usage,
        "package_hash_source": {
            "gate_hash": input_data["gate_hash"],
            "snapshot_hash": input_data["snapshot_hash"],
            "repo_head": repo_state["repo_head"],
        },
    }

    permission_package["package_hash"] = stable_hash(permission_package)

    output = {
        "phase": "G",
        "subphase": "G-H",
        "status": "EXECUTION_PERMISSION_READY",
        "logical_execution_permission_ready": True,
        "execution_permission": False,
        "permission_package": permission_package,
        "constraints": constraints,
        "trace_chain": trace_chain_final,
        "risk_analysis": risk_analysis,
        "execution_runner_target": execution_runner_target,
        "reason_registry": [reason("PERMISSION_READY_LOGICAL_ONLY", "Logical permission ready; execution remains delegated to G-I.")],
        "decision": "EXECUTION_PERMISSION_READY",
        "deterministic": True,
    }

    if contains_side_effect_token(output):
        return _blocked("ZERO_SIDE_EFFECT_VIOLATION")

    return _finalize(output)
