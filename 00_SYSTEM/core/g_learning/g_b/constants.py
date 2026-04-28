from __future__ import annotations

VALID_RECORD_TYPES = {"logs", "metrics", "decisions", "outcomes"}
VALID_STATUSES = {
    "VALID",
    "WARNING",
    "REVIEW_REQUIRED",
    "NO_PATTERN_FOUND",
    "INSUFFICIENT_PATTERN_EVIDENCE",
    "CONFLICTING_PATTERN",
    "FALSE_LEARNING_DETECTED",
    "BLOCKED",
    "CRITICAL",
}

REQUIRED_INPUT_KEYS = (
    "phase",
    "source_subphase",
    "status",
    "evidence_quality",
    "evidence_count",
    "records",
    "input_hash",
    "output_hash",
)

REQUIRED_RECORD_KEYS = (
    "type",
    "index",
    "data",
    "source_hash",
    "origin",
    "timestamp",
)
