from __future__ import annotations

from typing import Any

DANGEROUS_PERMISSIONS = {
    "content_engine_construction_validation_map_allowed_now": False,
    "content_engine_construction_validation_plan_allowed_now": False,
    "content_engine_construction_validation_allowed_now": False,
    "content_engine_construction_gate_closure_allowed_now": False,
    "content_generation_allowed_now": False,
    "asset_generation_allowed_now": False,
    "content_queue_write_allowed_now": False,
    "metrics_write_allowed_now": False,
    "monetization_allowed_now": False,
    "publishing_preparation_allowed_now": False,
    "publishing_execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "global_execution_allowed_now": False,
}

NEXT_PERMISSIONS = {
    "content_engine_construction_post_build_audit_allowed_next": True,
    **DANGEROUS_PERMISSIONS,
}


def build_permission_matrix() -> dict[str, bool]:
    return dict(NEXT_PERMISSIONS)


def dangerous_permissions_are_false(matrix: dict[str, Any] | None = None) -> bool:
    matrix = matrix or build_permission_matrix()
    return all(matrix.get(key) is False for key in DANGEROUS_PERMISSIONS)


def validate_permission_matrix(matrix: dict[str, Any] | None = None) -> dict[str, Any]:
    matrix = matrix or build_permission_matrix()
    escalated = [key for key in DANGEROUS_PERMISSIONS if matrix.get(key) is not False]
    next_ok = matrix.get("content_engine_construction_post_build_audit_allowed_next") is True
    return {
        "status": "PASS" if not escalated and next_ok else "BLOCK",
        "escalated": escalated,
        "post_build_audit_allowed_next": next_ok,
    }
