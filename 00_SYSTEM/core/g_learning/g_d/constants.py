from __future__ import annotations

REQUIRED_INPUT_KEYS = (
    "phase",
    "subphase",
    "status",
    "recommendations",
    "quarantined",
    "review_queue",
    "recommendation_count",
    "decision",
    "deterministic",
    "input_hash",
    "recommendation_hash",
    "config_hash",
    "output_hash",
)

REQUIRED_RECOMMENDATION_KEYS = (
    "recommendation_id",
    "confidence_score",
    "risk_level",
    "stability_impact",
    "touch_scope",
    "affects_phase",
    "rollback_required",
    "auto_apply_allowed",
    "requires_human_approval",
    "reversible",
    "evidence_ref",
    "statement",
)

SEALED_PHASES = {"F", "G-A", "G-B", "G-C"}

RISK_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_STABILITY_IMPACTS = {"NONE", "LOW", "MEDIUM", "HIGH"}

CONFIDENCE_MIN_REQUIRED = 0.75
CONFIDENCE_STRONG = 0.85
EVIDENCE_REF_MIN = 1

HIDDEN_OPTIMIZATION_TERMS = (
    "auto apply",
    "bypass",
    "skip audit",
    "reduce validation",
    "remove checks",
    "direct execution",
    "disable fail-closed",
    "modify sealed phase",
)
