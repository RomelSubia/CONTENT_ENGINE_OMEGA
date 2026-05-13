from __future__ import annotations

from typing import Any

EXPECTED_FINAL_CLOSURE_SUBJECT = "Close MANUAL-CEREBRO bridge final closure"
EXPECTED_BRIDGE_STATUS = "MANUAL_CEREBRO_BRIDGE_CLOSED_VALIDATED"


def validate_final_closure_subject(subject: str) -> dict[str, Any]:
    return {
        "status": "PASS" if subject == EXPECTED_FINAL_CLOSURE_SUBJECT else "BLOCK",
        "expected": EXPECTED_FINAL_CLOSURE_SUBJECT,
        "actual": subject,
    }


def validate_bridge_status(status: str) -> dict[str, Any]:
    return {
        "status": "PASS" if status == EXPECTED_BRIDGE_STATUS else "BLOCK",
        "expected": EXPECTED_BRIDGE_STATUS,
        "actual": status,
    }


def build_project_state_read_contract() -> dict[str, Any]:
    return {
        "status": "PASS",
        "read_only": True,
        "write_allowed": False,
        "expected_final_closure_subject": EXPECTED_FINAL_CLOSURE_SUBJECT,
        "expected_bridge_status": EXPECTED_BRIDGE_STATUS,
    }
