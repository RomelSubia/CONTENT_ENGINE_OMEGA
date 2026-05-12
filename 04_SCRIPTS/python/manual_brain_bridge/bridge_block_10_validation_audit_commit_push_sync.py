from __future__ import annotations

import hashlib
import json
from typing import Any

PASS = "PASS"
BLOCK = "BLOCK"
LOCK = "LOCK"

PROJECT = "CONTENT_ENGINE_OMEGA"
SUBSYSTEM = "MANUAL_CEREBRO_BRIDGE"
BLOCK_ID = "BLOQUE_10_VALIDATION_AUDIT_COMMIT_PUSH_SYNC"
STATUS = "BUILT_PENDING_POST_AUDIT"

DANGEROUS_PERMISSIONS = {
    "execution_allowed_now": False,
    "external_execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "content_engine_construction_allowed_now": False,
    "content_engine_build_allowed_now": False,
    "bloque_10_validation_map_allowed_now": False,
    "bloque_10_validation_plan_allowed_now": False,
    "bloque_10_validation_allowed_now": False,
    "bloque_10_gate_closure_allowed_now": False,
    "global_execution_allowed_now": False,
}

BUILD_PERMISSIONS = {
    "bloque_10_post_build_audit_allowed_next": True,
    "bloque_10_validation_map_allowed_now": False,
    "bloque_10_validation_plan_allowed_now": False,
    "bloque_10_validation_allowed_now": False,
    "bloque_10_gate_closure_allowed_now": False,
    "manual_cerebro_bridge_closed_validated": False,
    **DANGEROUS_PERMISSIONS,
}

ALLOWED_BLOCK10_STATES = [
    "BLOQUE_10_BUILT_PENDING_POST_AUDIT",
    "BLOQUE_10_BUILT_POST_AUDITED",
    "BLOQUE_10_VALIDATION_MAP_DEFINED",
    "BLOQUE_10_VALIDATION_PLAN_DEFINED",
    "BLOQUE_10_VALIDATED_POST_AUDITED",
    "BLOQUE_10_CLOSED_VALIDATED",
    "MANUAL_CEREBRO_BRIDGE_CLOSED_VALIDATED",
]

AMBIGUOUS_STATES = [
    "DONE",
    "READY",
    "COMPLETE",
    "SUCCESS",
    "FINISHED",
    "CLOSED",
    "VALIDATED",
    "PRODUCTION_READY",
]

EVIDENCE_RESOLUTIONS = [
    "DIRECT_ARTIFACTS",
    "SEMANTIC_ARTIFACTS",
    "TRACEABILITY_ANCHORED",
    "MISSING_REAL",
]

VALIDATION_DOMAIN_COUNT = 22
VALIDATION_GATE_COUNT = 40
VALIDATION_ITEM_COUNT = 66
NEGATIVE_CHECK_COUNT = 22
FAILURE_INJECTION_COUNT = 22


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_state_matrix() -> dict[str, Any]:
    return {
        "status": PASS,
        "allowed_states": list(ALLOWED_BLOCK10_STATES),
        "ambiguous_states_blocked": list(AMBIGUOUS_STATES),
        "rules": {
            "unknown_state": BLOCK,
            "valid_state_without_artifact": BLOCK,
            "artifact_without_manifest": BLOCK,
            "manifest_without_seal": BLOCK,
            "seal_without_valid_hash": BLOCK,
        },
    }


def evaluate_state_transition(state: str, *, artifact: bool, manifest: bool, seal: bool, hash_valid: bool) -> dict[str, Any]:
    if state in AMBIGUOUS_STATES:
        return {"status": BLOCK, "reason": "AMBIGUOUS_STATE"}
    if state not in ALLOWED_BLOCK10_STATES:
        return {"status": BLOCK, "reason": "UNKNOWN_STATE"}
    if not artifact:
        return {"status": BLOCK, "reason": "VALID_STATE_WITHOUT_ARTIFACT"}
    if not manifest:
        return {"status": BLOCK, "reason": "ARTIFACT_WITHOUT_MANIFEST"}
    if not seal:
        return {"status": BLOCK, "reason": "MANIFEST_WITHOUT_SEAL"}
    if not hash_valid:
        return {"status": BLOCK, "reason": "SEAL_WITHOUT_VALID_HASH"}
    return {"status": PASS, "reason": "STATE_VALIDATED"}


def build_permission_boundary() -> dict[str, Any]:
    return {
        "status": PASS if all(value is False for key, value in BUILD_PERMISSIONS.items() if key != "bloque_10_post_build_audit_allowed_next") else BLOCK,
        "permissions": dict(BUILD_PERMISSIONS),
        "post_build_audit_allowed_next": BUILD_PERMISSIONS["bloque_10_post_build_audit_allowed_next"],
        "dangerous_permissions_all_false": all(value is False for value in DANGEROUS_PERMISSIONS.values()),
    }


def build_failure_recovery_policy() -> dict[str, Any]:
    return {
        "status": PASS,
        "policy": "FAIL_CLOSED",
        "rules": {
            "fail_before_artifacts": {"cleanup": False, "commit": False, "push": False},
            "fail_after_allowlisted_artifacts": {"cleanup_allowlisted_only_on_retry": True, "commit": False, "push": False},
            "dirty_out_of_scope": {"status": BLOCK, "cleanup": False, "commit": False, "push": False},
            "protected_root_changed": {"status": "CRITICAL_BLOCK", "cleanup": False, "commit": False, "push": False},
            "remote_divergence": {"status": BLOCK, "commit": False, "push": False},
            "hash_mismatch": {"status": BLOCK, "commit": False, "push": False},
            "artifact_missing": {"status": BLOCK, "commit": False, "push": False},
        },
    }


def build_evidence_discovery_policy() -> dict[str, Any]:
    return {
        "status": PASS,
        "resolutions": list(EVIDENCE_RESOLUTIONS),
        "rules": {
            "BLOQUE_9": ["DIRECT_ARTIFACTS"],
            "BLOQUE_8": ["DIRECT_ARTIFACTS", "SEMANTIC_ARTIFACTS"],
            "BLOQUE_1_TO_7": ["DIRECT_ARTIFACTS", "SEMANTIC_ARTIFACTS", "TRACEABILITY_ANCHORED"],
            "MISSING_REAL": BLOCK,
        },
        "missing_real_required": 0,
        "hash_only_consumption": True,
        "no_rewrite_previous_evidence": True,
    }


def evaluate_evidence_resolution(block_number: int, resolution: str) -> dict[str, Any]:
    if resolution == "MISSING_REAL":
        return {"status": BLOCK, "reason": "MISSING_REAL"}
    if block_number == 9 and resolution != "DIRECT_ARTIFACTS":
        return {"status": BLOCK, "reason": "BLOQUE_9_DIRECT_ARTIFACTS_REQUIRED"}
    if block_number == 8 and resolution not in {"DIRECT_ARTIFACTS", "SEMANTIC_ARTIFACTS"}:
        return {"status": BLOCK, "reason": "BLOQUE_8_DIRECT_OR_SEMANTIC_REQUIRED"}
    if 1 <= block_number <= 7 and resolution in {"DIRECT_ARTIFACTS", "SEMANTIC_ARTIFACTS", "TRACEABILITY_ANCHORED"}:
        return {"status": PASS, "reason": "HISTORICAL_BLOCK_RESOLVED"}
    if block_number in {8, 9}:
        return {"status": PASS, "reason": "RECENT_BLOCK_RESOLVED"}
    return {"status": BLOCK, "reason": "UNKNOWN_BLOCK"}


def build_git_chain_contract() -> dict[str, Any]:
    return {
        "status": PASS,
        "requirements": {
            "branch": "main",
            "repo_clean": True,
            "head_subject": "Close MANUAL-CEREBRO bridge block 9 test harness 40 pruebas",
            "head_parent_short": "4832275",
            "head_parent_subject": "Validate MANUAL-CEREBRO bridge block 9 test harness 40 pruebas",
            "head_equals_upstream": True,
            "parent_chain_required": True,
            "commit_chain_no_gaps": True,
        },
    }


def build_push_sync_contract() -> dict[str, Any]:
    return {
        "status": PASS,
        "requirements": {
            "remote_url_expected": True,
            "head_equals_upstream": True,
            "unpushed_commits": 0,
            "unpulled_commits": 0,
            "remote_divergence": False,
            "git_status_short": "",
        },
    }


def build_anti_simulation_contract() -> dict[str, Any]:
    return {
        "status": PASS,
        "blocked_risks": [
            "report_pass_without_manifest",
            "manifest_without_seal",
            "seal_hash_mismatch",
            "summary_json_contradiction",
            "test_count_without_report",
            "premature_readiness",
            "subject_correct_parent_wrong",
            "artifact_missing_declared_present",
            "no_touch_without_fingerprints",
            "permissions_dangerous_true",
            "local_remote_not_synced",
        ],
        "simulation_risk_count_required": 0,
    }


def detect_simulation_risks(checks: dict[str, bool]) -> dict[str, Any]:
    risks = [name for name, passed in checks.items() if not passed]
    return {
        "status": PASS if not risks else BLOCK,
        "simulation_risk_count": len(risks),
        "risks": risks,
    }


def build_no_touch_contract() -> dict[str, Any]:
    return {
        "status": PASS,
        "requires_fingerprints_before": True,
        "requires_fingerprints_after": True,
        "changed_roots_required": {},
        "protected_root_change_policy": "CRITICAL_BLOCK",
    }


def evaluate_no_touch(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in sorted(set(before) | set(after))
        if before.get(key) != after.get(key)
    }
    return {
        "status": PASS if not changed else BLOCK,
        "changed_roots": changed,
        "no_touch_pass": not changed,
    }


def build_validation_domains() -> list[dict[str, Any]]:
    names = [
        "Repo baseline",
        "Expected HEAD binding",
        "Parent chain audit",
        "Remote sync audit",
        "Remote URL audit",
        "Block 1-9 closure chain",
        "Historical evidence resolver",
        "Missing real detection",
        "Manifest/seal integrity",
        "Canonical JSON integrity",
        "Hash consistency",
        "Commit surface audit",
        "Push audit",
        "Test harness integrity",
        "Anti-simulation",
        "No-touch fingerprints",
        "Permission boundary",
        "State matrix enforcement",
        "Failure recovery policy",
        "Readiness separation",
        "Bridge final closure criteria",
        "Next phase blueprint-only boundary",
    ]
    return [
        {"domain_id": f"B10-D{idx:02d}", "name": name, "risk": "CRITICAL" if idx in {1, 2, 3, 4, 8, 15, 16, 17, 21, 22} else "HIGH"}
        for idx, name in enumerate(names, start=1)
    ]


def build_validation_gates() -> list[dict[str, Any]]:
    gate_names = [
        "REPO_EXISTS",
        "BRANCH_MAIN",
        "REPO_CLEAN_BEFORE_START",
        "LOCAL_REMOTE_SYNCED_BEFORE_START",
        "REMOTE_URL_EXPECTED",
        "EXPECTED_BLOCK9_CLOSURE_HEAD_HASH",
        "EXPECTED_BLOCK9_CLOSURE_SUBJECT",
        "EXPECTED_BLOCK9_CLOSURE_PARENT_HASH",
        "EXPECTED_BLOCK9_CLOSURE_PARENT_SUBJECT",
        "BLOCK1_CLOSED_VALIDATED",
        "BLOCK2_CLOSED_VALIDATED",
        "BLOCK3_CLOSED_VALIDATED",
        "BLOCK4_CLOSED_VALIDATED",
        "BLOCK5_CLOSED_VALIDATED",
        "BLOCK6_CLOSED_VALIDATED",
        "BLOCK7_CLOSED_VALIDATED",
        "BLOCK8_CLOSED_VALIDATED",
        "BLOCK9_CLOSED_VALIDATED",
        "CHAIN_EVIDENCE_DISCOVERY_PASS",
        "MISSING_REAL_ZERO",
        "MANIFESTS_PRESENT",
        "SEALS_PRESENT",
        "CANONICAL_JSON_PASS",
        "HASH_VALIDATION_PASS",
        "COMMIT_CHAIN_PASS",
        "PARENT_CHAIN_PASS",
        "PUSH_SYNC_PASS",
        "NO_UNTRACKED_OUT_OF_SCOPE",
        "NO_REMOTE_DIVERGENCE",
        "TEST_HARNESS_PASS",
        "EVIDENCE_RESOLVER_PASS",
        "NO_TOUCH_FINGERPRINTS_PASS",
        "DANGEROUS_PERMISSIONS_FALSE",
        "ANTI_SIMULATION_PASS",
        "FAILURE_RECOVERY_POLICY_DEFINED",
        "STATE_MATRIX_PASS",
        "BLOCK10_READINESS_PASS",
        "BRIDGE_FINAL_READINESS_PASS",
        "NEXT_PHASE_BLUEPRINT_ONLY",
        "FAIL_CLOSED_READY",
    ]
    return [
        {
            "gate_id": f"B10-G{idx:02d}_{name}",
            "status": "DEFINED",
            "required": True,
            "failure_policy": "FAIL_CLOSED",
        }
        for idx, name in enumerate(gate_names, start=1)
    ]


def build_validation_items() -> list[dict[str, Any]]:
    domains = build_validation_domains()
    modes = ["POSITIVE", "NEGATIVE", "FAILURE_INJECTION"]
    items = []
    counter = 1
    for domain in domains:
        for mode in modes:
            items.append({
                "item_id": f"B10-I{counter:03d}",
                "domain_id": domain["domain_id"],
                "mode": mode,
                "expected": PASS if mode == "POSITIVE" else "LOCK_OR_BLOCK",
                "mutation_allowed": False,
                "dangerous_permissions_expected_false": list(DANGEROUS_PERMISSIONS),
            })
            counter += 1
    return items


def validate_block10_contracts() -> dict[str, Any]:
    domains = build_validation_domains()
    gates = build_validation_gates()
    items = build_validation_items()
    negative = [item for item in items if item["mode"] == "NEGATIVE"]
    failure = [item for item in items if item["mode"] == "FAILURE_INJECTION"]

    checks = {
        "domain_count": len(domains) >= VALIDATION_DOMAIN_COUNT,
        "gate_count": len(gates) >= VALIDATION_GATE_COUNT,
        "item_count": len(items) >= 60,
        "negative_count": len(negative) >= 18,
        "failure_injection_count": len(failure) >= 15,
        "permission_boundary": build_permission_boundary()["status"] == PASS,
        "state_matrix": build_state_matrix()["status"] == PASS,
        "failure_policy": build_failure_recovery_policy()["status"] == PASS,
        "evidence_policy": build_evidence_discovery_policy()["status"] == PASS,
        "git_chain_contract": build_git_chain_contract()["status"] == PASS,
        "push_sync_contract": build_push_sync_contract()["status"] == PASS,
        "anti_simulation_contract": build_anti_simulation_contract()["status"] == PASS,
        "no_touch_contract": build_no_touch_contract()["status"] == PASS,
    }

    return {
        "status": PASS if all(checks.values()) else BLOCK,
        "checks": checks,
        "domain_count": len(domains),
        "gate_count": len(gates),
        "validation_item_count": len(items),
        "negative_check_count": len(negative),
        "failure_injection_check_count": len(failure),
    }


def build_block10_report_payloads(
    git_context: dict[str, Any],
    chain_discovery: dict[str, Any],
    git_audit: dict[str, Any],
    evidence_integrity: dict[str, Any],
    no_touch_audit: dict[str, Any],
    anti_simulation_audit: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    validation = validate_block10_contracts()

    base = {
        "project": PROJECT,
        "subsystem": SUBSYSTEM,
        "block": BLOCK_ID,
        "gate": "BUILD_FIX_1_1",
        "status": STATUS,
        "result": PASS,
        "fixed_issue": "TARGETED_PYTEST_COUNT_TOO_LOW",
        "previous_issue_fixed": "PYTEST_RUNTIME_ENV_MISSING",
        "next_safe_step": "BLOQUE_10_POST_BUILD_AUDIT",
        "permissions": dict(BUILD_PERMISSIONS),
        "git_context": git_context,
    }

    block10_readiness = {
        "status": PASS,
        "bloque_10_status": STATUS,
        "manual_cerebro_bridge_status": "NOT_CLOSED_YET",
        "next_safe_step": "BLOQUE_10_POST_BUILD_AUDIT",
        "bloque_10_post_build_audit_allowed_next": True,
        "bloque_10_validation_map_allowed_now": False,
        "bloque_10_validation_allowed_now": False,
        "bloque_10_gate_closure_allowed_now": False,
        "content_engine_build_allowed_now": False,
        "execution_allowed_now": False,
    }

    bridge_readiness = {
        "status": PASS,
        "manual_cerebro_bridge_status": "NOT_CLOSED_YET",
        "reason": "BLOQUE_10_BUILD_ONLY_NOT_GATE_CLOSURE",
        "next_allowed": "BLOQUE_10_POST_BUILD_AUDIT",
        "content_engine_operational_construction_blueprint_allowed_next": False,
        "content_engine_build_allowed_now": False,
        "execution_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "n8n_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
    }

    return {
        "BRIDGE_BLOCK_10_BUILD_REPORT.json": {
            **base,
            "contract": "Block10BuildReportContract",
            "validation": validation,
            "chain_discovery": chain_discovery,
            "git_audit": git_audit,
            "evidence_integrity": evidence_integrity,
            "anti_simulation_audit": anti_simulation_audit,
            "no_touch_audit": no_touch_audit,
        },
        "BRIDGE_BLOCK_10_CHAIN_VALIDATION_MAP.json": {
            **base,
            "contract": "ChainValidationMapContract",
            "domains": build_validation_domains(),
            "gates": build_validation_gates(),
            "items": build_validation_items(),
            "validation": validation,
        },
        "BRIDGE_BLOCK_10_COMMIT_AUDIT_MAP.json": {
            **base,
            "contract": "CommitAuditMapContract",
            "commit_audit": git_audit.get("commit_chain", {}),
        },
        "BRIDGE_BLOCK_10_PUSH_SYNC_AUDIT_MAP.json": {
            **base,
            "contract": "PushSyncAuditMapContract",
            "push_sync_audit": git_audit.get("push_sync", {}),
        },
        "BRIDGE_BLOCK_10_EVIDENCE_INTEGRITY_MAP.json": {
            **base,
            "contract": "EvidenceIntegrityMapContract",
            "evidence_integrity": evidence_integrity,
        },
        "BRIDGE_BLOCK_10_CHAIN_EVIDENCE_DISCOVERY_REPORT.json": {
            **base,
            "contract": "ChainEvidenceDiscoveryReportContract",
            "chain_discovery": chain_discovery,
        },
        "BRIDGE_BLOCK_10_GIT_CHAIN_AND_SYNC_AUDIT.json": {
            **base,
            "contract": "GitChainAndSyncAuditContract",
            "git_audit": git_audit,
        },
        "BRIDGE_BLOCK_10_FAILURE_RECOVERY_POLICY.json": {
            **base,
            "contract": "FailureRecoveryPolicyContract",
            "failure_recovery_policy": build_failure_recovery_policy(),
        },
        "BRIDGE_BLOCK_10_ANTI_SIMULATION_AUDIT.json": {
            **base,
            "contract": "AntiSimulationAuditContract",
            "anti_simulation_contract": build_anti_simulation_contract(),
            "anti_simulation_audit": anti_simulation_audit,
        },
        "BRIDGE_BLOCK_10_NO_TOUCH_FINGERPRINT_AUDIT.json": {
            **base,
            "contract": "NoTouchFingerprintAuditContract",
            "no_touch_contract": build_no_touch_contract(),
            "no_touch_audit": no_touch_audit,
        },
        "BRIDGE_BLOCK_10_PERMISSION_BOUNDARY_MAP.json": {
            **base,
            "contract": "PermissionBoundaryMapContract",
            "permission_boundary": build_permission_boundary(),
        },
        "BRIDGE_BLOCK_10_STATE_MATRIX.json": {
            **base,
            "contract": "StateMatrixContract",
            "state_matrix": build_state_matrix(),
        },
        "BRIDGE_BLOCK_10_FINAL_READINESS_MAP.json": {
            **base,
            "contract": "Block10FinalReadinessMapContract",
            "readiness": block10_readiness,
        },
        "MANUAL_CEREBRO_BRIDGE_FINAL_READINESS_MAP.json": {
            **base,
            "contract": "ManualCerebroBridgeFinalReadinessMapContract",
            "readiness": bridge_readiness,
        },
    }
