from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "execution_gate",
    "execution_permission",
    "gate_hash",
    "snapshot_hash",
    "validation_hash",
    "rollback_hash",
    "drift_hash",
    "output_hash",
    "deterministic",
)

REQUIRED_PERMISSION_KEYS = (
    "permission_id",
    "permission_version",
    "requested_by",
    "identity_verified",
    "permission_statement",
    "permission_scope",
    "dual_consent",
    "secondary_confirmation",
    "revocation_status",
    "permission_timestamp",
    "permission_expiration",
    "execution_window",
    "environment",
    "source_gate_hash",
    "source_snapshot_hash",
    "source_repo_head",
    "constraints_hash",
    "trace_chain_id",
)

REQUIRED_REPO_STATE_KEYS = (
    "repo_clean",
    "cache_clean",
    "head_equals_upstream",
    "no_pycache_tracked",
    "repo_head",
)

REQUIRED_PERMISSION_USAGE_KEYS = (
    "used",
    "single_use",
    "usage_hash",
)

PERMISSION_VERSION = "v1.3"
PERMISSION_SCOPE = "CONTROLLED_EXECUTION_PERMISSION_ONLY"
RUNNER_TARGET = "G-I"

FORBIDDEN_OUTPUT_TERMS = (
    "powershell",
    "bash",
    "cmd.exe",
    "execute now",
    "run now",
    "apply patch",
    "deploy now",
    "delete now",
    "move now",
    "git push",
    "git commit",
)

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
