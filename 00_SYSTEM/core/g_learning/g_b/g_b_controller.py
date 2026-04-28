from __future__ import annotations

from typing import Any, Dict

from .confidence_engine import calculate_confidence
from .contract_validator import validate_input_contract, validate_records
from .contradiction_detector import detect_contradictions
from .false_learning_guard import false_learning_guard
from .hashing import stable_hash
from .hypothesis_layer import anti_causality_guard, build_hypotheses
from .pattern_detector import detect_patterns
from .signal_analyzer import analyze_signals


def _blocked(reason: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-B",
        "status": "BLOCKED",
        "patterns": [],
        "signals": [],
        "hypotheses": [],
        "confidence_score": 0.0,
        "pattern_state": "BLOCKED",
        "false_learning_flags": [{"type": reason}],
        "deterministic": True,
        "input_hash": stable_hash(input_data),
        "records_hash": "",
        "config_hash": stable_hash({"version": "G-B_v1.5"}),
        "final_decision": reason,
    }
    output["output_hash"] = stable_hash(output)
    return output


def run_g_b(input_data: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason, input_data)

    records = input_data["records"]

    ok, reason = validate_records(records)
    if not ok:
        return _blocked(reason, input_data)

    evidence_quality = float(input_data["evidence_quality"])
    evidence_count = int(input_data["evidence_count"])

    patterns = detect_patterns(records)

    if not patterns:
        output = {
            "phase": "G",
            "subphase": "G-B",
            "status": "NO_PATTERN_FOUND",
            "patterns": [],
            "signals": [],
            "hypotheses": [],
            "confidence_score": 0.0,
            "pattern_state": "NO_PATTERN_FOUND",
            "false_learning_flags": [],
            "deterministic": True,
            "input_hash": stable_hash(input_data),
            "records_hash": stable_hash(records),
            "config_hash": stable_hash({"version": "G-B_v1.5"}),
            "final_decision": "NO_PATTERN_FOUND",
        }
        output["output_hash"] = stable_hash(output)
        return output

    contradictions = detect_contradictions(patterns, records)
    confidence = calculate_confidence(patterns, evidence_quality, contradictions)
    signals = analyze_signals(patterns, evidence_quality, confidence)
    hypotheses = build_hypotheses(patterns)

    if not anti_causality_guard(hypotheses):
        return _blocked("CAUSALITY_CLAIM_BLOCKED", input_data)

    clear, false_learning_flags = false_learning_guard(
        patterns=patterns,
        signals=signals,
        evidence_count=evidence_count,
        evidence_quality=evidence_quality,
        contradictions=contradictions,
    )

    status = "VALID"
    pattern_state = "VALID"
    final_decision = "LEARNING_REPORT_READY"

    if contradictions:
        status = "REVIEW_REQUIRED"
        pattern_state = "CONFLICTING_PATTERN"
        final_decision = "REVIEW_REQUIRED"

    if not clear:
        if status == "VALID":
            status = "FALSE_LEARNING_DETECTED"
            pattern_state = "FALSE_LEARNING_DETECTED"
            final_decision = "FALSE_LEARNING_DETECTED"

    output = {
        "phase": "G",
        "subphase": "G-B",
        "status": status,
        "patterns": patterns,
        "signals": signals,
        "hypotheses": hypotheses,
        "confidence_score": confidence,
        "pattern_state": pattern_state,
        "false_learning_flags": false_learning_flags,
        "deterministic": True,
        "input_hash": stable_hash(input_data),
        "records_hash": stable_hash(records),
        "config_hash": stable_hash({"version": "G-B_v1.5"}),
        "final_decision": final_decision,
    }

    output["output_hash"] = stable_hash(output)
    return output
