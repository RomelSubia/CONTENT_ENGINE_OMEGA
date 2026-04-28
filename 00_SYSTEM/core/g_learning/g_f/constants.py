from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "authorized_items",
    "pending_items",
    "blocked_items",
    "decision",
    "deterministic",
    "approval_hash",
    "scope_hash",
    "lineage_hash",
    "intent_hash",
    "authorization_hash",
    "output_hash",
)

ALLOWED_ACTIONS = {"READ_ANALYZE", "INSPECT", "VALIDATE", "SIMULATE"}
DENIED_ACTIONS = {"WRITE", "DELETE", "MOVE", "EXECUTE", "PATCH", "DEPLOY", "APPLY", "RUN"}

ALLOWED_TARGET_TYPES = {"FILE", "MODULE", "REPORT", "LOG", "METADATA"}
DENIED_TARGET_TERMS = (
    "core system",
    "security",
    ".git",
    "git",
    "sealed",
    "fail-closed",
    "g_learning/g_a",
    "g_learning/g_b",
    "g_learning/g_c",
    "g_learning/g_d",
    "g_learning/g_e",
)

FORBIDDEN_EXECUTION_TERMS = (
    "execute",
    "run",
    "apply",
    "patch",
    "deploy",
    "delete",
    "move",
    "write",
    "modify code",
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
