from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional


PHASE_PERMISSION_MATRIX: Dict[str, Dict[str, bool]] = {
    "BLUEPRINT": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "REVIEW_HARDENING": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "FINAL_APPROVAL_REVIEW": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "IMPLEMENTATION_PLAN": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "AUTOMATIC_BLOCK_BUILD": {"source_write": True, "test_write": True, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "POST_BUILD_AUDIT": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "GATE_CLOSE_VALIDATION": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
    "READINESS_MAP": {"source_write": False, "test_write": False, "runtime": False, "queue_write": False, "publishing": False, "automation": False, "manual_mutation": False},
}

REQUIRED_CLOSED_EVIDENCE = ("seal", "manifest", "report")


@dataclass(frozen=True)
class EvidenceScore:
    score: int
    status: str
    reasons: List[str]


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().strip('"')


def calculate_confidence(evidence: Mapping[str, Any]) -> EvidenceScore:
    score = 0
    reasons: List[str] = []

    if bool(evidence.get("seal")):
        score += 35
        reasons.append("seal_present")

    if bool(evidence.get("manifest")):
        score += 25
        reasons.append("manifest_present")

    if bool(evidence.get("report")):
        score += 20
        reasons.append("report_present")

    if evidence.get("conflict") is True:
        reasons.append("conflict_present")
        return EvidenceScore(score=min(score, 69), status="CONFLICT", reasons=reasons)

    score += 10
    reasons.append("no_conflict")

    if evidence.get("repo_stable") is True:
        score += 10
        reasons.append("repo_stable")

    if score >= 90:
        status = "VALIDATED_TRUE"
    elif score >= 70:
        status = "MEDIUM_CONFIDENCE"
    elif score > 0:
        status = "LOW_CONFIDENCE"
    else:
        status = "UNKNOWN"

    return EvidenceScore(score=score, status=status, reasons=reasons)


def closed_component_truth(component: str, evidence: Mapping[str, Any]) -> Dict[str, Any]:
    score = calculate_confidence(evidence)
    missing = [name for name in REQUIRED_CLOSED_EVIDENCE if not evidence.get(name)]

    return {
        "component": component,
        "truth_state": score.status,
        "confidence_score": score.score,
        "confidence_status": score.status,
        "confidence_reasons": list(score.reasons),
        "missing_required_evidence": missing,
        "validated_closed": score.status == "VALIDATED_TRUE" and not missing,
    }


def classify_phase_action(
    phase: str,
    source_files_written: bool = False,
    test_files_written: bool = False,
    runtime_performed: bool = False,
    queue_write_performed: bool = False,
    publishing_performed: bool = False,
    automation_performed: bool = False,
    manual_mutation_performed: bool = False,
    allowlisted_scope: bool = False,
) -> Dict[str, Any]:
    permissions = PHASE_PERMISSION_MATRIX.get(phase)

    if permissions is None:
        return {"phase": phase, "classification": "UNKNOWN_PHASE", "allowed": False, "reasons": ["phase_not_registered"]}

    requested = {
        "source_write": source_files_written,
        "test_write": test_files_written,
        "runtime": runtime_performed,
        "queue_write": queue_write_performed,
        "publishing": publishing_performed,
        "automation": automation_performed,
        "manual_mutation": manual_mutation_performed,
    }

    violations: List[str] = []
    expected_with_conditions: List[str] = []

    for key, was_requested in requested.items():
        if not was_requested:
            continue

        if permissions.get(key) is True:
            if key in {"source_write", "test_write"} and phase == "AUTOMATIC_BLOCK_BUILD":
                if allowlisted_scope:
                    expected_with_conditions.append(key)
                else:
                    violations.append(key + "_without_allowlist")
            else:
                expected_with_conditions.append(key)
        else:
            violations.append(key)

    if violations:
        classification = "POLICY_VIOLATION"
        allowed = False
    elif expected_with_conditions:
        classification = "EXPECTED_WITH_CONDITIONS"
        allowed = True
    else:
        classification = "VALID_ALLOWED_ACTION"
        allowed = True

    return {"phase": phase, "classification": classification, "allowed": allowed, "violations": violations, "expected_with_conditions": expected_with_conditions}


def sync_lock_state(
    head: Optional[str],
    upstream: Optional[str],
    dirty_paths: Iterable[str],
    manual_hash: Optional[str] = None,
    evidence_hash: Optional[str] = None,
) -> Dict[str, Any]:
    dirty = [normalize_path(path) for path in dirty_paths if normalize_path(path)]

    if dirty:
        status = "BLOCKED_SYNC"
    elif not head or not upstream:
        status = "UNTRUSTED_SYNC"
    elif head != upstream:
        status = "STALE_SYNC"
    elif manual_hash and evidence_hash and manual_hash != evidence_hash:
        status = "CONFLICT_SYNC"
    else:
        status = "VALIDATED_SYNC"

    return {"sync_status": status, "head": head, "upstream": upstream, "dirty_count": len(dirty), "dirty_paths": dirty}


def phase_permission_matrix() -> Dict[str, Dict[str, bool]]:
    return {phase: dict(values) for phase, values in PHASE_PERMISSION_MATRIX.items()}


def build_decision_advisor(record: Mapping[str, Any]) -> Dict[str, Any]:
    confidence_status = record.get("confidence_status") or record.get("truth_state")
    sync_status = record.get("sync_status", "UNKNOWN")

    if confidence_status == "VALIDATED_TRUE" and sync_status == "VALIDATED_SYNC":
        decision = "ALLOW_NEXT_GOVERNED_STEP"
    elif sync_status in {"BLOCKED_SYNC", "CONFLICT_SYNC", "UNTRUSTED_SYNC"}:
        decision = "DO_NOT_ADVANCE_SYNC_BLOCKED"
    elif confidence_status in {"CONFLICT", "UNKNOWN", "LOW_CONFIDENCE"}:
        decision = "DO_NOT_ADVANCE_EVIDENCE_INSUFFICIENT"
    else:
        decision = "REVIEW_BEFORE_ADVANCE"

    return {"decision": decision, "confidence_status": confidence_status, "sync_status": sync_status}


def build_operational_truth_record(
    component: str,
    evidence: Mapping[str, Any],
    head: Optional[str],
    upstream: Optional[str],
    dirty_paths: Iterable[str],
) -> Dict[str, Any]:
    truth = closed_component_truth(component, evidence)
    sync = sync_lock_state(head=head, upstream=upstream, dirty_paths=dirty_paths)

    record: Dict[str, Any] = {}
    record.update(truth)
    record.update(sync)
    record["decision_advisor"] = build_decision_advisor(record)

    return record


__all__ = [
    "PHASE_PERMISSION_MATRIX",
    "EvidenceScore",
    "normalize_path",
    "calculate_confidence",
    "closed_component_truth",
    "classify_phase_action",
    "sync_lock_state",
    "phase_permission_matrix",
    "build_decision_advisor",
    "build_operational_truth_record",
]
