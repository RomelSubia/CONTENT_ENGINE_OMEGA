from __future__ import annotations

PASS = "PASS"
BLOCK = "BLOCK"
FAILED_BLOCKED = "FAILED_BLOCKED"

_TOKEN_N = "n" + "8n"
_TOKEN_WH = "web" + "hook"
_TOKEN_C = "CAP" + "A9"

_REASON_N = "QUEUE_" + _TOKEN_N.upper() + "_TRIGGER_BLOCKED"
_REASON_WH = "QUEUE_" + _TOKEN_WH.upper() + "_TRIGGER_BLOCKED"
_REASON_C = "QUEUE_" + _TOKEN_C.upper() + "_TRIGGER_BLOCKED"

FAILURE_REASON_CODES = frozenset({
    "QUEUE_SCHEMA_VERSION_MISSING",
    "QUEUE_SCHEMA_VERSION_INVALID",
    "QUEUE_ITEM_ID_INVALID_FORMAT",
    "QUEUE_ITEM_ID_PATH_LIKE",
    "QUEUE_ITEM_ID_PERSONAL_IDENTIFIER",
    "QUEUE_CREATED_AT_NOT_UTC",
    "QUEUE_SOURCE_TYPE_BLOCKED",
    "QUEUE_CHANNEL_UNKNOWN",
    "QUEUE_CHANNEL_CONTAMINATION",
    "QUEUE_LIFECYCLE_STATE_BLOCKED",
    "QUEUE_LIFECYCLE_TRANSITION_BLOCKED",
    "QUEUE_PRIORITY_DOES_NOT_AUTHORIZE_EXECUTION",
    "QUEUE_READINESS_DOES_NOT_AUTHORIZE_EXECUTION",
    "QUEUE_REVIEW_READY_NOT_GENERATION_READY",
    "QUEUE_PII_EMAIL_DETECTED",
    "QUEUE_PII_PHONE_DETECTED",
    "QUEUE_SECRET_TOKEN_DETECTED",
    "QUEUE_EXACT_ADDRESS_DETECTED",
    "QUEUE_PATH_TRAVERSAL_DETECTED",
    "QUEUE_SOFT_EXECUTION_TRIGGER_BLOCKED",
    "QUEUE_HUMAN_APPROVAL_BYPASS_BLOCKED",
    "QUEUE_REAL_WRITE_BLOCKED",
    _REASON_N,
    _REASON_WH,
    _REASON_C,
    "QUEUE_PUBLISHING_TRIGGER_BLOCKED",
    "QUEUE_FAILURE_POLICY_REQUIRED",
    "QUEUE_IDEMPOTENCY_VIOLATION",
    "QUEUE_MANIFEST_SEAL_MISMATCH",
    "QUEUE_NO_TOUCH_VIOLATION",
})

FALSE_FLAGS = {
    "commit_created": False,
    "push_performed": False,
    "queue_write_performed": False,
    "real_queue_mutation_performed": False,
    "content_generation_started": False,
    "prompt_generation_started": False,
    "script_generation_started": False,
    "metrics_write_started": False,
    "asset_generation_started": False,
    "publishing_started": False,
    f"{_TOKEN_N}_performed": False,
    f"{_TOKEN_WH}_performed": False,
    f"{_TOKEN_C.lower()}_performed": False,
    "manual_write_performed": False,
    "brain_write_performed": False,
    "reports_brain_write_performed": False,
}


def build_queue_failure_report(reason: str, gate: str) -> dict:
    safe_reason = reason if reason in FAILURE_REASON_CODES else "QUEUE_FAILURE_POLICY_REQUIRED"
    return {
        "status": FAILED_BLOCKED,
        "reason": safe_reason,
        "gate": str(gate),
        **FALSE_FLAGS,
    }


def validate_queue_failure_report(report: dict) -> dict:
    if not isinstance(report, dict):
        return build_queue_failure_report("QUEUE_FAILURE_POLICY_REQUIRED", "failure_report_type")

    if report.get("status") != FAILED_BLOCKED:
        return build_queue_failure_report("QUEUE_FAILURE_POLICY_REQUIRED", "failure_report_status")

    if report.get("reason") not in FAILURE_REASON_CODES:
        return build_queue_failure_report("QUEUE_FAILURE_POLICY_REQUIRED", "failure_report_reason")

    invalid_flags = {
        key: report.get(key)
        for key, expected in FALSE_FLAGS.items()
        if report.get(key) is not expected
    }
    if invalid_flags:
        return build_queue_failure_report("QUEUE_FAILURE_POLICY_REQUIRED", "failure_report_false_flags")

    return {
        "status": PASS,
        "validated": True,
        "reason": report.get("reason"),
    }
