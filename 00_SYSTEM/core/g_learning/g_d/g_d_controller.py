from __future__ import annotations

from typing import Any, Dict, List

from .contract_validator import validate_input_contract
from .decision_matrix import classify_recommendation, quarantine_contract
from .false_optimization_guard import hidden_optimization_guard
from .hashing import stable_hash
from .no_action import no_action_output
from .reason_registry import add_reason
from .recommendation_validator import validate_recommendations
from .sealed_phase_guard import sealed_phase_guard
from .security_guard import security_guard
from .stability_guard import stability_guard


def _finalize(output: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    output["input_hash"] = stable_hash(input_data)
    output["risk_hash"] = stable_hash(output.get("risk_summary", {}))
    output["blocked_hash"] = stable_hash(output.get("blocked", []))
    output["quarantine_hash"] = stable_hash(output.get("quarantined", []))
    output["decision_hash"] = stable_hash(output.get("decision", ""))
    output["config_hash"] = stable_hash({"version": "G-D_v1.3"})
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    output = {
        "phase": "G",
        "subphase": "G-D",
        "status": "BLOCKED",
        "approved_for_review": [],
        "quarantined": [],
        "blocked": [],
        "risk_summary": {"state": "BLOCKED", "reason": reason},
        "reason_registry": [{"reason_code": reason, "recommendation_id": "", "reason_detail": reason}],
        "decision": "BLOCK",
        "deterministic": True,
    }
    return _finalize(output, input_data)


def run_g_d(input_data: Dict[str, Any]) -> Dict[str, Any]:
    ok, reason = validate_input_contract(input_data)
    if not ok:
        return _blocked(reason, input_data)

    if input_data["status"] == "NO_RECOMMENDATION" or input_data["decision"] == "NO_RECOMMENDATION":
        return _finalize(no_action_output(input_data), input_data)

    if input_data["status"] == "BLOCKED":
        return _blocked("SOURCE_BLOCKED", input_data)

    recommendations = input_data["recommendations"]

    ok, reason = validate_recommendations(recommendations)
    if not ok:
        return _blocked(reason, input_data)

    approved_for_review: List[Dict] = []
    quarantined: List[Dict] = []
    blocked: List[Dict] = []
    reason_registry: List[Dict] = []

    for recommendation in recommendations:
        rid = recommendation.get("recommendation_id", "")

        for guard in (sealed_phase_guard, hidden_optimization_guard, security_guard, stability_guard):
            ok, reason = guard(recommendation)
            if not ok:
                blocked.append(recommendation)
                add_reason(reason_registry, reason, rid)
                break
        else:
            decision = classify_recommendation(recommendation)

            if decision == "ALLOW_REVIEW":
                approved_for_review.append(recommendation)
            elif decision == "REVIEW_REQUIRED":
                quarantined.append(quarantine_contract(recommendation, "REVIEW_REQUIRED"))
                add_reason(reason_registry, "REVIEW_REQUIRED", rid)
            elif decision == "QUARANTINE":
                quarantined.append(quarantine_contract(recommendation, "HIGH_RISK_QUARANTINE"))
                add_reason(reason_registry, "HIGH_RISK_QUARANTINE", rid)
            elif decision == "BLOCK":
                blocked.append(recommendation)
                add_reason(reason_registry, "CRITICAL_RISK_BLOCKED", rid)

    final_decision = "NO_ACTION"
    status = "VALID"

    if blocked:
        final_decision = "BLOCK"
        status = "BLOCKED"
    elif quarantined:
        final_decision = "QUARANTINE"
        status = "REVIEW_REQUIRED"
    elif approved_for_review:
        final_decision = "ALLOW_REVIEW"
        status = "VALID"

    output = {
        "phase": "G",
        "subphase": "G-D",
        "status": status,
        "approved_for_review": approved_for_review,
        "quarantined": quarantined,
        "blocked": blocked,
        "risk_summary": {
            "approved_count": len(approved_for_review),
            "quarantined_count": len(quarantined),
            "blocked_count": len(blocked),
        },
        "reason_registry": reason_registry,
        "decision": final_decision,
        "deterministic": True,
    }

    return _finalize(output, input_data)
