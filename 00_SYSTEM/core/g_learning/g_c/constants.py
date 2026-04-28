from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "pattern_state",
    "confidence_score",
    "patterns",
    "signals",
    "hypotheses",
    "false_learning_flags",
    "deterministic",
    "input_hash",
    "records_hash",
    "config_hash",
    "output_hash",
)

SEALED_PHASES = {"F", "G-A", "G-B"}
PROTECTED_AREAS = {"security", "fail-closed", "governance", "repo_structure", "determinism"}

CONFIDENCE_MIN_GENERATE = 0.75
CONFIDENCE_MIN_PROMOTE = 0.85

RISK_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

VALID_OUTPUT_TYPES = {
    "INSIGHT",
    "ADVICE",
    "RECOMMENDATION",
    "OPTIMIZATION_CANDIDATE",
}

FORBIDDEN_OUTPUT_TYPES = {
    "PATCH",
    "CODE_CHANGE",
    "AUTO_FIX",
    "FILE_MOVE",
    "DELETE",
    "EXECUTION_PLAN",
}
