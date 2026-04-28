from __future__ import annotations

from typing import Any, Dict, List, Literal, TypedDict


Status = Literal[
    "VALID",
    "WARNING",
    "REVIEW_REQUIRED",
    "NO_LEARNING_ALLOWED",
    "BLOCKED",
    "CRITICAL",
]


class EvidenceInput(TypedDict):
    execution_id: str
    timestamp: str
    source_phase: str
    logs: List[Dict[str, Any]]
    metrics: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    outcomes: List[Dict[str, Any]]


class EvidenceOutput(TypedDict):
    phase: str
    subphase: str
    status: Status
    evidence_count: int
    evidence_quality: float
    input_hash: str
    output_hash: str
    deterministic: bool
    final_decision: str
