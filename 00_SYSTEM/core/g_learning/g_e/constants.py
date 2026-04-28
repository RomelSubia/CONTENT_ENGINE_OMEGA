from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "approved_for_review",
    "quarantined",
    "blocked",
    "decision",
    "deterministic",
    "input_hash",
    "risk_hash",
    "decision_hash",
    "output_hash",
)

REQUIRED_APPROVAL_KEYS = (
    "approval_id",
    "approval_version",
    "human_approval",
    "approved_by",
    "identity_verified",
    "approval_statement",
    "approval_intent",
    "approved_items",
    "approval_scope",
    "understands_risk",
    "rollback_acknowledged",
    "multi_step_confirmed",
    "approval_timestamp",
    "approval_expiration",
    "revocation_status",
    "source_input_hash",
    "source_risk_hash",
    "source_decision_hash",
)

ALLOWED_SCOPE = "CONTROLLED_PLAN_ONLY"
ALLOWED_INTENT = "CONTROLLED_PLAN_ONLY"
APPROVAL_VERSION = "v1.3"

AMBIGUOUS_APPROVALS = {
    "ok",
    "dale",
    "si",
    "sí",
    "aprobado",
    "hazlo",
    "👍",
}

FORBIDDEN_EXECUTION_TERMS = (
    "execute",
    "run",
    "apply",
    "patch",
    "deploy",
    "delete",
    "move",
    "modify code",
    "auto_execute",
    "execute_now",
)
