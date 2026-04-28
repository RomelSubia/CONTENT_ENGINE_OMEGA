from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_VALIDATION_CHECKS


def validate_rollback_plan(rollback_plan: Dict) -> Tuple[bool, str]:
    required = (
        "rollback_strategy",
        "restore_point",
        "files_to_restore",
        "validation_after_rollback",
        "human_review_required",
    )

    missing = [key for key in required if key not in rollback_plan]
    if missing:
        return False, "MISSING_ROLLBACK_KEYS:" + ",".join(missing)

    if rollback_plan["human_review_required"] is not True:
        return False, "ROLLBACK_HUMAN_REVIEW_REQUIRED"

    if not isinstance(rollback_plan["validation_after_rollback"], list) or not rollback_plan["validation_after_rollback"]:
        return False, "ROLLBACK_VALIDATION_MISSING"

    return True, "ROLLBACK_OK"


def validate_validation_plan(validation_plan: Dict) -> Tuple[bool, str]:
    checks = validation_plan.get("checks")

    if not isinstance(checks, list):
        return False, "VALIDATION_CHECKS_NOT_LIST"

    missing = [check for check in REQUIRED_VALIDATION_CHECKS if check not in checks]
    if missing:
        return False, "MISSING_VALIDATION_CHECKS:" + ",".join(missing)

    return True, "VALIDATION_PLAN_OK"


def validate_review_package(review_package: Dict) -> Tuple[bool, str]:
    required = (
        "summary",
        "steps",
        "diff_preview",
        "risk_summary",
        "validation_plan",
        "rollback_plan",
        "decision_required",
    )

    missing = [key for key in required if key not in review_package]
    if missing:
        return False, "MISSING_REVIEW_PACKAGE_KEYS:" + ",".join(missing)

    if review_package["decision_required"] != "HUMAN_REVIEW_REQUIRED":
        return False, "REVIEW_DECISION_INVALID"

    return True, "REVIEW_PACKAGE_OK"
