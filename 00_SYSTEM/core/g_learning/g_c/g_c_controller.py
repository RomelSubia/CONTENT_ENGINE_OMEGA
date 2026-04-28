from __future__ import annotations

from typing import Any, Dict

from .boundary_guard import validate_boundaries
from .contract_validator import validate_input_contract
from .deduplication_engine import deduplicate_recommendations
from .hashing import stable_hash
from .no_action_guard import build_no_recommendation, no_action_required
from .policy_guard import validate_policy
from .recommendation_builder import build_recommendations
from .recommendation_validator import validate_recommendations
from .review_queue import build_review_queue
from .stability_gate import validate_stability


def _blocked(reason: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-C",
        "status": "BLOCKED",
        "recommendations": [],
        "quarantined": [],
        "review_queue": [],
        "recommendation_count": 0,
        "decision": reason,
        "deterministic": True,
        "input_hash": stable_hash(input_data),
        "recommendation_hash": "",
        "config_hash": stable_hash({"version": "G-C_v1.3"}),
    }
    output["output_hash"] = stable_hash(output)
    return output


def run_g_c(input_data: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason, input_data)

    if no_action_required(input_data):
        base = build_no_recommendation()
        output = {
            "phase": "G",
            "subphase": "G-C",
            "status": base["status"],
            "recommendations": [],
            "quarantined": [],
            "review_queue": [],
            "recommendation_count": 0,
            "decision": base["decision"],
            "deterministic": True,
            "input_hash": stable_hash(input_data),
            "recommendation_hash": stable_hash([]),
            "config_hash": stable_hash({"version": "G-C_v1.3"}),
        }
        output["output_hash"] = stable_hash(output)
        return output

    recommendations = build_recommendations(input_data)
    recommendations = deduplicate_recommendations(recommendations)

    ok, reason = validate_recommendations(recommendations)
    if not ok:
        return _blocked(reason, input_data)

    ok, reason = validate_boundaries(recommendations)
    if not ok:
        return _blocked(reason, input_data)

    ok, reason = validate_stability(recommendations)
    if not ok:
        return _blocked(reason, input_data)

    ok, reason = validate_policy(recommendations)
    if not ok:
        return _blocked(reason, input_data)

    review_queue, quarantined, decision = build_review_queue(recommendations)

    status = "VALID"
    if decision == "REVIEW_REQUIRED":
        status = "REVIEW_REQUIRED"
    elif decision == "NO_RECOMMENDATION":
        status = "NO_RECOMMENDATION"

    output = {
        "phase": "G",
        "subphase": "G-C",
        "status": status,
        "recommendations": recommendations,
        "quarantined": quarantined,
        "review_queue": review_queue,
        "recommendation_count": len(recommendations),
        "decision": decision,
        "deterministic": True,
        "input_hash": stable_hash(input_data),
        "recommendation_hash": stable_hash(recommendations),
        "config_hash": stable_hash({"version": "G-C_v1.3"}),
    }

    output["output_hash"] = stable_hash(output)
    return output
