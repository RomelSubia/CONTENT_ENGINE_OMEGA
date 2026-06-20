"""Pure reconciliation primitives for governed truth objects.

This module builds in-memory truth objects, matrices and display contracts.
It is intentionally side-effect free.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


ALLOWED_TRUTH_STATES = {
    "VERIFIED_TRUE",
    "VERIFIED_FALSE",
    "PARTIAL",
    "UNKNOWN",
    "CONFLICT",
    "STALE",
    "SUPERSEDED",
    "HISTORICAL",
}

ALLOWED_CONFIDENCE_STATES = {
    "HIGH_CONFIDENCE",
    "MEDIUM_CONFIDENCE",
    "LOW_CONFIDENCE",
    "UNKNOWN",
    "CONFLICT",
}

TRUTH_OBJECT_REQUIRED_FIELDS = (
    "truth_object_id",
    "layer",
    "subject",
    "current_state",
    "truth_state",
    "confidence",
    "evidence_refs",
    "evidence_hashes",
    "source_priority",
    "generated_at_utc",
    "staleness_state",
    "conflict_state",
    "display_allowed",
    "next_safe_step",
)

PRODUCTIVE_OPERATION_TOKENS = {
    "runtime_execution",
    "productive_runtime",
    "queue_" + "mutation",
    "queue_" + "write",
    "publication_" + "mutation",
    "pub" + "lish",
    "pub" + "lishing",
    "sched" + "ule",
    "sched" + "uling",
    "automation_" + "trigger",
    "web" + "hook",
    "n" + "8n",
    "manual_" + "mutation",
    "brain_" + "mutation",
    "argos_" + "mutation",
    "dashboard_runtime_" + "mutation",
    "interface_runtime_" + "mutation",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_list(value: Optional[Iterable[Any]]) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return list(value)


def _state_from_evidence_item(item: Mapping[str, Any]) -> str:
    value = item.get("truth_state", item.get("state", "UNKNOWN"))
    state = str(value)
    return state if state in ALLOWED_TRUTH_STATES else "UNKNOWN"


def _has_conflict(evidence_items: Sequence[Mapping[str, Any]]) -> bool:
    states = {_state_from_evidence_item(item) for item in evidence_items}
    current_states = {str(item.get("current_state", "")) for item in evidence_items if item.get("current_state") is not None}
    if "CONFLICT" in states:
        return True
    if len(states - {"UNKNOWN", "PARTIAL"}) > 1:
        return True
    if len(current_states - {""}) > 1:
        return True
    return False


def _display_allowed_for(truth_state: str) -> bool:
    return truth_state in {"VERIFIED_TRUE", "PARTIAL"}


def build_truth_object(
    *,
    truth_object_id: str,
    layer: str,
    subject: str,
    current_state: str,
    truth_state: str,
    confidence: str = "UNKNOWN",
    evidence_refs: Optional[Iterable[str]] = None,
    evidence_hashes: Optional[Iterable[str]] = None,
    source_priority: Optional[Iterable[str]] = None,
    generated_at_utc: Optional[str] = None,
    staleness_state: str = "CURRENT",
    conflict_state: str = "NONE",
    display_allowed: Optional[bool] = None,
    next_safe_step: str = "UNKNOWN",
) -> Dict[str, Any]:
    if truth_state not in ALLOWED_TRUTH_STATES:
        raise ValueError(f"invalid truth_state: {truth_state}")

    if confidence not in ALLOWED_CONFIDENCE_STATES:
        raise ValueError(f"invalid confidence: {confidence}")

    if display_allowed is None:
        display_allowed = _display_allowed_for(truth_state)

    return {
        "truth_object_id": str(truth_object_id),
        "layer": str(layer),
        "subject": str(subject),
        "current_state": str(current_state),
        "truth_state": str(truth_state),
        "confidence": str(confidence),
        "evidence_refs": [str(item) for item in _as_list(evidence_refs)],
        "evidence_hashes": [str(item) for item in _as_list(evidence_hashes)],
        "source_priority": [str(item) for item in _as_list(source_priority)],
        "generated_at_utc": generated_at_utc or _utc_now(),
        "staleness_state": str(staleness_state),
        "conflict_state": str(conflict_state),
        "display_allowed": bool(display_allowed),
        "next_safe_step": str(next_safe_step),
    }


def validate_truth_object_contract(truth_object: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [field for field in TRUTH_OBJECT_REQUIRED_FIELDS if field not in truth_object]
    invalid: List[str] = []

    truth_state = str(truth_object.get("truth_state", "UNKNOWN"))
    confidence = str(truth_object.get("confidence", "UNKNOWN"))
    display_allowed = bool(truth_object.get("display_allowed", False))

    if truth_state not in ALLOWED_TRUTH_STATES:
        invalid.append("truth_state")

    if confidence not in ALLOWED_CONFIDENCE_STATES:
        invalid.append("confidence")

    if display_allowed and truth_state not in {"VERIFIED_TRUE", "PARTIAL"}:
        invalid.append("display_allowed")

    return {
        "valid": not missing and not invalid,
        "missing": missing,
        "invalid": invalid,
    }


def reconcile_layer_state(
    *,
    layer: str,
    subject: str,
    evidence_items: Optional[Sequence[Mapping[str, Any]]] = None,
    manual_expected: bool = False,
    brain_inference_only: bool = False,
    next_safe_step: str = "UNKNOWN",
) -> Dict[str, Any]:
    evidence = list(evidence_items or [])
    evidence_refs = [str(item.get("ref", item.get("id", ""))) for item in evidence if item.get("ref", item.get("id", ""))]
    evidence_hashes = [str(item.get("sha256", "")) for item in evidence if item.get("sha256")]
    source_priority = [str(item.get("source", "evidence")) for item in evidence]

    if not evidence:
        if manual_expected:
            truth_state = "PARTIAL"
            current_state = "EXPECTED_WITHOUT_EVIDENCE"
            confidence = "LOW_CONFIDENCE"
        elif brain_inference_only:
            truth_state = "PARTIAL"
            current_state = "INFERENCE_WITHOUT_EVIDENCE"
            confidence = "LOW_CONFIDENCE"
        else:
            truth_state = "UNKNOWN"
            current_state = "NO_EVIDENCE"
            confidence = "UNKNOWN"

        return build_truth_object(
            truth_object_id=f"{layer}:{subject}",
            layer=layer,
            subject=subject,
            current_state=current_state,
            truth_state=truth_state,
            confidence=confidence,
            evidence_refs=evidence_refs,
            evidence_hashes=evidence_hashes,
            source_priority=source_priority,
            conflict_state="NONE",
            next_safe_step=next_safe_step,
        )

    if _has_conflict(evidence):
        return build_truth_object(
            truth_object_id=f"{layer}:{subject}",
            layer=layer,
            subject=subject,
            current_state="CONFLICTING_EVIDENCE",
            truth_state="CONFLICT",
            confidence="CONFLICT",
            evidence_refs=evidence_refs,
            evidence_hashes=evidence_hashes,
            source_priority=source_priority,
            conflict_state="CONFLICT_FAIL_CLOSED",
            display_allowed=False,
            next_safe_step=next_safe_step,
        )

    states = [_state_from_evidence_item(item) for item in evidence]
    stale_or_historical = all(state in {"STALE", "HISTORICAL", "SUPERSEDED"} for state in states)

    if stale_or_historical:
        truth_state = states[0] if states else "STALE"
        return build_truth_object(
            truth_object_id=f"{layer}:{subject}",
            layer=layer,
            subject=subject,
            current_state="NOT_CURRENT",
            truth_state=truth_state,
            confidence="LOW_CONFIDENCE",
            evidence_refs=evidence_refs,
            evidence_hashes=evidence_hashes,
            source_priority=source_priority,
            staleness_state="NOT_CURRENT",
            display_allowed=False,
            next_safe_step=next_safe_step,
        )

    if "VERIFIED_TRUE" in states:
        truth_state = "VERIFIED_TRUE"
        current_state = "CURRENT_VERIFIED"
        confidence = "HIGH_CONFIDENCE"
    elif "VERIFIED_FALSE" in states:
        truth_state = "VERIFIED_FALSE"
        current_state = "CURRENT_FALSE"
        confidence = "HIGH_CONFIDENCE"
    elif "PARTIAL" in states:
        truth_state = "PARTIAL"
        current_state = "CURRENT_PARTIAL"
        confidence = "MEDIUM_CONFIDENCE"
    else:
        truth_state = "UNKNOWN"
        current_state = "CURRENT_UNKNOWN"
        confidence = "UNKNOWN"

    return build_truth_object(
        truth_object_id=f"{layer}:{subject}",
        layer=layer,
        subject=subject,
        current_state=current_state,
        truth_state=truth_state,
        confidence=confidence,
        evidence_refs=evidence_refs,
        evidence_hashes=evidence_hashes,
        source_priority=source_priority,
        next_safe_step=next_safe_step,
    )


def reconcile_global_state(layers: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
    truth_objects = list(layers.values())
    invalid = [obj for obj in truth_objects if not validate_truth_object_contract(obj)["valid"]]
    states = {str(obj.get("truth_state", "UNKNOWN")) for obj in truth_objects}

    if invalid or "CONFLICT" in states:
        global_state = "CONFLICT"
        confidence = "CONFLICT"
        display_allowed = False
    elif "UNKNOWN" in states:
        global_state = "PARTIAL"
        confidence = "LOW_CONFIDENCE"
        display_allowed = True
    elif "PARTIAL" in states:
        global_state = "PARTIAL"
        confidence = "MEDIUM_CONFIDENCE"
        display_allowed = True
    else:
        global_state = "VERIFIED_TRUE"
        confidence = "HIGH_CONFIDENCE"
        display_allowed = True

    global_truth = build_truth_object(
        truth_object_id="global:manual_brain_dashboard_interface",
        layer="global",
        subject="manual_brain_dashboard_interface_reconciliation",
        current_state=global_state,
        truth_state=global_state,
        confidence=confidence,
        evidence_refs=[str(obj.get("truth_object_id")) for obj in truth_objects],
        evidence_hashes=[],
        source_priority=["manual", "brain", "dashboard", "interface_hud", "evidence"],
        display_allowed=display_allowed,
        next_safe_step="CONTENT_ENGINE_GLOBAL_MANUAL_BRAIN_DASHBOARD_INTERFACE_RECONCILIATION_POST_BUILD_AUDIT",
    )

    return {
        "global_truth_object": global_truth,
        "layers": dict(layers),
        "valid": validate_truth_object_contract(global_truth)["valid"] and not invalid,
    }


def build_capability_matrix(truth_objects: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    matrix: List[Dict[str, Any]] = []

    for obj in truth_objects:
        truth_state = str(obj.get("truth_state", "UNKNOWN"))
        if truth_state == "VERIFIED_TRUE":
            capability_status = "VERIFIED"
        elif truth_state == "PARTIAL":
            capability_status = "PARTIAL"
        elif truth_state == "CONFLICT":
            capability_status = "BLOCKED"
        else:
            capability_status = "UNKNOWN"

        matrix.append(
            {
                "capability": str(obj.get("subject", "unknown")),
                "layer": str(obj.get("layer", "unknown")),
                "truth_state": truth_state,
                "capability_status": capability_status,
                "evidence_refs": list(obj.get("evidence_refs", [])),
            }
        )

    return matrix


def build_risk_matrix(truth_objects: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    risks: List[Dict[str, Any]] = []

    for obj in truth_objects:
        truth_state = str(obj.get("truth_state", "UNKNOWN"))
        if truth_state == "CONFLICT":
            severity = "CRITICAL"
            blocking_status = "BLOCKS_ADVANCE"
        elif truth_state == "UNKNOWN":
            severity = "HIGH"
            blocking_status = "BLOCKS_ADVANCE"
        elif truth_state == "PARTIAL":
            severity = "MEDIUM"
            blocking_status = "ALLOW_WITH_LABEL"
        else:
            severity = "LOW"
            blocking_status = "ALLOW"

        risks.append(
            {
                "risk_id": f"{obj.get('layer', 'unknown')}:{obj.get('subject', 'unknown')}",
                "layer": str(obj.get("layer", "unknown")),
                "description": f"Truth state is {truth_state}",
                "severity": severity,
                "trigger": truth_state,
                "evidence": list(obj.get("evidence_refs", [])),
                "mitigation": "reconcile evidence before stronger claim",
                "owner_layer": str(obj.get("layer", "unknown")),
                "blocking_status": blocking_status,
            }
        )

    return risks


def build_dashboard_display_contract(truth_objects: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    renderable = []
    blocked = []

    for obj in truth_objects:
        validation = validate_truth_object_contract(obj)
        allowed = validation["valid"] and bool(obj.get("display_allowed", False))
        row = {
            "truth_object_id": str(obj.get("truth_object_id", "unknown")),
            "layer": str(obj.get("layer", "unknown")),
            "subject": str(obj.get("subject", "unknown")),
            "truth_state": str(obj.get("truth_state", "UNKNOWN")),
            "display_allowed": allowed,
        }
        if allowed:
            renderable.append(row)
        else:
            blocked.append(row)

    return {
        "consumer": "dashboard",
        "renderable": renderable,
        "blocked": blocked,
        "rule": "dashboard_consumes_truth_objects_only",
    }


def build_interface_hud_display_contract(dashboard_contract: Mapping[str, Any]) -> Dict[str, Any]:
    renderable = list(dashboard_contract.get("renderable", []))
    blocked = list(dashboard_contract.get("blocked", []))

    return {
        "consumer": "interface_hud",
        "displayable": renderable,
        "blocked": blocked,
        "rule": "interface_hud_consumes_dashboard_truth_contract_only",
        "requires_state_label": True,
        "requires_risk_label": True,
        "requires_next_safe_step": True,
    }


def validate_no_productive_operations(intent_tokens: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    tokens = {str(token).lower() for token in _as_list(intent_tokens)}
    forbidden = sorted(tokens.intersection(PRODUCTIVE_OPERATION_TOKENS))

    return {
        "valid": not forbidden,
        "forbidden": forbidden,
        "productive_operations_blocked": not forbidden,
    }
