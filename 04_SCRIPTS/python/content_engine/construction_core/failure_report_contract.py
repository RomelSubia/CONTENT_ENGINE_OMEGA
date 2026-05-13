from __future__ import annotations

from typing import Any


def build_failure_report(reason: str, failed_gate: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "FAILED_BLOCKED",
        "failure_reason": reason,
        "failed_gate": failed_gate,
        "extra": extra or {},
        "commit_created": False,
        "push_performed": False,
        "construction_core_built": False,
        "execution_started": False,
        "manual_write_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "n8n_performed": False,
        "webhook_performed": False,
        "publishing_performed": False,
        "capa9_performed": False,
    }


def validate_failure_report(report: dict[str, Any]) -> dict[str, Any]:
    required_false = [
        "commit_created",
        "push_performed",
        "construction_core_built",
        "execution_started",
        "manual_write_performed",
        "brain_write_performed",
        "reports_brain_write_performed",
        "n8n_performed",
        "webhook_performed",
        "publishing_performed",
        "capa9_performed",
    ]
    failures = [key for key in required_false if report.get(key) is not False]
    if report.get("status") != "FAILED_BLOCKED":
        failures.append("status")
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}
