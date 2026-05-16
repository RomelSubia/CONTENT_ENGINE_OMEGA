from __future__ import annotations

from typing import Any


def build_prompt_failure_report(reason: str, failed_gate: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "status": "FAILED_BLOCKED",
        "failure_reason": reason,
        "failed_gate": failed_gate,
        "extra": extra or {},
        "commit_created": False,
        "push_performed": False,
        "prompt_governance_built": False,
        "prompt_production_started": False,
        "final_prompt_generation_started": False,
        "full_prompt_body_generation_started": False,
        "script_generation_started": False,
        "content_generation_started": False,
        "queue_write_started": False,
        "metrics_write_started": False,
        "asset_write_started": False,
        "publishing_started": False,
        "execution_started": False,
        "human_authorization_simulated": False,
        "manual_write_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
        "n8n_performed": False,
        "webhook_performed": False,
        "capa9_performed": False,
    }


def validate_prompt_failure_report(report: dict[str, Any]) -> dict[str, Any]:
    required_false = [
        "commit_created",
        "push_performed",
        "prompt_governance_built",
        "prompt_production_started",
        "final_prompt_generation_started",
        "full_prompt_body_generation_started",
        "script_generation_started",
        "content_generation_started",
        "queue_write_started",
        "metrics_write_started",
        "asset_write_started",
        "publishing_started",
        "execution_started",
        "human_authorization_simulated",
        "manual_write_performed",
        "brain_write_performed",
        "reports_brain_write_performed",
        "n8n_performed",
        "webhook_performed",
        "capa9_performed",
    ]
    failures = [key for key in required_false if report.get(key) is not False]
    if report.get("status") != "FAILED_BLOCKED":
        failures.append("status")
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}
