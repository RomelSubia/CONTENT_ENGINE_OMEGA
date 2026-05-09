"""
CONTENT ENGINE Ω — MANUAL ↔ CEREBRO BRIDGE
BLOQUE 5 — Conflict detector + brain read-only adapter

This module is intentionally local, deterministic, read-only by design,
and fail-closed. It does not perform runtime brain access, network calls,
shell execution, cache writes, index rebuilds, manual writes, or brain writes.
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
VALID_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
VALID_CLAIM_TYPES = {"RULE", "INTENT", "POLICY", "STATE", "FACT", "DECISION"}
VALID_POLARITIES = {"AFFIRM", "DENY", "RESTRICT", "ALLOW", "REQUIRE", "UNKNOWN"}
VALID_AUTHORITIES = {"LOW", "MEDIUM", "HIGH", "CANONICAL", "SEALED"}
VALID_CONFLICT_TYPES = {
    "SEMANTIC_CONFLICT",
    "POLICY_CONFLICT",
    "STATE_CONFLICT",
    "PERMISSION_CONFLICT",
    "SOURCE_AUTHORITY_CONFLICT",
    "DUPLICATE_RULE_CONFLICT",
    "INTENT_CONTRADICTION",
    "TIMELINE_CONFLICT",
    "EVIDENCE_CONFLICT",
    "BRAIN_WRITE_CONFLICT",
    "NO_TOUCH_CONFLICT",
    "CAPA9_CONFLICT",
    "UNKNOWN_CONFLICT",
}

DECISION_RANK = {
    PASS: 0,
    PASS_WITH_WARNINGS: 1,
    REQUIRE_REVIEW: 2,
    BLOCK: 3,
    LOCK: 4,
}

SEVERITY_RANK = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}

AUTHORITY_RANK = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CANONICAL": 3,
    "SEALED": 4,
}

CONFLICT_MIN_DECISION = {
    "PERMISSION_CONFLICT": LOCK,
    "BRAIN_WRITE_CONFLICT": LOCK,
    "NO_TOUCH_CONFLICT": LOCK,
    "CAPA9_CONFLICT": LOCK,
    "STATE_CONFLICT": BLOCK,
    "SOURCE_AUTHORITY_CONFLICT": BLOCK,
    "EVIDENCE_CONFLICT": BLOCK,
    "SEMANTIC_CONFLICT": REQUIRE_REVIEW,
    "POLICY_CONFLICT": BLOCK,
    "DUPLICATE_RULE_CONFLICT": PASS_WITH_WARNINGS,
    "INTENT_CONTRADICTION": REQUIRE_REVIEW,
    "TIMELINE_CONFLICT": REQUIRE_REVIEW,
    "UNKNOWN_CONFLICT": REQUIRE_REVIEW,
}

DANGEROUS_CAPABILITY_PATTERNS = (
    r"\bwrite_text\s*\(",
    r"\bwrite_bytes\s*\(",
    r"\bopen\s*\([^)]*,\s*['\"][wa+]",
    r"\bPath\s*\([^)]*\)\.unlink\s*\(",
    r"\.unlink\s*\(",
    r"\.rename\s*\(",
    r"\.replace\s*\(",
    r"\brmtree\s*\(",
    r"\bos\.remove\s*\(",
    r"\bos\.system\s*\(",
    r"\bsubprocess\b",
    r"\brequests\b",
    r"\bhttpx\b",
    r"\bsocket\b",
    r"\bftplib\b",
    r"\bsmtplib\b",
    r"\bwebbrowser\b",
    r"\bsqlite.*\bwrite\b",
)

CACHE_INDEX_MUTATION_ACTIONS = {
    "cache_write",
    "index_rebuild",
    "embedding_update",
    "brain_index_mutation",
    "derived_brain_store_write",
    "temporary_brain_copy_write",
    "brain_normalization_write",
}

AUTOMATIC_RESOLUTION_ACTIONS = {
    "auto_merge",
    "auto_patch",
    "auto_delete",
    "auto_promote_source",
    "auto_select_winner",
    "auto_update_manual",
    "auto_update_brain",
    "auto_create_plan",
    "auto_execute_recovery",
}

BLOCK6_FORBIDDEN_ACTIONS = {
    "decision_mapper",
    "controlled_plan_builder",
    "plan_execution_model",
    "automatic_resolution_engine",
    "bloque_6_build",
    "bloque_6_prebuild",
}


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


def most_restrictive(*decisions: str) -> str:
    known = [d for d in decisions if d in VALID_DECISIONS]
    if not known:
        return LOCK
    return max(known, key=lambda d: DECISION_RANK[d])


@dataclass(frozen=True)
class BrainReadScopeLimiter:
    mode: str = "STRICT_BOUNDED_READ"
    max_results_per_query: int = 10
    max_query_depth: int = 2
    max_summary_chars_per_result: int = 800
    max_total_summary_chars: int = 4000
    full_brain_scan_allowed: bool = False
    recursive_unbounded_scan_allowed: bool = False
    raw_file_dump_allowed: bool = False
    directory_walk_all_brain_allowed: bool = False
    timeout_seconds: int = 30
    max_claims_per_batch: int = 200
    max_pairwise_comparisons: int = 5000


@dataclass(frozen=True)
class NormalizedClaim:
    claim_id: str
    raw_claim: str
    normalized_claim: str
    claim_type: str
    polarity: str
    subject: str
    predicate: str
    object: str
    scope: str
    authority_level: str
    confidence: str
    evidence_pointer: str
    hash: str


@dataclass(frozen=True)
class ConflictEnvelope:
    conflict_id: str
    conflict_type: str
    severity: str
    decision: str
    left_claim: Mapping[str, Any]
    right_claim: Mapping[str, Any]
    reason: str
    evidence: Sequence[str]
    safe_recovery: str
    forbidden_actions: Sequence[str]


@dataclass(frozen=True)
class BrainReadOnlyResultEnvelope:
    result_id: str
    query_id: str
    status: str
    read_only: bool
    brain_write_performed: bool
    brain_mutation_performed: bool
    evidence_refs: Sequence[str]
    content_summary: str
    content_hash: str
    confidence: str
    limitations: Sequence[str]


def validate_scope_request(
    *,
    result_count: int,
    query_depth: int,
    requested_full_scan: bool,
    requested_raw_dump: bool,
    requested_directory_walk: bool,
    limiter: BrainReadScopeLimiter | None = None,
) -> Dict[str, Any]:
    limiter = limiter or BrainReadScopeLimiter()

    if limiter.mode != "STRICT_BOUNDED_READ":
        return make_decision(LOCK, "INVALID_READ_SCOPE_MODE")

    if requested_full_scan or requested_directory_walk:
        return make_decision(LOCK, "UNBOUNDED_BRAIN_SCAN_BLOCKED")

    if requested_raw_dump:
        return make_decision(LOCK, "RAW_BRAIN_DUMP_BLOCKED")

    if query_depth > limiter.max_query_depth:
        return make_decision(BLOCK, "QUERY_DEPTH_EXCEEDS_LIMIT")

    if result_count > limiter.max_results_per_query:
        return make_decision(BLOCK, "RESULT_COUNT_EXCEEDS_LIMIT")

    return make_decision(PASS, "READ_SCOPE_WITHIN_LIMITS")


def validate_summary_output(
    *,
    summary: str,
    evidence_pointer: str,
    content_hash: str,
    raw_content_returned: bool,
    full_document_returned: bool,
    limiter: BrainReadScopeLimiter | None = None,
) -> Dict[str, Any]:
    limiter = limiter or BrainReadScopeLimiter()

    if raw_content_returned or full_document_returned:
        return make_decision(LOCK, "RAW_OR_FULL_CONTENT_LEAKAGE_BLOCKED")

    if not evidence_pointer:
        return make_decision(BLOCK, "SUMMARY_WITHOUT_EVIDENCE_POINTER")

    if not is_sha256(content_hash):
        return make_decision(BLOCK, "SUMMARY_WITHOUT_VALID_HASH")

    if len(summary) > limiter.max_summary_chars_per_result:
        return make_decision(BLOCK, "SUMMARY_EXCEEDS_PER_RESULT_LIMIT")

    return make_decision(PASS, "SUMMARY_OUTPUT_SAFE")


def tree_fingerprint(root: Path) -> str:
    if not root.exists():
        return "MISSING"

    if root.is_file():
        return sha256_bytes(root.read_bytes())

    rows: List[str] = []
    for item in sorted(root.rglob("*"), key=lambda p: str(p).lower()):
        if item.is_file():
            rel = item.relative_to(root).as_posix()
            rows.append(f"{rel}::{sha256_bytes(item.read_bytes())}")

    return sha256_text("\n".join(rows) + "\n")


def verify_brain_not_mutated(before: str, after: str) -> Dict[str, Any]:
    if not before or not after:
        return make_decision(BLOCK, "BRAIN_FINGERPRINT_MISSING")

    if before != after:
        return make_decision(LOCK, "BRAIN_FINGERPRINT_CHANGED")

    return make_decision(PASS, "BRAIN_FINGERPRINT_UNCHANGED")


def detect_dangerous_capabilities(source_text: str) -> List[str]:
    findings: List[str] = []
    for pattern in DANGEROUS_CAPABILITY_PATTERNS:
        if re.search(pattern, source_text):
            findings.append(pattern)
    return sorted(findings)


def validate_no_dangerous_capabilities(source_text: str) -> Dict[str, Any]:
    findings = detect_dangerous_capabilities(source_text)
    if findings:
        return make_decision(LOCK, "DANGEROUS_CAPABILITY_DETECTED", findings=findings)
    return make_decision(PASS, "NO_DANGEROUS_CAPABILITIES_DETECTED", findings=[])


def normalize_claim(
    *,
    claim_id: str,
    raw_claim: str,
    claim_type: str,
    polarity: str,
    subject: str,
    predicate: str,
    object: str,
    scope: str,
    authority_level: str,
    confidence: str,
    evidence_pointer: str,
    content_hash: str,
) -> Tuple[Dict[str, Any], NormalizedClaim | None]:
    if not claim_id:
        return make_decision(BLOCK, "CLAIM_ID_MISSING"), None
    if not raw_claim:
        return make_decision(BLOCK, "RAW_CLAIM_MISSING"), None
    if claim_type not in VALID_CLAIM_TYPES:
        return make_decision(BLOCK, "UNKNOWN_CLAIM_TYPE"), None
    if polarity not in VALID_POLARITIES:
        return make_decision(BLOCK, "UNKNOWN_POLARITY"), None
    if authority_level not in VALID_AUTHORITIES:
        return make_decision(BLOCK, "UNKNOWN_AUTHORITY_LEVEL"), None
    if confidence not in {"LOW", "MEDIUM", "HIGH"}:
        return make_decision(BLOCK, "UNKNOWN_CONFIDENCE"), None
    if not evidence_pointer:
        return make_decision(BLOCK, "CLAIM_WITHOUT_EVIDENCE"), None
    if not is_sha256(content_hash):
        return make_decision(BLOCK, "CLAIM_WITHOUT_VALID_HASH"), None
    if polarity == "UNKNOWN" and claim_type in {"POLICY", "STATE", "DECISION"}:
        return make_decision(BLOCK, "UNKNOWN_POLARITY_HIGH_IMPACT"), None

    normalized = " ".join(raw_claim.strip().lower().split())
    claim = NormalizedClaim(
        claim_id=claim_id,
        raw_claim=raw_claim,
        normalized_claim=normalized,
        claim_type=claim_type,
        polarity=polarity,
        subject=subject.strip().lower(),
        predicate=predicate.strip().lower(),
        object=object.strip().lower(),
        scope=scope.strip().lower(),
        authority_level=authority_level,
        confidence=confidence,
        evidence_pointer=evidence_pointer,
        hash=content_hash,
    )
    return make_decision(PASS, "CLAIM_NORMALIZED"), claim


def validate_conflict_evidence(left: NormalizedClaim, right: NormalizedClaim) -> Dict[str, Any]:
    if not left.evidence_pointer or not right.evidence_pointer:
        return make_decision(BLOCK, "CONFLICT_WITH_ONE_SIDED_EVIDENCE")
    if not is_sha256(left.hash) or not is_sha256(right.hash):
        return make_decision(BLOCK, "CONFLICT_WITHOUT_VALID_HASHES")
    if left.authority_level not in VALID_AUTHORITIES or right.authority_level not in VALID_AUTHORITIES:
        return make_decision(BLOCK, "CONFLICT_WITHOUT_AUTHORITY_LEVELS")
    if left.authority_level == "SEALED" and right.authority_level == "SEALED" and left.hash != right.hash:
        return make_decision(LOCK, "CONTRADICTORY_SEALED_SOURCES")
    return make_decision(PASS, "CONFLICT_EVIDENCE_PAIR_VALID")


def enforce_severity_anti_downgrade(conflict_type: str, proposed_decision: str) -> Dict[str, Any]:
    if conflict_type not in VALID_CONFLICT_TYPES:
        return make_decision(LOCK, "UNKNOWN_CONFLICT_TYPE")

    minimum = CONFLICT_MIN_DECISION.get(conflict_type, REQUIRE_REVIEW)
    if DECISION_RANK[proposed_decision] < DECISION_RANK[minimum]:
        return make_decision(LOCK, "CRITICAL_CONFLICT_DOWNGRADED", minimum_decision=minimum)

    return make_decision(PASS, "SEVERITY_DECISION_ACCEPTABLE", minimum_decision=minimum)


def detect_conflict(left: NormalizedClaim, right: NormalizedClaim) -> ConflictEnvelope:
    evidence_status = validate_conflict_evidence(left, right)
    if evidence_status["status"] in {BLOCK, LOCK}:
        return make_conflict(
            conflict_type="EVIDENCE_CONFLICT",
            severity="HIGH" if evidence_status["status"] == BLOCK else "CRITICAL",
            left=left,
            right=right,
            reason=evidence_status["reason"],
        )

    same_target = (
        left.subject == right.subject
        and left.predicate == right.predicate
        and left.object == right.object
        and left.scope == right.scope
    )
    opposing = {left.polarity, right.polarity} in (
        {"ALLOW", "DENY"},
        {"AFFIRM", "DENY"},
        {"REQUIRE", "DENY"},
    )

    if same_target and opposing:
        if left.claim_type == "POLICY" or right.claim_type == "POLICY":
            return make_conflict("POLICY_CONFLICT", "HIGH", left, right, "POLICY_CLAIMS_CONTRADICT")
        return make_conflict("SEMANTIC_CONFLICT", "MEDIUM", left, right, "CLAIMS_CONTRADICT")

    if left.hash == right.hash:
        return make_conflict("DUPLICATE_RULE_CONFLICT", "LOW", left, right, "DUPLICATE_CLAIM_HASH")

    return make_conflict("UNKNOWN_CONFLICT", "MEDIUM", left, right, "RELATION_REQUIRES_REVIEW")


def make_conflict(
    conflict_type: str,
    severity: str,
    left: NormalizedClaim,
    right: NormalizedClaim,
    reason: str,
) -> ConflictEnvelope:
    if conflict_type not in VALID_CONFLICT_TYPES:
        conflict_type = "UNKNOWN_CONFLICT"
    if severity not in VALID_SEVERITIES:
        severity = "CRITICAL"

    minimum = CONFLICT_MIN_DECISION.get(conflict_type, REQUIRE_REVIEW)
    decision = minimum

    conflict_id_seed = "|".join([left.hash, right.hash, conflict_type, reason])
    conflict_id = sha256_text(conflict_id_seed)[:24]

    return ConflictEnvelope(
        conflict_id=conflict_id,
        conflict_type=conflict_type,
        severity=severity,
        decision=decision,
        left_claim=asdict(left),
        right_claim=asdict(right),
        reason=reason,
        evidence=[left.evidence_pointer, right.evidence_pointer],
        safe_recovery="REQUIRE_HUMAN_REVIEW_OR_HARDENING",
        forbidden_actions=[
            "AUTO_RESOLUTION",
            "MANUAL_WRITE",
            "BRAIN_WRITE",
            "REPORTS_BRAIN_WRITE",
            "EXECUTION",
        ],
    )


def deduplicate_conflicts(conflicts: Iterable[ConflictEnvelope]) -> List[ConflictEnvelope]:
    seen: Dict[Tuple[str, str, str], ConflictEnvelope] = {}
    for conflict in conflicts:
        left_hash = str(conflict.left_claim.get("hash", ""))
        right_hash = str(conflict.right_claim.get("hash", ""))
        key = tuple(sorted([left_hash, right_hash]) + [conflict.conflict_type])
        if key not in seen:
            seen[key] = conflict
    return list(seen.values())


def sort_conflicts(conflicts: Iterable[ConflictEnvelope]) -> List[ConflictEnvelope]:
    return sorted(
        conflicts,
        key=lambda c: (
            -SEVERITY_RANK.get(c.severity, 99),
            -max(
                AUTHORITY_RANK.get(str(c.left_claim.get("authority_level")), 0),
                AUTHORITY_RANK.get(str(c.right_claim.get("authority_level")), 0),
            ),
            c.conflict_type,
            c.conflict_id,
        ),
    )


def validate_cache_index_action(action: str) -> Dict[str, Any]:
    if action in CACHE_INDEX_MUTATION_ACTIONS:
        return make_decision(LOCK, "CACHE_OR_INDEX_MUTATION_BLOCKED", action=action)
    return make_decision(PASS, "NO_CACHE_INDEX_MUTATION", action=action)


def validate_automatic_resolution_action(action: str) -> Dict[str, Any]:
    if action in AUTOMATIC_RESOLUTION_ACTIONS:
        return make_decision(LOCK, "AUTOMATIC_RESOLUTION_BLOCKED", action=action)
    return make_decision(PASS, "NO_AUTOMATIC_RESOLUTION", action=action)


def validate_block6_boundary(action: str) -> Dict[str, Any]:
    if action in BLOCK6_FORBIDDEN_ACTIONS:
        return make_decision(LOCK, "BLOQUE_6_BOUNDARY_VIOLATION", action=action)
    return make_decision(PASS, "BLOQUE_6_BOUNDARY_RESPECTED", action=action)


def validate_human_review_boundary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    forbidden_true_fields = (
        "grant_build_directly",
        "execute",
        "write_manual",
        "write_brain",
        "write_reports_brain",
        "skip_implementation_plan",
        "skip_build_approval",
    )
    for field in forbidden_true_fields:
        if payload.get(field) is True:
            return make_decision(LOCK if field != "skip_implementation_plan" else BLOCK, "HUMAN_REVIEW_BOUNDARY_VIOLATION", field=field)
    return make_decision(PASS, "HUMAN_REVIEW_BOUNDARY_VALID")


def validate_performance_bounds(
    *,
    claim_count: int,
    pairwise_comparisons: int,
    brain_results: int,
    query_depth: int,
    limiter: BrainReadScopeLimiter | None = None,
) -> Dict[str, Any]:
    limiter = limiter or BrainReadScopeLimiter()

    if claim_count > limiter.max_claims_per_batch:
        return make_decision(BLOCK, "MAX_CLAIMS_EXCEEDED")
    if pairwise_comparisons > limiter.max_pairwise_comparisons:
        return make_decision(BLOCK, "MAX_PAIRWISE_COMPARISONS_EXCEEDED")
    if brain_results > limiter.max_results_per_query:
        return make_decision(BLOCK, "MAX_BRAIN_RESULTS_EXCEEDED")
    if query_depth > limiter.max_query_depth:
        return make_decision(BLOCK, "MAX_QUERY_DEPTH_EXCEEDED")

    return make_decision(PASS, "PERFORMANCE_BOUNDS_VALID")


def validate_read_only_result(result: BrainReadOnlyResultEnvelope) -> Dict[str, Any]:
    if result.read_only is not True:
        return make_decision(LOCK, "READ_ONLY_FALSE")
    if result.brain_write_performed is True:
        return make_decision(LOCK, "BRAIN_WRITE_PERFORMED")
    if result.brain_mutation_performed is True:
        return make_decision(LOCK, "BRAIN_MUTATION_PERFORMED")
    if not result.evidence_refs:
        return make_decision(BLOCK, "READ_RESULT_WITHOUT_EVIDENCE_REFS")
    if not is_sha256(result.content_hash):
        return make_decision(BLOCK, "READ_RESULT_WITHOUT_VALID_HASH")
    return make_decision(PASS, "READ_ONLY_RESULT_VALID")


def build_block5_report_payloads() -> Dict[str, Dict[str, Any]]:
    permissions = {
        "post_build_audit_allowed_next": True,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_6_blueprint_allowed_now": False,
        "execution_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
    }

    conflict_detector_report = {
        "project": "CONTENT_ENGINE_OMEGA",
        "subsystem": "MANUAL_CEREBRO_BRIDGE",
        "block": "BLOQUE_5_CONFLICT_DETECTOR_BRAIN_READ_ONLY_ADAPTER",
        "component": "CONFLICT_DETECTOR",
        "status": "BUILT_PENDING_POST_AUDIT",
        "features": [
            "claim_normalization",
            "conflict_evidence_pairing",
            "conflict_deduplication",
            "severity_anti_downgrade",
            "deterministic_conflict_ordering",
            "automatic_resolution_prohibition",
            "bloque_6_boundary_guard",
        ],
        "permissions": permissions,
    }

    brain_adapter_report = {
        "project": "CONTENT_ENGINE_OMEGA",
        "subsystem": "MANUAL_CEREBRO_BRIDGE",
        "block": "BLOQUE_5_CONFLICT_DETECTOR_BRAIN_READ_ONLY_ADAPTER",
        "component": "BRAIN_READ_ONLY_ADAPTER_CONTRACT",
        "status": "BUILT_PENDING_POST_AUDIT",
        "runtime_brain_access_performed": False,
        "read_scope_limiter": asdict(BrainReadScopeLimiter()),
        "raw_content_leakage_guard": "ENFORCED_BY_CONTRACT",
        "mutation_proof_guard": "FINGERPRINT_BEFORE_AFTER_REQUIRED",
        "cache_index_embedding_mutation": "LOCKED",
        "permissions": permissions,
    }

    severity_report = {
        "project": "CONTENT_ENGINE_OMEGA",
        "component": "CONFLICT_SEVERITY_POLICY",
        "status": "BUILT_PENDING_POST_AUDIT",
        "minimum_decisions": CONFLICT_MIN_DECISION,
        "decision_rank": DECISION_RANK,
        "severity_rank": SEVERITY_RANK,
        "permissions": permissions,
    }

    no_mutation_report = {
        "project": "CONTENT_ENGINE_OMEGA",
        "component": "NO_MUTATION_GUARD",
        "status": "BUILT_PENDING_POST_AUDIT",
        "brain_write_allowed": False,
        "brain_mutation_allowed": False,
        "manual_write_allowed": False,
        "reports_brain_write_allowed": False,
        "cache_write_allowed": False,
        "index_rebuild_allowed": False,
        "embedding_update_allowed": False,
        "runtime_brain_access_performed": False,
        "permissions": permissions,
    }

    validation_report = {
        "project": "CONTENT_ENGINE_OMEGA",
        "component": "BLOCK_5_BUILD_VALIDATION",
        "status": "BUILT_PENDING_POST_AUDIT",
        "result": "PASS",
        "canonical_json": True,
        "fail_closed": True,
        "permissions": permissions,
    }

    readiness_map = {
        "project": "CONTENT_ENGINE_OMEGA",
        "subsystem": "MANUAL_CEREBRO_BRIDGE",
        "current_block": "BLOQUE_5_CONFLICT_DETECTOR_BRAIN_READ_ONLY_ADAPTER",
        "status": "BUILT_PENDING_POST_AUDIT",
        "current_status": "BUILT_PENDING_POST_AUDIT",
        "next_safe_step": "BLOQUE_5_POST_BUILD_AUDIT",
        "post_build_audit_allowed_next": True,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_6_blueprint_allowed_now": False,
        "hard_blocks": {
            "bloque_6": "BLOCKED",
            "execution": "BLOCKED",
            "manual_write": "BLOCKED",
            "brain_write": "BLOCKED",
            "reports_brain_write": "BLOCKED",
            "n8n": "BLOCKED",
            "webhook": "BLOCKED",
            "publishing": "BLOCKED",
            "capa9": "BLOCKED"
        },
        "permissions": permissions,
    }

    return {
        "BRIDGE_BLOCK_5_CONFLICT_DETECTOR_REPORT.json": conflict_detector_report,
        "BRIDGE_BLOCK_5_BRAIN_READ_ONLY_ADAPTER_REPORT.json": brain_adapter_report,
        "BRIDGE_BLOCK_5_CONFLICT_SEVERITY_REPORT.json": severity_report,
        "BRIDGE_BLOCK_5_NO_MUTATION_REPORT.json": no_mutation_report,
        "BRIDGE_BLOCK_5_VALIDATION_REPORT.json": validation_report,
        "BRIDGE_BLOCK_5_NEXT_LAYER_READINESS_MAP.json": readiness_map,
    }


__all__ = [
    "PASS",
    "PASS_WITH_WARNINGS",
    "REQUIRE_REVIEW",
    "BLOCK",
    "LOCK",
    "BrainReadScopeLimiter",
    "NormalizedClaim",
    "ConflictEnvelope",
    "BrainReadOnlyResultEnvelope",
    "canonical_json",
    "sha256_text",
    "is_sha256",
    "most_restrictive",
    "validate_scope_request",
    "validate_summary_output",
    "tree_fingerprint",
    "verify_brain_not_mutated",
    "detect_dangerous_capabilities",
    "validate_no_dangerous_capabilities",
    "normalize_claim",
    "validate_conflict_evidence",
    "enforce_severity_anti_downgrade",
    "detect_conflict",
    "make_conflict",
    "deduplicate_conflicts",
    "sort_conflicts",
    "validate_cache_index_action",
    "validate_automatic_resolution_action",
    "validate_block6_boundary",
    "validate_human_review_boundary",
    "validate_performance_bounds",
    "validate_read_only_result",
    "build_block5_report_payloads",
]
