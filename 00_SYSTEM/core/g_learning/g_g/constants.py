from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "controlled_plan",
    "validation_plan",
    "rollback_plan",
    "review_package",
    "decision",
    "deterministic",
    "plan_hash",
    "steps_hash",
    "diff_hash",
    "rollback_hash",
    "validation_hash",
    "review_hash",
    "output_hash",
)

REQUIRED_APPROVAL_KEYS = (
    "final_approval_id",
    "approval_version",
    "final_approval",
    "approved_by",
    "identity_verified",
    "approval_statement",
    "approval_scope",
    "understands_execution_risk",
    "rollback_acknowledged",
    "snapshot_acknowledged",
    "multi_step_confirmed",
    "revocation_status",
    "approval_timestamp",
    "approval_expiration",
    "source_plan_hash",
    "source_repo_head",
    "source_snapshot_hash",
)

REQUIRED_SNAPSHOT_KEYS = (
    "snapshot_id",
    "snapshot_hash",
    "snapshot_strategy",
    "snapshot_target",
)

REQUIRED_REPO_STATE_KEYS = (
    "repo_clean",
    "cache_clean",
    "head_equals_upstream",
    "no_pycache_tracked",
    "repo_head",
)

APPROVAL_VERSION = "v1.3"
APPROVAL_SCOPE = "EXECUTION_GATE_REVIEW_ONLY"

FORBIDDEN_OUTPUT_TERMS = (
    "powershell",
    "bash",
    "cmd.exe",
    "execute",
    "run",
    "apply",
    "patch",
    "deploy",
    "delete",
    "move",
    "write",
    "modify code",
    "git push",
    "git commit",
)

REQUIRED_VALIDATION_CHECKS = (
    "py_compile",
    "pytest",
    "determinism_check",
    "repo_clean_check",
    "cache_clean_check",
    "HEAD_equals_upstream",
    "audit_verification",
)
