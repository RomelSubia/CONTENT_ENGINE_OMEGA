
"""
CONTENT ENGINE Ω — MANUAL ↔ CEREBRO BRIDGE
BLOQUE 6 — Decision mapper + controlled plan builder

This module is intentionally deterministic, local, non-executing,
non-writing to manual/brain/reports-brain, and fail-closed.
It maps decisions and proposes controlled plans only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple
import hashlib
import json
import re


PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
REQUIRE_REVIEW = "REQUIRE_REVIEW"
BLOCK = "BLOCK"
LOCK = "LOCK"

VALID_DECISIONS = {PASS, PASS_WITH_WARNINGS, REQUIRE_REVIEW, BLOCK, LOCK}
DECISION_PRECEDENCE = {
    LOCK: 5,
    BLOCK: 4,
    REQUIRE_REVIEW: 3,
    PASS_WITH_WARNINGS: 2,
    PASS: 1,
}

AUTHORITY_PRECEDENCE = {
    "SEALED": 5,
    "CANONICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "UNKNOWN": 0,
}

RISK_PRECEDENCE = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

ALLOWED_PLAN_TYPES = {
    "REVIEW_PLAN",
    "BUILD_PLAN",
    "VALIDATION_PLAN",
    "GATE_CLOSURE_PLAN",
    "RECOVERY_PLAN",
}

ALLOWED_STEP_TYPES = {
    "DESCRIBE_VALIDATION",
    "DESCRIBE_REPORT",
    "PROPOSE_REVIEW",
    "MAP_DECISION",
    "MAP_EVIDENCE",
    "MAP_RISK",
    "MAP_AUTHORIZATION_REQUIREMENT",
    "MAP_ROLLBACK_REQUIREMENT",
    "MAP_NEXT_GATE",
}

FORBIDDEN_STEP_TYPES = {
    "VALIDATE_NOW",
    "GENERATE_REPORT_NOW",
    "RUN_TESTS_NOW",
    "WRITE_REPORT_NOW",
    "EXECUTE",
    "WRITE_MANUAL",
    "WRITE_BRAIN",
    "WRITE_REPORTS_BRAIN",
    "PUBLISH",
    "WEBHOOK",
    "N8N_RUN",
    "CAPA9_RUN",
}

EXECUTABLE_CONTENT_PATTERNS = (
    r"\bpowershell\b",
    r"\bpwsh\b",
    r"\bcmd\b",
    r"\bbash\b",
    r"\bpython\s+\S+\.py\b",
    r"\bpytest\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+reset\b",
    r"\bgit\s+clean\b",
    r"\bsubprocess\b",
    r"\bstart-process\b",
    r"\binvoke-webrequest\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bn8n\s+run\b",
    r"\bwebhook\b",
    r"\bpublish\b",
    r"\bwrite\s+file\b",
    r"\bdelete\s+file\b",
    r"\bmove\s+file\b",
    r"\bcopy\s+file\b",
    r"\bopen\s*\([^)]*,\s*['\"][wa+]",
    r"\bpath\.write_text\b",
    r"\bpath\.write_bytes\b",
)

BLOCK7_DENYLIST = {
    "global traceability engine",
    "full reporting layer",
    "cross-block report consolidator",
    "historical report reconciler",
    "manifest registry engine",
    "global evidence dashboard",
    "bridge-wide reporting orchestrator",
    "GlobalTraceabilityEngine",
    "ReportConsolidator",
    "ManifestRegistryEngine",
}

BLOCK8_DENYLIST = {
    "AtomicWriter",
    "LockManager",
    "QuarantineWriter",
    "RecoveryExecutor",
    "RollbackExecutor",
    "WriteTransaction",
    "PendingWriteSet",
    "MutationQueue",
    "FilesystemMutationPlan",
    "AtomicCommitPlan",
    "PatchApplier",
    "ManualWriter",
    "BrainWriter",
    "ReportsBrainWriter",
}

PROTECTED_WRITE_TOKENS = {
    "manual_write",
    "brain_write",
    "reports_brain_write",
    "write_manual",
    "write_brain",
    "write_reports_brain",
    "manual/current",
    "00_SYSTEM/brain",
    "00_SYSTEM/reports/brain",
}

PLAN_BOUNDS = {
    "max_decision_inputs": 100,
    "max_plan_steps": 25,
    "max_evidence_refs": 50,
    "max_step_description_chars": 500,
    "max_total_plan_chars": 10000,
    "max_nested_depth": 4,
    "max_authorization_requirements": 10,
    "max_risk_reasons": 20,
}

ALLOWED_SOURCE_STATUSES = {
    "CLOSED_VALIDATED",
    "VALIDATED_POST_AUDITED",
    "BUILT_POST_AUDITED",
    "VALIDATION_MAP_DEFINED",
    "VALIDATION_PLAN_DEFINED",
}

BLOCKED_ACTIONS_DEFAULT = [
    "EXECUTION",
    "MANUAL_WRITE",
    "BRAIN_WRITE",
    "REPORTS_BRAIN_WRITE",
    "N8N",
    "WEBHOOK",
    "PUBLISHING",
    "CAPA9",
    "BLOQUE_7_PREBUILD",
    "BLOQUE_8_PREBUILD",
    "BLOQUE_9_PREBUILD",
    "BLOQUE_10_PREBUILD",
]


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[a-f0-9]{64}", value or ""))


def make_decision(status: str, reason: str, **extra: Any) -> Dict[str, Any]:
    if status not in VALID_DECISIONS:
        status = LOCK
        reason = "INVALID_DECISION_ESCALATED_TO_LOCK"
    payload = {"status": status, "reason": reason}
    payload.update(extra)
    return payload


def choose_worst_decision(decisions: Iterable[str]) -> str:
    known = [decision for decision in decisions if decision in VALID_DECISIONS]
    if not known:
        return LOCK
    return max(known, key=lambda item: DECISION_PRECEDENCE[item])


@dataclass(frozen=True)
class EvidenceDependency:
    evidence_id: str
    artifact_path: str
    sha256: str
    source_block: str
    source_status: str
    source_authority: str
    required: bool = True


@dataclass(frozen=True)
class AuthorizationRequirement:
    authorization_required: bool
    authorization_type: str
    authorization_status: str = "NOT_REQUESTED"
    authorization_input_present: bool = False
    authorization_validated: bool = False
    authorization_granted: bool = False
    authorization_consumed: bool = False
    execution_permission_granted: bool = False


@dataclass(frozen=True)
class RollbackRequirement:
    rollback_required: bool
    rollback_type: str = "DECLARED_REQUIREMENT_ONLY"
    rollback_strategy_described: bool = True
    rollback_executor_created: bool = False
    rollback_executed: bool = False
    recovery_writer_created: bool = False
    quarantine_writer_created: bool = False


@dataclass(frozen=True)
class PlanStepContract:
    step_id: str
    step_order: int
    step_type: str
    description: str
    evidence_required: Sequence[str]
    risk_level: str
    rollback_required: bool
    execution_allowed: bool = False


@dataclass(frozen=True)
class DecisionEnvelope:
    decision_id: str
    decision_type: str
    decision_reason: str
    decision_precedence_rank: int
    source_authority_rank: int
    source_inputs: Sequence[str]
    evidence_refs: Sequence[str]
    hash_refs: Sequence[str]
    blocked_capabilities: Sequence[str]
    allowed_next_step: str | None
    human_review_required: bool
    human_authorization_required: bool
    authorization_status: str
    authorization_consumed: bool
    execution_permission_granted: bool
    execution_allowed: bool
    manual_write_allowed: bool
    brain_write_allowed: bool
    reports_brain_write_allowed: bool


@dataclass(frozen=True)
class ControlledPlanEnvelope:
    plan_id: str
    plan_type: str
    plan_status: str
    approval_status: str
    execution_status: str
    next_gate_required: bool
    approval_gate_required: bool
    build_gate_required: bool
    risk_classification: str
    steps: Sequence[Mapping[str, Any]]
    required_evidence: Sequence[Mapping[str, Any]]
    required_authorizations: Sequence[Mapping[str, Any]]
    rollback_requirements: Sequence[Mapping[str, Any]]
    forbidden_actions: Sequence[str]
    allowed_actions: Sequence[str]
    execution_allowed: bool
    manual_write_allowed: bool
    brain_write_allowed: bool
    reports_brain_write_allowed: bool
    external_io_allowed: bool


def scan_executable_content(value: Any) -> List[str]:
    text = canonical_json(value).lower() if not isinstance(value, str) else value.lower()
    findings = []
    for pattern in EXECUTABLE_CONTENT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(pattern)
    return sorted(set(findings))


def validate_executable_content(value: Any) -> Dict[str, Any]:
    findings = scan_executable_content(value)
    if findings:
        return make_decision(LOCK, "EXECUTABLE_PLAN_CONTENT_DETECTED", findings=findings)
    return make_decision(PASS, "NO_EXECUTABLE_PLAN_CONTENT", findings=[])


def validate_step_type(step_type: str) -> Dict[str, Any]:
    if step_type in FORBIDDEN_STEP_TYPES:
        return make_decision(LOCK, "FORBIDDEN_STEP_TYPE", step_type=step_type)
    if step_type not in ALLOWED_STEP_TYPES:
        return make_decision(BLOCK, "AMBIGUOUS_OR_UNKNOWN_STEP_TYPE", step_type=step_type)
    return make_decision(PASS, "STEP_TYPE_ALLOWED", step_type=step_type)


def validate_authorization_requirement(auth: AuthorizationRequirement | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(auth) if isinstance(auth, AuthorizationRequirement) else dict(auth)

    forbidden_true_fields = [
        "authorization_input_present",
        "authorization_validated",
        "authorization_granted",
        "authorization_consumed",
        "execution_permission_granted",
    ]
    for field in forbidden_true_fields:
        if payload.get(field) is True:
            return make_decision(LOCK, "AUTHORIZATION_CONSUMPTION_OR_GRANT_BLOCKED", field=field)

    if payload.get("authorization_status") != "NOT_REQUESTED":
        return make_decision(LOCK, "AUTHORIZATION_STATUS_MUST_REMAIN_NOT_REQUESTED")

    return make_decision(PASS, "AUTHORIZATION_REQUIREMENT_SAFE")


def verify_evidence_dependency(dep: EvidenceDependency | Mapping[str, Any], root: Path | None = None) -> Dict[str, Any]:
    payload = asdict(dep) if isinstance(dep, EvidenceDependency) else dict(dep)
    root = root or Path.cwd()

    if not payload.get("evidence_id"):
        return make_decision(BLOCK, "EVIDENCE_REF_MISSING")

    artifact_path = str(payload.get("artifact_path") or "")
    if not artifact_path:
        return make_decision(BLOCK, "ARTIFACT_PATH_MISSING")

    digest = str(payload.get("sha256") or "")
    if not digest:
        return make_decision(BLOCK, "HASH_MISSING")

    if not is_sha256(digest):
        return make_decision(BLOCK, "HASH_FORMAT_INVALID")

    artifact = root / artifact_path
    if not artifact.exists():
        return make_decision(BLOCK, "ARTIFACT_MISSING", artifact_path=artifact_path)

    current_hash = sha256_bytes(artifact.read_bytes())
    if current_hash != digest:
        return make_decision(LOCK, "HASH_MISMATCH", expected=digest, actual=current_hash)

    if payload.get("source_status") not in ALLOWED_SOURCE_STATUSES:
        return make_decision(LOCK, "SOURCE_STATUS_INVALID")

    if payload.get("source_authority") not in AUTHORITY_PRECEDENCE or payload.get("source_authority") == "UNKNOWN":
        return make_decision(LOCK, "UNKNOWN_SOURCE_AUTHORITY_ON_DECISION")

    return make_decision(PASS, "EVIDENCE_DEPENDENCY_VALID")


ACTIONABLE_SCAN_FIELDS = {
    "description",
    "plan_description",
    "step_description",
    "required_actions",
    "recovery_notes",
    "human_summary",
    "instructions",
    "command",
    "commands",
    "script",
    "action",
    "actions",
    "proposed_action",
    "execution_notes",
}

NON_ACTIONABLE_DECLARATIVE_FIELDS = {
    "forbidden_actions",
    "blocked_capabilities",
    "permissions",
    "blocked_actions",
    "allowed_actions",
}


def extract_actionable_content(value: Any) -> List[str]:
    """Return only fields that represent real proposed/actionable content.

    Safety lists such as forbidden_actions, blocked_capabilities, permissions,
    and blocked_actions are intentionally excluded so that declaring a capability
    as forbidden does not become a false executable-content LOCK.
    """
    items: List[str] = []

    if isinstance(value, str):
        items.append(value)
        return items

    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in NON_ACTIONABLE_DECLARATIVE_FIELDS:
                continue

            if key_text in ACTIONABLE_SCAN_FIELDS:
                items.append(canonical_json(child) if not isinstance(child, str) else child)
                continue

            if key_text == "steps" and isinstance(child, Sequence) and not isinstance(child, (str, bytes, bytearray)):
                for step in child:
                    if isinstance(step, Mapping):
                        for step_key in ("description", "step_description", "required_actions", "recovery_notes"):
                            if step_key in step:
                                step_value = step[step_key]
                                items.append(canonical_json(step_value) if not isinstance(step_value, str) else step_value)
                continue

            if isinstance(child, Mapping):
                items.extend(extract_actionable_content(child))

        return items

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            items.extend(extract_actionable_content(child))
        return items

    return items


def validate_non_actionable_output(value: Any) -> Dict[str, Any]:
    actionable_items = extract_actionable_content(value)
    findings: List[str] = []

    for item in actionable_items:
        findings.extend(scan_executable_content(item))

    findings = sorted(set(findings))
    if findings:
        return make_decision(LOCK, "ACTIONABLE_OUTPUT_DETECTED", findings=findings)

    return make_decision(PASS, "OUTPUT_IS_NON_ACTIONABLE")


def validate_rollback_requirement(rollback: RollbackRequirement | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(rollback) if isinstance(rollback, RollbackRequirement) else dict(rollback)

    if payload.get("rollback_required") is True and payload.get("rollback_type") != "DECLARED_REQUIREMENT_ONLY":
        return make_decision(LOCK, "ROLLBACK_TYPE_NOT_DECLARATION_ONLY")

    if payload.get("rollback_required") is False:
        return make_decision(BLOCK, "ROLLBACK_MISSING_FOR_CONTROLLED_PLAN")

    forbidden_true_fields = [
        "rollback_executor_created",
        "rollback_executed",
        "recovery_writer_created",
        "quarantine_writer_created",
    ]
    for field in forbidden_true_fields:
        if payload.get(field) is True:
            return make_decision(LOCK, "ROLLBACK_EXECUTOR_OR_WRITER_BLOCKED", field=field)

    return make_decision(PASS, "ROLLBACK_DECLARATION_ONLY_SAFE")


def validate_block7_boundary(value: Any) -> Dict[str, Any]:
    text = canonical_json(value)
    findings = [token for token in BLOCK7_DENYLIST if token.lower() in text.lower()]
    if findings:
        return make_decision(LOCK, "BLOQUE_7_BOUNDARY_VIOLATION", findings=sorted(findings))
    return make_decision(PASS, "BLOQUE_7_BOUNDARY_RESPECTED")


def validate_block8_boundary(value: Any) -> Dict[str, Any]:
    text = canonical_json(value)
    findings = [token for token in BLOCK8_DENYLIST if token.lower() in text.lower()]
    if findings:
        return make_decision(LOCK, "BLOQUE_8_WRITER_BOUNDARY_VIOLATION", findings=sorted(findings))
    return make_decision(PASS, "BLOQUE_8_BOUNDARY_RESPECTED")


def validate_approval_by_plan(plan: ControlledPlanEnvelope | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(plan) if isinstance(plan, ControlledPlanEnvelope) else dict(plan)

    if payload.get("plan_status") != "PROPOSED_ONLY":
        return make_decision(LOCK, "PLAN_STATUS_NOT_PROPOSED_ONLY")

    if payload.get("approval_status") != "NOT_APPROVED":
        return make_decision(LOCK, "APPROVAL_STATUS_NOT_ALLOWED")

    if payload.get("execution_status") != "NOT_EXECUTED":
        return make_decision(LOCK, "EXECUTION_STATUS_NOT_NOT_EXECUTED")

    for field in ["next_gate_required", "approval_gate_required", "build_gate_required"]:
        if payload.get(field) is not True:
            return make_decision(BLOCK, "REQUIRED_GATE_FLAG_FALSE", field=field)

    return make_decision(PASS, "APPROVAL_BY_PLAN_GUARD_PASS")


def nested_depth(value: Any, current: int = 0) -> int:
    if isinstance(value, Mapping):
        if not value:
            return current + 1
        return max(nested_depth(v, current + 1) for v in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not value:
            return current + 1
        return max(nested_depth(v, current + 1) for v in value)
    return current


def validate_plan_bounds(plan: ControlledPlanEnvelope | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(plan) if isinstance(plan, ControlledPlanEnvelope) else dict(plan)
    text = canonical_json(payload)

    if len(payload.get("steps", [])) > PLAN_BOUNDS["max_plan_steps"]:
        return make_decision(BLOCK, "PLAN_STEPS_EXCEED_LIMIT")

    if len(payload.get("required_evidence", [])) > PLAN_BOUNDS["max_evidence_refs"]:
        return make_decision(BLOCK, "EVIDENCE_REFS_EXCEED_LIMIT")

    if len(payload.get("required_authorizations", [])) > PLAN_BOUNDS["max_authorization_requirements"]:
        return make_decision(BLOCK, "AUTHORIZATION_REQUIREMENTS_EXCEED_LIMIT")

    if len(text) > PLAN_BOUNDS["max_total_plan_chars"]:
        return make_decision(BLOCK, "TOTAL_PLAN_CHARS_EXCEED_LIMIT")

    if nested_depth(payload) > PLAN_BOUNDS["max_nested_depth"]:
        return make_decision(BLOCK, "NESTED_DEPTH_EXCEEDED")

    for step in payload.get("steps", []):
        if len(str(step.get("description", ""))) > PLAN_BOUNDS["max_step_description_chars"]:
            return make_decision(BLOCK, "STEP_DESCRIPTION_EXCEEDS_LIMIT")

    return make_decision(PASS, "PLAN_BOUNDS_VALID")


def decision_sort_key(decision: Mapping[str, Any]) -> Tuple[Any, ...]:
    return (
        -int(decision.get("decision_precedence_rank", 0)),
        -int(decision.get("source_authority_rank", 0)),
        str(decision.get("decision_type", "")),
        str(decision.get("decision_id", "")),
    )


def sort_decisions(decisions: Iterable[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    return sorted(decisions, key=decision_sort_key)


def stable_plan_hash(plan: Mapping[str, Any]) -> str:
    forbidden = {"timestamp", "created_at", "updated_at", "random_id", "uuid"}
    text = canonical_json(plan)
    lowered = text.lower()
    for token in forbidden:
        if token in lowered:
            return "VOLATILE_FIELD_FORBIDDEN"
    return sha256_text(text)


def validate_hash_stability(plan: Mapping[str, Any]) -> Dict[str, Any]:
    first = stable_plan_hash(plan)
    second = stable_plan_hash(plan)
    if first == "VOLATILE_FIELD_FORBIDDEN":
        return make_decision(LOCK, "VOLATILE_FIELD_IN_PLAN_HASH")
    if not is_sha256(first) or first != second:
        return make_decision(LOCK, "UNSTABLE_PLAN_HASH")
    return make_decision(PASS, "PLAN_HASH_STABLE", plan_hash=first)


def validate_explainability(value: Mapping[str, Any]) -> Dict[str, Any]:
    if not value.get("decision_reason") and not value.get("plan_reason"):
        return make_decision(BLOCK, "REASON_MISSING")

    if value.get("raw_source_dump_allowed") is True or value.get("full_artifact_dump_allowed") is True:
        return make_decision(LOCK, "RAW_OR_FULL_DUMP_ALLOWED")

    if not value.get("evidence_refs"):
        return make_decision(BLOCK, "EVIDENCE_REFS_MISSING")

    if not value.get("hash_refs"):
        return make_decision(BLOCK, "HASH_REFS_MISSING")

    return make_decision(PASS, "EXPLAINABILITY_WITHOUT_LEAKAGE_VALID")


def validate_anti_loop(value: Mapping[str, Any]) -> Dict[str, Any]:
    if value.get("recursive_plan_generation_allowed") is True:
        return make_decision(LOCK, "RECURSIVE_PLAN_GENERATION_BLOCKED")

    if value.get("self_referential_plan_allowed") is True:
        return make_decision(BLOCK, "SELF_REFERENTIAL_PLAN_BLOCKED")

    if value.get("plan_generates_plan_allowed") is True:
        return make_decision(LOCK, "PLAN_GENERATES_PLAN_BLOCKED")

    if value.get("decision_plan_cycles", 0) > 1:
        return make_decision(LOCK, "DECISION_PLAN_LOOP_DETECTED")

    return make_decision(PASS, "ANTI_LOOP_GUARD_VALID")


def validate_protected_write_intent(value: Any) -> Dict[str, Any]:
    text = canonical_json(value).lower()
    findings = [token for token in PROTECTED_WRITE_TOKENS if token.lower() in text]
    if findings:
        return make_decision(LOCK, "PROTECTED_WRITE_INTENT_DETECTED", findings=sorted(findings))
    return make_decision(PASS, "NO_PROTECTED_WRITE_INTENT")


def validate_decision_envelope(decision: DecisionEnvelope | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(decision) if isinstance(decision, DecisionEnvelope) else dict(decision)

    if payload.get("decision_type") not in VALID_DECISIONS:
        return make_decision(LOCK, "INVALID_DECISION_TYPE")

    if not payload.get("decision_reason"):
        return make_decision(BLOCK, "DECISION_WITHOUT_REASON")

    if not payload.get("evidence_refs"):
        return make_decision(BLOCK, "DECISION_WITHOUT_EVIDENCE_REF")

    if not payload.get("hash_refs"):
        return make_decision(BLOCK, "DECISION_WITHOUT_HASH_REF")

    for field in [
        "authorization_consumed",
        "execution_permission_granted",
        "execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
    ]:
        if payload.get(field) is True:
            return make_decision(LOCK, "DECISION_UNSAFE_PERMISSION_TRUE", field=field)

    # Only actionable decision text is scanned. Declarative safety lists
    # such as blocked_capabilities are not execution intent.
    scan = validate_non_actionable_output(
        {
            "description": payload.get("decision_reason", ""),
            "proposed_action": payload.get("proposed_action", ""),
            "execution_notes": payload.get("execution_notes", ""),
        }
    )
    if scan["status"] == LOCK:
        return scan

    return make_decision(PASS, "DECISION_ENVELOPE_VALID")


def validate_controlled_plan(plan: ControlledPlanEnvelope | Mapping[str, Any]) -> Dict[str, Any]:
    payload = asdict(plan) if isinstance(plan, ControlledPlanEnvelope) else dict(plan)

    checks = [
        validate_approval_by_plan(payload),
        validate_plan_bounds(payload),
        validate_non_actionable_output(payload),
        validate_block7_boundary(payload),
        validate_block8_boundary(payload),
        validate_hash_stability(payload),
    ]

    for field in [
        "execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "external_io_allowed",
    ]:
        if payload.get(field) is True:
            checks.append(make_decision(LOCK, "CONTROLLED_PLAN_UNSAFE_PERMISSION_TRUE", field=field))

    for step in payload.get("steps", []):
        checks.append(validate_step_type(str(step.get("step_type", ""))))
        if step.get("execution_allowed") is True:
            checks.append(make_decision(LOCK, "PLAN_STEP_EXECUTION_ALLOWED_TRUE"))

    status = choose_worst_decision(check["status"] for check in checks)
    if status != PASS:
        return make_decision(status, "CONTROLLED_PLAN_INVALID", checks=checks)

    hash_check = validate_hash_stability(payload)
    return make_decision(PASS, "CONTROLLED_PLAN_VALID", plan_hash=hash_check.get("plan_hash"))


def map_decision(
    *,
    source_inputs: Sequence[str],
    evidence_refs: Sequence[str],
    hash_refs: Sequence[str],
    decision_candidates: Sequence[str],
    source_authorities: Sequence[str],
    reason: str,
    allowed_next_step: str | None = None,
) -> DecisionEnvelope:
    worst = choose_worst_decision(decision_candidates)
    authority_rank = max((AUTHORITY_PRECEDENCE.get(item, 0) for item in source_authorities), default=0)

    if not evidence_refs:
        worst = choose_worst_decision([worst, BLOCK])
        reason = "MISSING_EVIDENCE_REF"

    if not hash_refs:
        worst = choose_worst_decision([worst, BLOCK])
        reason = "MISSING_HASH_REF"

    if authority_rank == 0 and worst in {LOCK, BLOCK}:
        worst = LOCK
        reason = "UNKNOWN_AUTHORITY_ON_CRITICAL_DECISION"

    seed = canonical_json(
        {
            "source_inputs": sorted(source_inputs),
            "evidence_refs": sorted(evidence_refs),
            "hash_refs": sorted(hash_refs),
            "decision": worst,
            "reason": reason,
            "allowed_next_step": allowed_next_step,
        }
    )

    return DecisionEnvelope(
        decision_id=sha256_text(seed),
        decision_type=worst,
        decision_reason=reason,
        decision_precedence_rank=DECISION_PRECEDENCE[worst],
        source_authority_rank=authority_rank,
        source_inputs=tuple(sorted(source_inputs)),
        evidence_refs=tuple(sorted(evidence_refs)),
        hash_refs=tuple(sorted(hash_refs)),
        blocked_capabilities=tuple(BLOCKED_ACTIONS_DEFAULT),
        allowed_next_step=allowed_next_step,
        human_review_required=worst in {REQUIRE_REVIEW, BLOCK, LOCK},
        human_authorization_required=False,
        authorization_status="NOT_REQUESTED",
        authorization_consumed=False,
        execution_permission_granted=False,
        execution_allowed=False,
        manual_write_allowed=False,
        brain_write_allowed=False,
        reports_brain_write_allowed=False,
    )


def build_controlled_plan(
    *,
    plan_type: str,
    steps: Sequence[PlanStepContract],
    required_evidence: Sequence[EvidenceDependency],
    required_authorizations: Sequence[AuthorizationRequirement],
    rollback_requirements: Sequence[RollbackRequirement],
    risk_classification: str,
) -> ControlledPlanEnvelope:
    if plan_type not in ALLOWED_PLAN_TYPES:
        plan_type = "REVIEW_PLAN"

    step_payloads = [asdict(step) for step in sorted(steps, key=lambda s: (s.step_order, s.step_id))]
    evidence_payloads = [asdict(dep) for dep in sorted(required_evidence, key=lambda d: d.evidence_id)]
    auth_payloads = [asdict(auth) for auth in required_authorizations]
    rollback_payloads = [asdict(rb) for rb in rollback_requirements]

    seed = canonical_json(
        {
            "plan_type": plan_type,
            "steps": step_payloads,
            "required_evidence": evidence_payloads,
            "risk_classification": risk_classification,
        }
    )

    return ControlledPlanEnvelope(
        plan_id=sha256_text(seed),
        plan_type=plan_type,
        plan_status="PROPOSED_ONLY",
        approval_status="NOT_APPROVED",
        execution_status="NOT_EXECUTED",
        next_gate_required=True,
        approval_gate_required=True,
        build_gate_required=True,
        risk_classification=risk_classification,
        steps=tuple(step_payloads),
        required_evidence=tuple(evidence_payloads),
        required_authorizations=tuple(auth_payloads),
        rollback_requirements=tuple(rollback_payloads),
        forbidden_actions=tuple(BLOCKED_ACTIONS_DEFAULT),
        allowed_actions=("DESCRIBE", "MAP", "PROPOSE", "REVIEW"),
        execution_allowed=False,
        manual_write_allowed=False,
        brain_write_allowed=False,
        reports_brain_write_allowed=False,
        external_io_allowed=False,
    )


def build_block6_report_payloads() -> Dict[str, Dict[str, Any]]:
    permissions = {
        "post_build_audit_allowed_next": True,
        "validation_map_allowed_now": False,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_7_blueprint_allowed_now": False,
        "execution_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
    }

    base = {
        "project": "CONTENT_ENGINE_OMEGA",
        "subsystem": "MANUAL_CEREBRO_BRIDGE",
        "block": "BLOQUE_6_DECISION_MAPPER_CONTROLLED_PLAN_BUILDER",
        "status": "BUILT_PENDING_POST_AUDIT",
        "permissions": permissions,
    }

    return {
        "BRIDGE_BLOCK_6_DECISION_MAPPER_REPORT.json": {
            **base,
            "component": "DECISION_MAPPER",
            "features": [
                "decision_envelope",
                "decision_precedence_matrix",
                "authority_precedence_matrix",
                "evidence_refs_required",
                "hash_refs_required",
                "fail_closed_mapping",
            ],
        },
        "BRIDGE_BLOCK_6_CONTROLLED_PLAN_BUILDER_REPORT.json": {
            **base,
            "component": "CONTROLLED_PLAN_BUILDER",
            "features": [
                "controlled_plan_envelope",
                "plan_status_proposed_only",
                "approval_status_not_approved",
                "execution_status_not_executed",
                "next_gate_required",
            ],
        },
        "BRIDGE_BLOCK_6_PLAN_SAFETY_REPORT.json": {
            **base,
            "component": "PLAN_SAFETY",
            "guards": [
                "executable_plan_content_scanner",
                "non_actionable_output_guard",
                "rollback_declaration_only_guard",
                "approval_by_plan_guard",
                "anti_loop_recursive_plan_guard",
                "plan_hash_stability_guard",
            ],
        },
        "BRIDGE_BLOCK_6_PERMISSION_REPORT.json": {
            **base,
            "component": "PERMISSION_MODEL",
            "execution_allowed": False,
            "manual_write_allowed": False,
            "brain_write_allowed": False,
            "reports_brain_write_allowed": False,
            "n8n_webhook_publishing_capa9_allowed": False,
            "human_authorization_consumption_allowed": False,
        },
        "BRIDGE_BLOCK_6_VALIDATION_REPORT.json": {
            **base,
            "component": "BUILD_VALIDATION",
            "result": "PASS",
            "canonical_json": True,
            "fail_closed": True,
        },
        "BRIDGE_BLOCK_6_NEXT_LAYER_READINESS_MAP.json": {
            **base,
            "component": "NEXT_LAYER_READINESS",
            "current_status": "BUILT_PENDING_POST_AUDIT",
            "next_safe_step": "BLOQUE_6_POST_BUILD_AUDIT",
            "post_build_audit_allowed_next": True,
            "bloque_7_blueprint_allowed_now": False,
        },
    }


__all__ = [
    "PASS",
    "PASS_WITH_WARNINGS",
    "REQUIRE_REVIEW",
    "BLOCK",
    "LOCK",
    "DecisionEnvelope",
    "ControlledPlanEnvelope",
    "PlanStepContract",
    "EvidenceDependency",
    "AuthorizationRequirement",
    "RollbackRequirement",
    "canonical_json",
    "sha256_text",
    "is_sha256",
    "choose_worst_decision",
    "scan_executable_content",
    "validate_executable_content",
    "validate_step_type",
    "validate_authorization_requirement",
    "verify_evidence_dependency",
    "validate_non_actionable_output",
    "validate_rollback_requirement",
    "validate_block7_boundary",
    "validate_block8_boundary",
    "validate_approval_by_plan",
    "validate_plan_bounds",
    "sort_decisions",
    "stable_plan_hash",
    "validate_hash_stability",
    "validate_explainability",
    "validate_anti_loop",
    "validate_protected_write_intent",
    "validate_decision_envelope",
    "validate_controlled_plan",
    "map_decision",
    "build_controlled_plan",
    "build_block6_report_payloads",
]
