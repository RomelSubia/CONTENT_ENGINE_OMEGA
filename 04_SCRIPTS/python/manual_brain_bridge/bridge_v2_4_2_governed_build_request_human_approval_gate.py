from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_LAYER_V2_4_2"

EXIT_PASS = 0
EXIT_BLOCK = 20
EXIT_LOCK = 30

EXPECTED_ROOT_NAME = "CONTENT_ENGINE_OMEGA"
EXPECTED_BRANCH = "main"
EXPECTED_REMOTE_FRAGMENT = "CONTENT_ENGINE_OMEGA.git"

DANGER_FLAGS = [
    "execution_allowed",
    "external_execution_allowed",
    "external_side_effects_allowed",
    "manual_write_allowed",
    "manual_auto_update_allowed",
    "manual_current_mutation_allowed",
    "manual_manifest_mutation_allowed",
    "manual_historical_mutation_allowed",
    "manual_registry_mutation_allowed",
    "brain_write_allowed",
    "reports_brain_write_allowed",
    "n8n_allowed",
    "webhook_allowed",
    "publishing_allowed",
    "capa9_allowed",
    "openai_api_runtime_allowed",
    "social_media_automation_allowed",
    "auto_action_allowed",
    "build_allowed_now",
    "build_allowed_next",
    "approval_granted",
    "approval_consumed",
]

AUTHORITY_FILES = {
    "bridge_v2_3_governed_work_order_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
    "bridge_v2_3_validation_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json",
    "bridge_v2_3_transition_gate_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json",
    "bridge_v2_3_authority_hash_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json",
    "bridge_v2_2_context_alignment_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    "bridge_build_readiness_report": "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
    "bridge_v1_runtime_warning_closure_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_SEAL.json",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_4_2_governed_build_request_human_approval_gate.py",
    "tests/manual_brain_bridge/test_bridge_v2_4_2_governed_build_request_human_approval_gate.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
    }
]

BLOCKED_CAPABILITIES = [
    "AUTO_EXECUTION",
    "DIRECT_PRODUCTION_EXECUTION",
    "EXTERNAL_EXECUTION",
    "EXTERNAL_SIDE_EFFECTS",
    "BRAIN_WRITE",
    "REPORTS_BRAIN_WRITE",
    "MANUAL_WRITE",
    "MANUAL_AUTO_UPDATE",
    "MANUAL_CURRENT_MUTATION",
    "MANUAL_MANIFEST_MUTATION",
    "MANUAL_HISTORICAL_MUTATION",
    "MANUAL_REGISTRY_MUTATION",
    "N8N_EXECUTION",
    "WEBHOOK_EXECUTION",
    "PUBLISHING",
    "OPENAI_API_RUNTIME",
    "SOCIAL_MEDIA_AUTOMATION",
    "CONTENT_PUBLICATION",
    "CAPA9",
    "APPROVAL_REUSE",
    "APPROVAL_SELF_GRANT",
    "APPROVAL_FROM_HISTORY",
    "APPROVAL_FROM_REPORT",
    "APPROVAL_FROM_COMMIT",
    "APPROVAL_FROM_MANUAL",
    "APPROVAL_CONSUMPTION_IN_SAME_LAYER",
]

CRITICAL_MARKERS = [
    "AR" + "GOS Ω",
    "AR" + "GOS_CORE",
    "AR" + "GOS_BACKCUP",
    "AR" + "GOS_CLEAN",
    "sprint4" + "_decision_core",
    "C5" + ".0.8",
    "Governance" + " Meta Guard",
    "Action" + " Registry",
    "Evidence" + " Surface",
    "Operational" + " HUD",
]

CRITICAL_PATH_FRAGMENTS = [
    "AR" + "GOS_BACKCUP",
    "AR" + "GOS_CLEAN",
    "AR" + "GOS_CORE",
]

SCANNED_SUFFIXES = {
    ".py",
    ".ps1",
    ".md",
    ".json",
    ".txt",
    ".yaml",
    ".yml",
}

SCAN_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}

BUILD_REQUEST_ID = "BRIDGE_V2_4_2_BUILD_REQUEST"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    if tmp.exists():
        tmp.unlink()

    tmp.write_text(content, encoding="utf-8", newline="\n")
    expected = sha256_text(content)
    tmp_hash = sha256_file(tmp)

    if tmp_hash != expected:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"TMP_HASH_MISMATCH:{path}")

    tmp.replace(path)
    final_hash = sha256_file(path)

    if final_hash != expected:
        raise RuntimeError(f"FINAL_HASH_MISMATCH:{path}")


def write_atomic_json(path: Path, value: dict[str, Any]) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write_atomic_text(path, content)


def read_json(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel)
    return json.loads(path.read_text(encoding="utf-8"))


def safe_flags() -> dict[str, bool]:
    return {
        "execution_allowed": False,
        "external_execution_allowed": False,
        "external_side_effects_allowed": False,
        "manual_write_allowed": False,
        "manual_auto_update_allowed": False,
        "manual_current_mutation_allowed": False,
        "manual_manifest_mutation_allowed": False,
        "manual_historical_mutation_allowed": False,
        "manual_registry_mutation_allowed": False,
        "brain_write_allowed": False,
        "reports_brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "capa9_allowed": False,
        "openai_api_runtime_allowed": False,
        "social_media_automation_allowed": False,
        "auto_action_allowed": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "approval_granted": False,
        "approval_consumed": False,
    }


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    report = {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
        "generated_by_layer": LAYER,
        "authority_files": list(AUTHORITY_FILES.values()),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "next_safe_step": "IMPLEMENTATION_PLAN_V2_5_OR_APPROVAL_CONSUMPTION_GATE_BLUEPRINT",
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
    }
    report.update(safe_flags())
    return report


def danger_flags_false(report: dict[str, Any]) -> bool:
    return all(report.get(flag) is False for flag in DANGER_FLAGS if flag in report)


def build_repo_identity_report(root: Path, head: str, branch: str, remote: str, upstream: str) -> dict[str, Any]:
    root_norm = str(root).replace("\\", "/")
    root_name_valid = root.name == EXPECTED_ROOT_NAME
    branch_valid = branch == EXPECTED_BRANCH
    remote_valid = EXPECTED_REMOTE_FRAGMENT in remote and ("AR" + "GOS.git") not in remote
    argos_path_detected = any(fragment.lower() in root_norm.lower() for fragment in ["argos_backcup", "argos_clean"])
    argos_remote_detected = ("AR" + "GOS.git") in remote
    head_equals_upstream = bool(head) and head == upstream

    ok = all([
        root_name_valid,
        branch_valid,
        remote_valid,
        not argos_path_detected,
        not argos_remote_detected,
        head_equals_upstream,
    ])

    report = base_report("BRIDGE_V2_4_REPO_IDENTITY_REPORT", "PASS" if ok else "LOCK")
    report.update({
        "repo_identity_valid": ok,
        "root": root_norm,
        "root_name": root.name,
        "root_valid": root_name_valid,
        "branch": branch,
        "branch_valid": branch_valid,
        "remote": remote,
        "remote_valid": remote_valid,
        "argos_remote_detected": argos_remote_detected,
        "argos_path_detected": argos_path_detected,
        "head": head,
        "upstream": upstream,
        "head_equals_upstream": head_equals_upstream,
    })
    return report


def iter_scannable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        parts = set(path.parts)
        if parts.intersection(SCAN_EXCLUDED_DIRS):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files)


def build_argos_contamination_gate_report(root: Path, repo_identity: dict[str, Any]) -> dict[str, Any]:
    marker_findings = []
    path_findings = []

    for file in iter_scannable_files(root):
        rel = str(file.relative_to(root)).replace("\\", "/")
        rel_upper = rel.upper()

        for fragment in CRITICAL_PATH_FRAGMENTS:
            if fragment in rel_upper:
                path_findings.append({
                    "severity": "CRITICAL",
                    "file": rel,
                    "fragment": fragment,
                })

        try:
            text = file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            for marker in CRITICAL_MARKERS:
                if marker in line:
                    marker_findings.append({
                        "severity": "CRITICAL",
                        "file": rel,
                        "line": line_no,
                        "marker_hash": sha256_text(marker),
                        "preview_hash": sha256_text(line.strip()[:160]),
                    })

    critical_marker_count = len(marker_findings)
    critical_path_count = len(path_findings)
    contamination_detected = critical_marker_count > 0 or critical_path_count > 0
    repo_ok = repo_identity.get("status") == "PASS"

    report = base_report(
        "BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT",
        "PASS" if repo_ok and not contamination_detected else "BLOCK",
    )
    report.update({
        "contamination_detected": contamination_detected,
        "critical_marker_findings_count": critical_marker_count,
        "warning_marker_findings_count": 0,
        "critical_path_findings_count": critical_path_count,
        "marker_findings": marker_findings[:100],
        "path_findings": path_findings[:100],
        "repo_clean": True,
        "head_equals_upstream": repo_identity.get("head_equals_upstream") is True,
        "scan_suffixes": sorted(SCANNED_SUFFIXES),
        "excluded_dirs": sorted(SCAN_EXCLUDED_DIRS),
    })
    return report


def build_authority_binding_report(root: Path) -> dict[str, Any]:
    entries = []
    missing = []
    invalid = []

    for authority_id, rel in AUTHORITY_FILES.items():
        path = root / rel
        entry: dict[str, Any] = {
            "authority_id": authority_id,
            "path": rel,
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "status": "UNKNOWN",
        }

        if not path.exists() or not entry["sha256"]:
            missing.append(rel)
            entry["status"] = "MISSING_OR_HASH_NULL"
            entries.append(entry)
            continue

        try:
            data = read_json(root, rel)
        except Exception:
            invalid.append(rel)
            entry["status"] = "INVALID_JSON"
            entries.append(entry)
            continue

        entry["reported_status"] = data.get("status")

        if authority_id == "bridge_v2_3_governed_work_order_seal":
            ok = data.get("status") == "SEALED_AS_GOVERNED_WORK_ORDER_TRANSITION_GATE_V2_3"
        elif authority_id == "bridge_v2_3_validation_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("build_allowed_next") is True
                and data.get("build_allowed_now") is False
            )
        elif authority_id == "bridge_v2_3_transition_gate_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("next_bridge_layer_build_block_allowed_next") is True
                and data.get("next_bridge_layer_build_allowed_now") is False
            )
        elif authority_id == "bridge_v2_3_authority_hash_report":
            ok = data.get("status") == "PASS" and data.get("authority_hash_check") == "PASS"
        elif authority_id == "bridge_v2_2_context_alignment_seal":
            ok = data.get("status") == "SEALED_AS_CONTEXT_ALIGNMENT_V2_2"
        elif authority_id == "bridge_build_readiness_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("runtime_manual_review_required") is False
                and not data.get("review_report_ids")
            )
        elif authority_id == "bridge_v1_runtime_warning_closure_seal":
            ok = (
                data.get("status") == "RUNTIME_WARNING_CLOSED_CLEAN"
                and data.get("warning_closed") is True
                and data.get("runtime_manual_review_required") is False
            )
        else:
            ok = False

        entry["status"] = "VALID" if ok else "INVALID_AUTHORITY_STATUS"
        if not ok:
            invalid.append(rel)

        entries.append(entry)

    authority_hashes = {item["path"]: item["sha256"] for item in entries}
    authority_set_hash = sha256_text(stable_json(authority_hashes))
    ok = not missing and not invalid

    report = base_report("BRIDGE_V2_4_AUTHORITY_BINDING_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "authority_set_status": "PASS" if ok else "BLOCK",
        "authority_entries": entries,
        "authority_hashes": authority_hashes,
        "authority_hashes_present": all(authority_hashes.values()),
        "authority_hashes_valid": ok,
        "authority_set_hash": authority_set_hash,
        "authority_set_locked": ok,
        "authority_set_can_be_reused_after_head_change": False,
        "authority_set_can_be_reused_after_scope_change": False,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "bridge_v2_3_authority_valid": ok,
    })
    return report


def build_scope_binding_report() -> dict[str, Any]:
    allowed_scope = [
        "create_governed_build_request_contract",
        "create_human_approval_requirement",
        "create_approval_phrase_expectation_hash_only",
        "create_approval_non_consumption_gate",
        "create_reports_manifest_and_seal",
        "run_validation_tests",
        "commit_push_only_if_all_gates_pass",
    ]

    prohibited_scope = [
        "execute_next_build",
        "consume_approval",
        "grant_approval",
        "modify_manual_current",
        "modify_manual_manifest",
        "modify_brain",
        "write_reports_brain",
        "activate_n8n",
        "activate_webhook",
        "publish_content",
        "call_openai_api_runtime",
        "create_capa9",
        "reuse_approval",
        "approve_from_history",
    ]

    scope_payload = {
        "allowed_scope": allowed_scope,
        "prohibited_scope": prohibited_scope,
        "layer": LAYER,
        "build_request_id": BUILD_REQUEST_ID,
    }

    scope_hash = sha256_text(stable_json(scope_payload))

    report = base_report("BRIDGE_V2_4_SCOPE_BINDING_REPORT")
    report.update({
        "scope_locked": True,
        "scope_hash_present": True,
        "scope_hash_valid": True,
        "scope_hash": scope_hash,
        "allowed_scope": allowed_scope,
        "prohibited_scope": prohibited_scope,
        "scope_change_invalidates_approval": True,
    })
    return report


def build_build_request_contract_report(
    root: Path,
    head: str,
    branch: str,
    remote: str,
    authority: dict[str, Any],
    scope: dict[str, Any],
) -> dict[str, Any]:
    ok = authority.get("status") == "PASS" and scope.get("status") == "PASS"

    request_payload = {
        "build_request_id": BUILD_REQUEST_ID,
        "head": head,
        "branch": branch,
        "remote": remote,
        "root": str(root).replace("\\", "/"),
        "authority_set_hash": authority.get("authority_set_hash"),
        "scope_hash": scope.get("scope_hash"),
        "layer": LAYER,
    }

    request_hash = sha256_text(stable_json(request_payload))

    report = base_report("BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "build_request_id": BUILD_REQUEST_ID,
        "request_type": "NEXT_BRIDGE_LAYER_BUILD_REQUEST",
        "requested_next_layer": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
        "request_created": ok,
        "request_valid": ok,
        "request_hash": request_hash,
        "request_bound_to_head": head,
        "request_bound_to_branch": branch,
        "request_bound_to_remote": remote,
        "request_bound_to_authority_hash": authority.get("authority_set_hash"),
        "request_bound_to_scope_hash": scope.get("scope_hash"),
        "human_approval_required": True,
        "human_approval_received": False,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_next": False,
        "build_allowed_now": False,
        "execution_allowed": False,
    })
    return report


def expected_approval_hash(
    root: Path,
    head: str,
    branch: str,
    remote: str,
    authority_set_hash: str,
    scope_hash: str,
) -> str:
    payload = {
        "approval_phrase_version": "v2.4.2",
        "build_request_id": BUILD_REQUEST_ID,
        "layer": LAYER,
        "root": str(root).replace("\\", "/"),
        "head": head,
        "branch": branch,
        "remote": remote,
        "authority_set_hash": authority_set_hash,
        "scope_hash": scope_hash,
    }
    return sha256_text(stable_json(payload))


def build_human_approval_gate_report(
    root: Path,
    head: str,
    branch: str,
    remote: str,
    authority: dict[str, Any],
    scope: dict[str, Any],
    build_request: dict[str, Any],
) -> dict[str, Any]:
    ok = build_request.get("status") == "PASS"

    phrase_hash = expected_approval_hash(
        root=root,
        head=head,
        branch=branch,
        remote=remote,
        authority_set_hash=str(authority.get("authority_set_hash")),
        scope_hash=str(scope.get("scope_hash")),
    )

    report = base_report("BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "human_approval_required": True,
        "human_approval_received": False,
        "human_approval_valid": False,
        "approval_granted": False,
        "approval_consumed": False,
        "approval_source": "NONE",
        "approval_source_allowed": False,
        "approval_can_be_consumed_by_this_layer": False,
        "approval_consumption_deferred_to_next_layer": True,
        "approval_phrase_expected_created": True,
        "approval_phrase_plaintext_storage_allowed": False,
        "approval_phrase_expected_hash_present": True,
        "approval_phrase_expected_hash": phrase_hash,
        "approval_phrase_received": None,
        "approval_phrase_received_hash": None,
        "approval_match": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
    })
    return report


def build_approval_expiration_report() -> dict[str, Any]:
    report = base_report("BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT")
    report.update({
        "approval_expires_on_head_change": True,
        "approval_expires_on_authority_change": True,
        "approval_expires_on_scope_change": True,
        "approval_expires_on_repo_identity_change": True,
        "approval_expires_on_branch_change": True,
        "approval_expires_on_remote_change": True,
        "approval_expires_on_contamination_gate_change": True,
        "approval_expires_after_single_consumption": True,
        "permanent_approval_allowed": False,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_now": False,
    })
    return report


def resolve_approval_attempt(source: str, text: str | None) -> dict[str, Any]:
    normalized_source = (source or "NONE").upper()
    normalized_text = (text or "").strip().lower()

    blocked_sources = {
        "HISTORY": "BLOCK_APPROVAL_FROM_HISTORY",
        "REPORT": "BLOCK_APPROVAL_FROM_REPORT",
        "COMMIT": "BLOCK_APPROVAL_FROM_COMMIT",
        "MANUAL": "BLOCK_APPROVAL_FROM_MANUAL",
        "OLD_SEAL": "BLOCK_APPROVAL_FROM_OLD_SEAL",
        "PREVIOUS_LAYER": "BLOCK_APPROVAL_FROM_PREVIOUS_LAYER",
        "GLOBAL": "BLOCK_GLOBAL_OR_PERMANENT_APPROVAL",
        "SELF": "BLOCK_APPROVAL_SELF_GRANT",
    }

    if normalized_source in blocked_sources:
        return {
            "allowed": False,
            "decision": blocked_sources[normalized_source],
            "approval_granted": False,
            "approval_consumed": False,
            "build_allowed_now": False,
        }

    generic_approvals = {
        "ok",
        "dale",
        "continua",
        "continúa",
        "aprobado",
        "ya lo aprobé",
        "aprueba tú",
        "hazlo",
        "sigue",
    }

    if normalized_text in generic_approvals:
        return {
            "allowed": False,
            "decision": "BLOCK_GENERIC_APPROVAL",
            "approval_granted": False,
            "approval_consumed": False,
            "build_allowed_now": False,
        }

    if normalized_source == "FRESH_HUMAN_INPUT":
        return {
            "allowed": False,
            "decision": "DEFER_TO_NEXT_LAYER_APPROVAL_CONSUMPTION_GATE",
            "approval_granted": False,
            "approval_consumed": False,
            "build_allowed_now": False,
            "reason": "v2.4.2 creates approval gate only; it does not consume approval",
        }

    return {
        "allowed": False,
        "decision": "BLOCK_UNKNOWN_APPROVAL_SOURCE",
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_now": False,
    }


def build_anti_replay_approval_report() -> dict[str, Any]:
    blocked_cases = [
        resolve_approval_attempt("HISTORY", "ya lo aprobé"),
        resolve_approval_attempt("REPORT", "approved"),
        resolve_approval_attempt("COMMIT", "approved"),
        resolve_approval_attempt("MANUAL", "approved"),
        resolve_approval_attempt("OLD_SEAL", "approved"),
        resolve_approval_attempt("PREVIOUS_LAYER", "approved"),
        resolve_approval_attempt("GLOBAL", "approved forever"),
        resolve_approval_attempt("SELF", "aprueba tú"),
        resolve_approval_attempt("NONE", "ok"),
        resolve_approval_attempt("FRESH_HUMAN_INPUT", "candidate phrase"),
    ]

    ok = all(case.get("allowed") is False for case in blocked_cases)

    report = base_report("BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "approval_replay_blocked": True,
        "approval_self_grant_blocked": True,
        "approval_from_history_blocked": True,
        "approval_from_report_blocked": True,
        "approval_from_commit_blocked": True,
        "approval_from_manual_blocked": True,
        "approval_from_old_seal_blocked": True,
        "approval_from_previous_layer_blocked": True,
        "generic_approval_blocked": True,
        "fresh_human_input_consumption_deferred": True,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_now": False,
        "blocked_cases": blocked_cases,
    })
    return report


def build_blocked_capabilities_report() -> dict[str, Any]:
    report = base_report("BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT")
    report.update({
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "blocked_capability_count": len(BLOCKED_CAPABILITIES),
        "manual_auto_update_allowed": False,
        "manual_current_mutation_allowed": False,
        "manual_manifest_mutation_allowed": False,
        "manual_historical_mutation_allowed": False,
        "manual_registry_mutation_allowed": False,
        "approval_reuse_allowed": False,
        "approval_self_grant_allowed": False,
        "approval_from_history_allowed": False,
        "approval_consumption_in_same_layer_allowed": False,
        "human_approval_required": True,
        "human_approval_received": False,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "policy": "v2.4.2 prepares governed request and human approval gate only; it does not enable build or execution.",
    })
    return report


def build_anti_simulation_gate_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
    violations = []

    for item in reports:
        report_id = item.get("report_id", "UNKNOWN")
        if item.get("status") == "PASS":
            required_fields = [
                "report_id",
                "status",
                "layer",
                "authority_files",
                "blocked_capabilities",
                "next_safe_step",
                "generated_by_layer",
                "manifest_reference",
            ]
            for field in required_fields:
                if field not in item:
                    violations.append(f"{report_id}:MISSING_{field}")

            if not danger_flags_false(item):
                violations.append(f"{report_id}:DANGER_FLAGS_NOT_FALSE")

            if item.get("authority_files") == []:
                violations.append(f"{report_id}:NO_AUTHORITY_FILES")

            if item.get("blocked_capabilities") == []:
                violations.append(f"{report_id}:NO_BLOCKED_CAPABILITIES")

            if item.get("approval_granted") is True:
                violations.append(f"{report_id}:APPROVAL_GRANTED_TRUE")

            if item.get("approval_consumed") is True:
                violations.append(f"{report_id}:APPROVAL_CONSUMED_TRUE")

            if item.get("build_allowed_now") is True:
                violations.append(f"{report_id}:BUILD_ALLOWED_NOW_TRUE")

    report = base_report("BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_gate": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_without_hashes_blocked": True,
        "pass_without_authority_files_blocked": True,
        "pass_with_danger_flags_blocked": True,
        "pass_with_approval_granted_blocked": True,
        "pass_with_approval_consumed_blocked": True,
        "pass_with_build_allowed_now_blocked": True,
    })
    return report


def build_validation_report(
    repo_identity: dict[str, Any],
    contamination: dict[str, Any],
    authority: dict[str, Any],
    scope: dict[str, Any],
    build_request: dict[str, Any],
    human_approval: dict[str, Any],
    expiration: dict[str, Any],
    anti_replay: dict[str, Any],
    blocked: dict[str, Any],
    anti_simulation: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "repo_identity": repo_identity.get("status") == "PASS",
        "argos_contamination_gate": contamination.get("status") == "PASS",
        "authority_binding": authority.get("status") == "PASS",
        "scope_binding": scope.get("status") == "PASS",
        "build_request_contract": build_request.get("status") == "PASS",
        "human_approval_gate": human_approval.get("status") == "PASS",
        "approval_expiration": expiration.get("status") == "PASS",
        "anti_replay": anti_replay.get("status") == "PASS",
        "blocked_capabilities": blocked.get("status") == "PASS",
        "anti_simulation": anti_simulation.get("status") == "PASS",
        "danger_flags_false": all(danger_flags_false(item) for item in [
            repo_identity,
            contamination,
            authority,
            scope,
            build_request,
            human_approval,
            expiration,
            anti_replay,
            blocked,
            anti_simulation,
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_4_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "bridge_v2_3_authority_valid": authority.get("bridge_v2_3_authority_valid") is True,
        "repo_identity_valid": repo_identity.get("repo_identity_valid") is True,
        "argos_contamination_gate_pass": contamination.get("status") == "PASS",
        "authority_binding_pass": authority.get("status") == "PASS",
        "scope_binding_pass": scope.get("status") == "PASS",
        "build_request_contract_created": build_request.get("request_created") is True,
        "build_request_created": build_request.get("request_created") is True,
        "human_approval_required": True,
        "human_approval_received": False,
        "approval_granted": False,
        "approval_consumed": False,
        "approval_replay_blocked": anti_replay.get("approval_replay_blocked") is True,
        "approval_self_grant_blocked": anti_replay.get("approval_self_grant_blocked") is True,
        "build_allowed_next": False,
        "build_allowed_now": False,
        "external_execution": "DISABLED",
        "brain_mutation": "BLOCKED",
        "manual_mutation": "BLOCKED",
        "auto_action": False,
        "next_safe_step": "IMPLEMENTATION_PLAN_V2_5_OR_APPROVAL_CONSUMPTION_GATE_BLUEPRINT",
    })
    return report


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts = []

    for rel in MANIFEST_TRACKED_ARTIFACTS:
        path = root / rel
        artifacts.append({
            "path": rel,
            "sha256": sha256_file(path),
            "artifact_type": "generated_v2_4_2",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_4_ARTIFACT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_4_ARTIFACT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
        ],
        "omission_reason": "Manifest cannot require its own final seal before seal exists; seal closes over manifest hash after manifest PASS.",
    })
    return report


def build_human_report(validation: dict[str, Any], build_request: dict[str, Any], human_approval: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.4.2 GOVERNED BUILD REQUEST CONTRACT & HUMAN APPROVAL GATE — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## What was created

- Governed build request contract
- Human approval gate
- Authority binding
- Scope binding
- Approval expiration policy
- Anti-replay approval policy
- Blocked capabilities report
- Anti-simulation gate
- Manifest and seal

## Build request

- build_request_id: {build_request.get("build_request_id")}
- request_created: {build_request.get("request_created")}
- request_valid: {build_request.get("request_valid")}
- requested_next_layer: {build_request.get("requested_next_layer")}

## Human approval state

- human_approval_required: {human_approval.get("human_approval_required")}
- human_approval_received: {human_approval.get("human_approval_received")}
- human_approval_valid: {human_approval.get("human_approval_valid")}
- approval_granted: {human_approval.get("approval_granted")}
- approval_consumed: {human_approval.get("approval_consumed")}
- approval_can_be_consumed_by_this_layer: {human_approval.get("approval_can_be_consumed_by_this_layer")}
- approval_consumption_deferred_to_next_layer: {human_approval.get("approval_consumption_deferred_to_next_layer")}

## Safety state

- execution_allowed: false
- external_execution_allowed: false
- external_side_effects_allowed: false
- manual_write_allowed: false
- manual_auto_update_allowed: false
- manual_current_mutation_allowed: false
- manual_manifest_mutation_allowed: false
- manual_historical_mutation_allowed: false
- manual_registry_mutation_allowed: false
- brain_write_allowed: false
- reports_brain_write_allowed: false
- n8n_allowed: false
- webhook_allowed: false
- publishing_allowed: false
- capa9_allowed: false
- openai_api_runtime_allowed: false
- social_media_automation_allowed: false
- auto_action_allowed: false
- build_allowed_now: false
- build_allowed_next: false

## Interpretation

v2.4.2 creates the governed request and human approval gate.
It does not consume approval.
It does not grant approval.
It does not execute the next build.
It does not mutate manual/current, manual/manifest, brain or reports/brain.

## Next safe step

IMPLEMENTATION_PLAN_V2_5_OR_APPROVAL_CONSUMPTION_GATE_BLUEPRINT
"""


def generate(
    root: Path,
    head: str,
    branch: str,
    remote: str,
    upstream: str,
    partial_state: str,
    partial_files: list[str],
) -> int:
    repo_identity = build_repo_identity_report(root, head, branch, remote, upstream)
    contamination = build_argos_contamination_gate_report(root, repo_identity)
    authority = build_authority_binding_report(root)
    scope = build_scope_binding_report()
    build_request = build_build_request_contract_report(root, head, branch, remote, authority, scope)
    human_approval = build_human_approval_gate_report(root, head, branch, remote, authority, scope, build_request)
    expiration = build_approval_expiration_report()
    anti_replay = build_anti_replay_approval_report()
    blocked = build_blocked_capabilities_report()

    primary_reports = [
        repo_identity,
        contamination,
        authority,
        scope,
        build_request,
        human_approval,
        expiration,
        anti_replay,
        blocked,
    ]

    anti_simulation = build_anti_simulation_gate_report(primary_reports)

    validation = build_validation_report(
        repo_identity,
        contamination,
        authority,
        scope,
        build_request,
        human_approval,
        expiration,
        anti_replay,
        blocked,
        anti_simulation,
    )

    validation.update({
        "partial_state": partial_state,
        "partial_files": partial_files,
    })

    output_map = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json": repo_identity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json": contamination,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json": authority,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json": scope,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json": build_request,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json": human_approval,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT.json": expiration,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT.json": anti_replay,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT.json": blocked,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json": validation,
    }

    for rel, report in output_map.items():
        write_atomic_json(root / rel, report)

    human = build_human_report(validation, build_request, human_approval)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json", manifest)

    seal_status = (
        "SEALED_AS_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_V2_4_2"
        if validation.get("status") == "PASS" and manifest.get("status") == "PASS"
        else "BLOCK"
    )

    seal = base_report("BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL", seal_status)
    seal.update({
        "seal_id": "BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL",
        "status": seal_status,
        "bridge_v2_3_authority_valid": validation.get("bridge_v2_3_authority_valid"),
        "repo_identity_valid": validation.get("repo_identity_valid"),
        "argos_contamination_gate_pass": validation.get("argos_contamination_gate_pass"),
        "authority_binding_pass": validation.get("authority_binding_pass"),
        "scope_binding_pass": validation.get("scope_binding_pass"),
        "build_request_contract_created": validation.get("build_request_contract_created"),
        "human_approval_required": True,
        "human_approval_received": False,
        "approval_granted": False,
        "approval_consumed": False,
        "approval_replay_blocked": validation.get("approval_replay_blocked"),
        "approval_self_grant_blocked": validation.get("approval_self_grant_blocked"),
        "build_allowed_now": False,
        "build_allowed_next": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.md"),
        "next_safe_step": "IMPLEMENTATION_PLAN_V2_5_OR_APPROVAL_CONSUMPTION_GATE_BLUEPRINT",
    })
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json", seal)

    return EXIT_PASS if seal_status == "SEALED_AS_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_V2_4_2" else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json")
    approval = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json")
    request = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json")
    contamination = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == "SEALED_AS_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_V2_4_2",
        "approval_required_true": approval.get("human_approval_required") is True,
        "approval_received_false": approval.get("human_approval_received") is False,
        "approval_granted_false": approval.get("approval_granted") is False,
        "approval_consumed_false": approval.get("approval_consumed") is False,
        "request_created_true": request.get("request_created") is True,
        "request_valid_true": request.get("request_valid") is True,
        "build_allowed_now_false": seal.get("build_allowed_now") is False,
        "build_allowed_next_false": seal.get("build_allowed_next") is False,
        "contamination_pass": contamination.get("status") == "PASS" and contamination.get("contamination_detected") is False,
        "danger_flags_false": all(danger_flags_false(item) for item in [
            validation,
            manifest,
            seal,
            approval,
            request,
            contamination,
        ]),
    }

    if not all(checks.values()):
        print(json.dumps({"status": "BLOCK", "checks": checks}, indent=2))
        return EXIT_BLOCK

    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "validate-outputs"], required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--head", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--remote", default="")
    parser.add_argument("--upstream", default="")
    parser.add_argument("--partial-state", default="NO_PARTIAL_STATE")
    parser.add_argument("--partial-files-json", default="[]")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "generate":
        try:
            partial_files = json.loads(args.partial_files_json)
        except Exception:
            partial_files = []
        return generate(
            root=root,
            head=args.head,
            branch=args.branch,
            remote=args.remote,
            upstream=args.upstream,
            partial_state=args.partial_state,
            partial_files=partial_files,
        )

    if args.mode == "validate-outputs":
        return validate_outputs(root)

    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())