from __future__ import annotations

from typing import Dict, List

from .hashing import stable_hash


def build_plan_id(input_data: Dict) -> str:
    return stable_hash(
        {
            "authorized_items": input_data["authorized_items"],
            "approval_hash": input_data["approval_hash"],
            "authorization_hash": input_data["authorization_hash"],
            "lineage_hash": input_data["lineage_hash"],
        }
    )


def build_steps(input_data: Dict) -> List[Dict]:
    steps = []

    for index, item in enumerate(input_data["authorized_items"]):
        recommendation_id = item.get("recommendation_id", f"item-{index}")
        risk = item.get("risk_level", "LOW")

        steps.append(
            {
                "step_id": stable_hash({"recommendation_id": recommendation_id, "index": index}),
                "action_type": "READ_ANALYZE",
                "target_type": "REPORT",
                "target": f"reports/controlled_plan/{recommendation_id}",
                "allowed_scope": "READ_ONLY",
                "risk_level": risk,
                "execution_allowed": False,
            }
        )

    return steps


def build_diff_preview(steps: List[Dict]) -> Dict:
    return {
        "affected_modules": [],
        "expected_changes": [],
        "impact_level": "LOW",
        "description": "Read-only planning preview. No file, code, or runtime modification is allowed.",
    }


def build_validation_plan() -> Dict:
    return {
        "checks": [
            "py_compile",
            "pytest",
            "determinism_check",
            "repo_clean_check",
            "cache_clean_check",
            "HEAD_equals_upstream",
            "audit_verification",
        ]
    }


def build_rollback_plan() -> Dict:
    return {
        "rollback_strategy": "NO_RUNTIME_CHANGE_PLAN_ONLY",
        "restore_point": "current_git_HEAD",
        "files_to_restore": [],
        "validation_after_rollback": [
            "pytest",
            "repo_clean_check",
            "HEAD_equals_upstream",
        ],
        "human_review_required": True,
    }


def build_review_package(steps: List[Dict], diff_preview: Dict, validation_plan: Dict, rollback_plan: Dict) -> Dict:
    return {
        "summary": "Controlled plan package for human review only. Execution is not allowed in G-F.",
        "steps": steps,
        "diff_preview": diff_preview,
        "risk_summary": {
            "risk_level": "LOW",
            "execution_allowed": False,
        },
        "validation_plan": validation_plan,
        "rollback_plan": rollback_plan,
        "decision_required": "HUMAN_REVIEW_REQUIRED",
    }
