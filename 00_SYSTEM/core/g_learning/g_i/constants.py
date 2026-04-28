from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "logical_execution_permission_ready",
    "execution_permission",
    "permission_package",
    "constraints",
    "trace_chain",
    "risk_analysis",
    "execution_runner_target",
    "permission_hash",
    "output_hash",
    "deterministic",
)

REQUIRED_REQUEST_KEYS = (
    "execution_request_id",
    "request_version",
    "requested_by",
    "identity_verified",
    "execution_mode",
    "runner_capability_mode",
    "controlled_run_unlocked",
    "physical_mutation_allowed",
    "emergency_stop_status",
    "allowed_operations",
    "idempotency_key",
)

REQUEST_VERSION = "v1.3"
RUNNER_TARGET = "G-I"

ALLOWED_EXECUTION_MODES = {"DRY_RUN_ONLY", "CONTROLLED_RUN", "ROLLBACK_ONLY"}
ALLOWED_CAPABILITY_MODES = {"REPORT_ONLY", "AUDIT_ONLY"}

ALLOWED_OPERATION_TYPES = {
    "CONTROLLED_REPORT_GENERATION",
    "CONTROLLED_AUDIT_WRITE",
}

BLOCKED_OPERATION_TYPES = {
    "DELETE",
    "MASS_MOVE",
    "SHELL_EXECUTION",
    "SYSTEM_COMMAND",
    "NETWORK_DEPLOY",
    "SECRET_ACCESS",
    "UNSCOPED_WRITE",
    "CONTROLLED_FILE_WRITE",
    "CONTROLLED_METADATA_UPDATE",
    "CONTROLLED_STATE_MARK_USED",
}

ALLOWED_ROOTS = (
    "00_SYSTEM/reports",
    "00_SYSTEM/audit",
)

DENIED_ROOTS = (
    ".git",
    ".venv",
    "00_SYSTEM/core",
    "tests",
    "secrets",
    "config/private",
)

ALLOWED_EXTENSIONS = (".json", ".txt", ".md", ".csv")

FORBIDDEN_CODE_TERMS = (
    "subprocess",
    "os.system",
    "invoke-expression",
    "start-process",
    "powershell",
    "cmd.exe",
    "bash",
    "git push",
    "git commit",
)

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}
