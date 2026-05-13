from __future__ import annotations

from typing import Any

from .build_boundary_planner import ALLOWED_ROOTS, PROTECTED_ROOTS
from .domain_registry import DOMAINS
from .evidence_contract_engine import canonical_json, sha256_text
from .permission_matrix import build_permission_matrix


def build_construction_plan() -> dict[str, Any]:
    plan = {
        "status": "PASS",
        "target": "CONTENT_ENGINE_CONSTRUCTION_CORE",
        "modules": [
            "state_contract",
            "permission_matrix",
            "project_state_reader",
            "domain_registry",
            "build_boundary_planner",
            "evidence_contract_engine",
            "construction_plan_kernel",
            "no_touch_validator",
            "failure_report_contract",
        ],
        "domains": list(DOMAINS),
        "allowed_roots": list(ALLOWED_ROOTS),
        "protected_roots": list(PROTECTED_ROOTS),
        "permissions": build_permission_matrix(),
        "execution_allowed_now": False,
    }
    plan["plan_hash"] = sha256_text(canonical_json({k: v for k, v in plan.items() if k != "plan_hash"}))
    return plan


def validate_construction_plan(plan: dict[str, Any] | None = None) -> dict[str, Any]:
    plan = plan or build_construction_plan()
    failures = []
    if plan.get("target") != "CONTENT_ENGINE_CONSTRUCTION_CORE":
        failures.append("target")
    if plan.get("execution_allowed_now") is not False:
        failures.append("execution_allowed_now")
    if not plan.get("modules"):
        failures.append("modules")
    return {"status": "PASS" if not failures else "BLOCK", "failures": failures}


def deterministic_plan_hash() -> str:
    first = build_construction_plan()["plan_hash"]
    second = build_construction_plan()["plan_hash"]
    if first != second:
        return "NON_DETERMINISTIC"
    return first
