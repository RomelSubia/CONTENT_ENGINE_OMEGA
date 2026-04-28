from __future__ import annotations

from typing import Any, Dict

from .dry_run_engine import build_evidence, build_journal, build_mutation_ledger
from .execution_request import validate_execution_request
from .hashing import stable_hash
from .input_contract import validate_input_contract
from .no_shell_guard import scan_no_shell
from .reason_registry import reason
from .risk_guard import validate_risk
from .sandbox_guard import validate_operations


def _finalize(output: Dict[str, Any]) -> Dict[str, Any]:
    output["execution_hash"] = stable_hash(output.get("dry_run_result", {}))
    output["ledger_hash"] = stable_hash(output.get("mutation_ledger", []))
    output["journal_hash"] = stable_hash(output.get("journal", {}))
    output["evidence_hash"] = stable_hash(output.get("evidence_artifact", {}))
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason_code: str) -> Dict[str, Any]:
    return _finalize(
        {
            "phase": "G",
            "subphase": "G-I",
            "status": "EXECUTION_BLOCKED",
            "execution_mode": "DRY_RUN_ONLY",
            "physical_mutation_allowed": False,
            "mutation_ledger": [],
            "transaction_state": "TRANSACTION_BLOCKED",
            "permission_state": "UNUSED",
            "dry_run_result": {},
            "evidence_artifact": {},
            "journal": {},
            "reason_registry": [reason(reason_code)],
            "decision": "BLOCK",
            "deterministic": True,
        }
    )


def _review_required(reason_code: str) -> Dict[str, Any]:
    return _finalize(
        {
            "phase": "G",
            "subphase": "G-I",
            "status": "REVIEW_REQUIRED",
            "execution_mode": "DRY_RUN_ONLY",
            "physical_mutation_allowed": False,
            "mutation_ledger": [],
            "transaction_state": "TRANSACTION_BLOCKED",
            "permission_state": "UNUSED",
            "dry_run_result": {},
            "evidence_artifact": {},
            "journal": {},
            "reason_registry": [reason(reason_code)],
            "decision": "REVIEW_REQUIRED",
            "deterministic": True,
        }
    )


def run_g_i(input_data: Dict[str, Any], execution_request: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason_code = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_execution_request(execution_request)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = scan_no_shell(execution_request)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = scan_no_shell(input_data)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_risk(input_data)
    if not ok:
        if reason_code == "RISK_MEDIUM_REVIEW_REQUIRED":
            return _review_required(reason_code)
        return _blocked(reason_code)

    operations = execution_request["allowed_operations"]

    ok, reason_code = validate_operations(operations)
    if not ok:
        return _blocked(reason_code)

    ledger = build_mutation_ledger(operations)
    journal = build_journal(execution_request, input_data, ledger)
    evidence = build_evidence(input_data, ledger, journal)

    dry_run_result = {
        "result": "PASS",
        "would_modify": [item["target_path"] for item in ledger],
        "estimated_operations": len(ledger),
        "rollback_possible": True,
        "risk_after_dry_run": "LOW",
    }

    output = {
        "phase": "G",
        "subphase": "G-I",
        "status": "DRY_RUN_COMPLETED",
        "execution_mode": "DRY_RUN_ONLY",
        "physical_mutation_allowed": False,
        "mutation_ledger": ledger,
        "transaction_state": "TRANSACTION_READY",
        "permission_state": "UNUSED",
        "dry_run_result": dry_run_result,
        "evidence_artifact": evidence,
        "journal": journal,
        "reason_registry": [reason("DRY_RUN_COMPLETED_NO_MUTATION", "Dry run completed without physical mutation.")],
        "decision": "DRY_RUN_PASS",
        "deterministic": True,
    }

    return _finalize(output)
