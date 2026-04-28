from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_VALIDATION_CHECKS


def validate_plan_integrity(input_data: Dict) -> Tuple[bool, str]:
    plan = input_data["controlled_plan"]

    if plan.get("execution_allowed") is not False:
        return False, "PLAN_EXECUTION_ALLOWED_FORBIDDEN"

    if plan.get("allowed_scope") != "READ_ONLY_ANALYSIS_AND_PLAN_ONLY":
        return False, "INVALID_PLAN_SCOPE"

    if not isinstance(plan.get("steps"), list) or not plan["steps"]:
        return False, "PLAN_STEPS_EMPTY"

    if not isinstance(plan.get("diff_preview"), dict) or not plan["diff_preview"]:
        return False, "DIFF_PREVIEW_MISSING"

    return True, "PLAN_INTEGRITY_OK"


def validate_validation_readiness(validation_plan: Dict) -> Tuple[bool, str]:
    checks = validation_plan.get("checks")

    if not isinstance(checks, list):
        return False, "VALIDATION_CHECKS_NOT_LIST"

    missing = [check for check in REQUIRED_VALIDATION_CHECKS if check not in checks]
    if missing:
        return False, "MISSING_VALIDATION_CHECKS:" + ",".join(missing)

    return True, "VALIDATION_READY"


def validate_rollback_readiness(rollback_plan: Dict) -> Tuple[bool, str]:
    required = (
        "rollback_strategy",
        "restore_point",
        "validation_after_rollback",
        "human_review_required",
    )

    missing = [key for key in required if key not in rollback_plan]
    if missing:
        return False, "MISSING_ROLLBACK_KEYS:" + ",".join(missing)

    if rollback_plan["human_review_required"] is not True:
        return False, "ROLLBACK_HUMAN_REVIEW_REQUIRED"

    return True, "ROLLBACK_READY"
