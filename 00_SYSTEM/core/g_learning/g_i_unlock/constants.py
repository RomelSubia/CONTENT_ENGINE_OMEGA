from __future__ import annotations

REQUIRED_EVIDENCE_KEYS = (
    "g_i_v13_audit_exists",
    "pytest_passed",
    "pytest_count",
    "no_mutation_pass",
    "controlled_run_locked",
    "repo_sync_valid",
    "commit_hash",
    "evidence_hash",
)

REQUIRED_APPROVAL_KEYS = (
    "unlock_approval_id",
    "approval_version",
    "approved_by",
    "identity_verified",
    "approval_scope",
    "approval_statement",
    "understands_mutation_risk",
    "understands_rollback_risk",
    "dry_run_evidence_reviewed",
    "secondary_confirmation",
    "revocation_status",
    "reuse_status",
    "approval_timestamp",
    "approval_expiration",
    "unlock_window",
)

REQUIRED_REPO_STATE_KEYS = (
    "repo_clean",
    "cache_clean",
    "head_equals_upstream",
    "no_pycache_tracked",
    "commit_hash",
)

APPROVAL_VERSION = "v1.4.1"
APPROVAL_SCOPE = "CONTROLLED_RUN_LIMITED_UNLOCK_REVIEW_ONLY"

UNLOCK_LEVEL = "LIMITED_REPORT_AUDIT_ONLY"
NEXT_PHASE_REQUIRED = "G-I v1.5"

ALLOWED_CAPABILITY_MODES = {"REPORT_ONLY", "AUDIT_ONLY"}
BLOCKED_CAPABILITY_MODES = {
    "STATE_ONLY",
    "FILE_WRITE",
    "METADATA_UPDATE",
    "SHELL",
    "SYSTEM",
}

FUTURE_ALLOWED_OPERATIONS = (
    "CONTROLLED_REPORT_GENERATION",
    "CONTROLLED_AUDIT_WRITE",
)

FUTURE_DENIED_OPERATIONS = (
    "CONTROLLED_FILE_WRITE",
    "CONTROLLED_METADATA_UPDATE",
    "CONTROLLED_STATE_MARK_USED",
    "DELETE",
    "MOVE",
    "SHELL_EXECUTION",
    "SYSTEM_COMMAND",
)

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
