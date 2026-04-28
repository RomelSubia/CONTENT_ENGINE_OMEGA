from __future__ import annotations

from typing import Any, Dict

from .evidence_ingestion import ingest_evidence
from .evidence_registry import register_evidence
from .evidence_validator import validate_evidence
from .hashing import stable_hash


def run_g_a(input_data: Dict[str, Any]) -> Dict[str, Any]:
    input_hash = stable_hash(input_data)

    try:
        evidence = ingest_evidence(input_data)
        status, quality = validate_evidence(evidence)
        registry = register_evidence(evidence)
    except Exception as exc:
        output = {
            "phase": "G",
            "subphase": "G-A",
            "status": "BLOCKED",
            "evidence_count": 0,
            "evidence_quality": 0.0,
            "input_hash": input_hash,
            "deterministic": True,
            "final_decision": str(exc),
        }
        output["output_hash"] = stable_hash(output)
        return output

    final_decision = "NO_ACTION"

    if status == "VALID":
        final_decision = "EVIDENCE_ACCEPTED"
    elif status == "NO_LEARNING_ALLOWED":
        final_decision = "NO_LEARNING_ALLOWED"
    elif status == "REVIEW_REQUIRED":
        final_decision = "REVIEW_REQUIRED"
    else:
        final_decision = "BLOCKED"

    output = {
        "phase": "G",
        "subphase": "G-A",
        "status": status,
        "evidence_count": len(registry),
        "evidence_quality": quality,
        "input_hash": input_hash,
        "deterministic": True,
        "final_decision": final_decision,
    }

    output["output_hash"] = stable_hash(output)
    return output
