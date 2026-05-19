"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


def build_generation_failure_report(reason: str, stage: str) -> dict:
    return {
        "status": "FAILED_BLOCKED",
        "reason": reason,
        "stage": stage,
        "commit_created": False,
        "push_performed": False,
        "content_generation_started": False,
        "draft_creation_started": False,
        "prompt_execution_started": False,
        "script_execution_started": False,
        "asset_generation_started": False,
        "publishing_started": False,
        "automation_started": False,
        "queue_write_performed": False,
        "real_queue_mutation_performed": False,
        "manual_write_performed": False,
        "brain_write_performed": False,
        "reports_brain_write_performed": False,
    }

def validate_generation_failure_report(report: dict) -> dict:
    if report.get("status") != "FAILED_BLOCKED":
        return {"status": "BLOCK", "reason": "FAILURE_REPORT_STATUS_INVALID"}
    forbidden_true = [key for key, value in report.items() if key.endswith(("started", "performed", "created")) and value is not False]
    if forbidden_true:
        return {"status": "BLOCK", "reason": "FAILURE_REPORT_HARD_FALSE_VIOLATION", "violations": forbidden_true}
    return {"status": "PASS", "reason": "FAILURE_POLICY_VALID"}
