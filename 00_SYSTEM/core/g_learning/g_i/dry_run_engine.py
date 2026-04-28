from __future__ import annotations

from typing import Dict

from .hashing import stable_hash


def build_mutation_ledger(operations) -> list[Dict]:
    ledger = []
    for operation in operations:
        ledger.append(
            {
                "operation_id": operation["operation_id"],
                "operation_type": operation["operation_type"],
                "target_path": operation["target_path"],
                "before_hash": None,
                "after_hash": None,
                "size_bytes": 0,
                "status": "SIMULATED",
            }
        )
    return ledger


def build_journal(request: Dict, input_data: Dict, ledger: list[Dict]) -> Dict:
    return {
        "journal_id": stable_hash(
            {
                "execution_request_id": request["execution_request_id"],
                "idempotency_key": request["idempotency_key"],
                "permission_hash": input_data["permission_hash"],
            }
        ),
        "execution_request_id": request["execution_request_id"],
        "permission_id": input_data["permission_package"].get("permission_id", ""),
        "mode": "DRY_RUN_ONLY",
        "steps": ledger,
        "pre_state_hash": stable_hash(input_data),
        "post_state_hash": stable_hash(input_data),
        "result": "DRY_RUN_PASS",
        "deterministic": True,
    }


def build_evidence(input_data: Dict, ledger: list[Dict], journal: Dict) -> Dict:
    return {
        "evidence_id": stable_hash(
            {
                "input_hash": stable_hash(input_data),
                "ledger_hash": stable_hash(ledger),
                "journal_hash": stable_hash(journal),
            }
        ),
        "mode": "DRY_RUN_ONLY",
        "input_hash": stable_hash(input_data),
        "ledger_hash": stable_hash(ledger),
        "journal_hash": stable_hash(journal),
        "result_hash": stable_hash({"status": "DRY_RUN_COMPLETED"}),
    }
