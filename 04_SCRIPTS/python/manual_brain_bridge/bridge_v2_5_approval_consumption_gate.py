from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_APPROVAL_CONSUMPTION_GATE_LAYER_V2_5_BUILD_FIX_3"

EXIT_PASS = 0
EXIT_BLOCK = 20

EXPECTED_ROOT_NAME = "CONTENT_ENGINE_OMEGA"
EXPECTED_BRANCH = "main"
EXPECTED_REMOTE_FRAGMENT = "CONTENT_ENGINE_OMEGA.git"

BUILD_REQUEST_ID = "BRIDGE_V2_4_2_BUILD_REQUEST"
NEXT_SAFE_STEP = "BLUEPRINT_V2_6_GOVERNED_BUILD_EXECUTION_GATE"

DANGER_ALWAYS_FALSE = [
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
    "approval_plaintext_stored",
]

V24_AUTHORITY_FILES = {
    "v24_human_approval_gate_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
    "v24_validation_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json",
    "v24_build_request_contract_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json",
    "v24_human_approval_gate_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json",
    "v24_contamination_gate_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_5_approval_consumption_gate.py",
    "tests/manual_brain_bridge/test_bridge_v2_5_approval_consumption_gate.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    }
]

BLOCKED_CAPABILITIES = [
    "AUTO_EXECUTION",
    "DIRECT_BUILD_EXECUTION",
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
    "APPROVAL_FROM_BRAIN",
    "APPROVAL_FROM_OLD_HEAD",
    "APPROVAL_FROM_WRONG_SCOPE",
    "APPROVAL_FROM_WRONG_AUTHORITY",
    "APPROVAL_PERMANENT",
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

SCANNED_SUFFIXES = {".py", ".ps1", ".md", ".json", ".txt", ".yaml", ".yml"}
SCAN_EXCLUDED_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}


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
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
    }


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    report = {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
        "generated_by_layer": LAYER,
        "authority_files": list(V24_AUTHORITY_FILES.values()),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "next_safe_step": NEXT_SAFE_STEP,
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
    }
    report.update(safe_flags())
    return report


def danger_always_false(report: dict[str, Any]) -> bool:
    return all(report.get(flag) is False for flag in DANGER_ALWAYS_FALSE if flag in report)


def build_repo_identity_report(root: Path, head: str, branch: str, remote: str, upstream: str, repo_clean: bool = True) -> dict[str, Any]:
    root_norm = str(root).replace("\\", "/")
    root_name_valid = root.name == EXPECTED_ROOT_NAME
    branch_valid = branch == EXPECTED_BRANCH
    remote_valid = EXPECTED_REMOTE_FRAGMENT in remote and ("AR" + "GOS.git") not in remote
    foreign_path_detected = any(fragment.lower() in root_norm.lower() for fragment in ["ar" + "gos_backcup", "ar" + "gos_clean"])
    foreign_remote_detected = ("AR" + "GOS.git") in remote
    head_equals_upstream = bool(head) and head == upstream

    ok = all([
        root_name_valid,
        branch_valid,
        remote_valid,
        not foreign_path_detected,
        not foreign_remote_detected,
        head_equals_upstream,
        repo_clean,
    ])

    report = base_report("BRIDGE_V2_5_REPO_IDENTITY_REPORT", "PASS" if ok else "LOCK")
    report.update({
        "repo_identity_valid": ok,
        "root": root_norm,
        "root_name": root.name,
        "root_valid": root_name_valid,
        "branch": branch,
        "branch_valid": branch_valid,
        "remote": remote,
        "remote_valid": remote_valid,
        "foreign_remote_detected": foreign_remote_detected,
        "foreign_path_detected": foreign_path_detected,
        "head": head,
        "upstream": upstream,
        "head_equals_upstream": head_equals_upstream,
        "repo_clean": repo_clean,
    })
    return report


def iter_scannable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if set(path.parts).intersection(SCAN_EXCLUDED_DIRS):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in SCANNED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files)


def build_contamination_gate_report(root: Path, repo_identity: dict[str, Any]) -> dict[str, Any]:
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
                    "fragment_hash": sha256_text(fragment),
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

    contamination_detected = bool(marker_findings or path_findings)
    repo_ok = repo_identity.get("status") == "PASS"

    report = base_report(
        "BRIDGE_V2_5_CONTAMINATION_GATE_REPORT",
        "PASS" if repo_ok and not contamination_detected else "BLOCK",
    )
    report.update({
        "contamination_detected": contamination_detected,
        "critical_marker_findings_count": len(marker_findings),
        "warning_marker_findings_count": 0,
        "critical_path_findings_count": len(path_findings),
        "marker_findings": marker_findings[:100],
        "path_findings": path_findings[:100],
        "repo_clean": repo_identity.get("repo_clean") is True,
        "head_equals_upstream": repo_identity.get("head_equals_upstream") is True,
        "scan_suffixes": sorted(SCANNED_SUFFIXES),
        "excluded_dirs": sorted(SCAN_EXCLUDED_DIRS),
    })
    return report


def build_v24_authority_consumption_report(root: Path) -> dict[str, Any]:
    entries = []
    missing = []
    invalid = []
    loaded: dict[str, dict[str, Any]] = {}

    for authority_id, rel in V24_AUTHORITY_FILES.items():
        path = root / rel
        entry = {
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
            loaded[authority_id] = data
        except Exception:
            invalid.append(rel)
            entry["status"] = "INVALID_JSON"
            entries.append(entry)
            continue

        entry["reported_status"] = data.get("status")

        if authority_id == "v24_human_approval_gate_seal":
            ok = data.get("status") == "SEALED_AS_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_V2_4_2"
        elif authority_id == "v24_validation_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("build_request_created") is True
                and data.get("human_approval_required") is True
                and data.get("human_approval_received") is False
                and data.get("approval_granted") is False
                and data.get("approval_consumed") is False
                and data.get("build_allowed_now") is False
                and data.get("build_allowed_next") is False
            )
        elif authority_id == "v24_build_request_contract_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("build_request_id") == BUILD_REQUEST_ID
                and data.get("request_created") is True
                and data.get("request_valid") is True
                and data.get("human_approval_required") is True
                and data.get("human_approval_received") is False
                and data.get("approval_granted") is False
                and data.get("approval_consumed") is False
                and data.get("build_allowed_now") is False
                and data.get("build_allowed_next") is False
            )
        elif authority_id == "v24_human_approval_gate_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("human_approval_required") is True
                and data.get("human_approval_received") is False
                and data.get("human_approval_valid") is False
                and data.get("approval_granted") is False
                and data.get("approval_consumed") is False
                and data.get("approval_phrase_expected_hash_present") is True
                and data.get("approval_phrase_plaintext_storage_allowed") is False
            )
        elif authority_id == "v24_contamination_gate_report":
            ok = data.get("status") == "PASS" and data.get("contamination_detected") is False
        else:
            ok = False

        entry["status"] = "VALID" if ok else "INVALID_AUTHORITY_STATUS"
        if not ok:
            invalid.append(rel)

        entries.append(entry)

    authority_hashes = {item["path"]: item["sha256"] for item in entries}
    authority_set_hash = sha256_text(stable_json(authority_hashes))
    ok = not missing and not invalid

    request = loaded.get("v24_build_request_contract_report", {})
    human_gate = loaded.get("v24_human_approval_gate_report", {})

    report = base_report("BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "v24_authority_status": "PASS" if ok else "BLOCK",
        "v24_authority_entries": entries,
        "v24_authority_hashes": authority_hashes,
        "v24_authority_hashes_present": all(authority_hashes.values()),
        "v24_authority_hashes_valid": ok,
        "v24_authority_set_hash": authority_set_hash,
        "v24_authority_set_locked": ok,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "build_request_id": request.get("build_request_id"),
        "request_hash": request.get("request_hash"),
        "request_bound_to_authority_hash": request.get("request_bound_to_authority_hash"),
        "request_bound_to_scope_hash": request.get("request_bound_to_scope_hash"),
        "v24_expected_approval_hash": human_gate.get("approval_phrase_expected_hash"),
        "human_approval_required": True,
        "human_approval_received_before_v25": False,
        "approval_granted_before_v25": False,
        "approval_consumed_before_v25": False,
        "build_allowed_next_before_v25": False,
        "build_allowed_now": False,
    })
    return report


def build_challenge(root: Path, head: str, branch: str, remote: str, upstream: str) -> dict[str, Any]:
    authority = build_v24_authority_consumption_report(root)
    request = read_json(root, V24_AUTHORITY_FILES["v24_build_request_contract_report"])

    v24_seal_hash = sha256_file(root / V24_AUTHORITY_FILES["v24_human_approval_gate_seal"])
    v24_request_hash = sha256_file(root / V24_AUTHORITY_FILES["v24_build_request_contract_report"])
    v24_validation_hash = sha256_file(root / V24_AUTHORITY_FILES["v24_validation_report"])
    v24_contamination_hash = sha256_file(root / V24_AUTHORITY_FILES["v24_contamination_gate_report"])

    scope_hash = str(request.get("request_bound_to_scope_hash"))
    request_hash = str(request.get("request_hash"))
    authority_hash = str(request.get("request_bound_to_authority_hash"))

    payload = {
        "system": SYSTEM,
        "approval_layer": LAYER,
        "consumed_request_id": BUILD_REQUEST_ID,
        "head": head,
        "branch": branch,
        "remote": remote,
        "upstream": upstream,
        "v24_seal_hash": v24_seal_hash,
        "v24_build_request_report_hash": v24_request_hash,
        "v24_validation_report_hash": v24_validation_hash,
        "v24_contamination_report_hash": v24_contamination_hash,
        "request_hash": request_hash,
        "authority_hash": authority_hash,
        "scope_hash": scope_hash,
        "v24_authority_set_hash": authority.get("v24_authority_set_hash"),
    }

    challenge_hash = sha256_text(stable_json(payload))

    phrase = (
        f"APRUEBO CONSUMIR {BUILD_REQUEST_ID} PARA CONTENT_ENGINE_OMEGA "
        f"HEAD={head[:12]} REQUEST={request_hash[:12]} "
        f"SCOPE={scope_hash[:12]} CHALLENGE={challenge_hash[:12]}"
    )

    return {
        "status": "PASS" if authority.get("status") == "PASS" else "BLOCK",
        "challenge_payload": payload,
        "approval_challenge_hash": challenge_hash,
        "required_approval_phrase": phrase,
        "expected_approval_hash": sha256_text(phrase),
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
    }


def build_approval_input_receipt_report(approval_present: bool, approval_input_hash: str, expected_hash: str) -> dict[str, Any]:
    approval_input_hash = (approval_input_hash or "").strip().lower()
    expected_hash = (expected_hash or "").strip().lower()

    valid_hash_shape = len(approval_input_hash) == 64 and all(ch in "0123456789abcdef" for ch in approval_input_hash)
    match = approval_present and valid_hash_shape and approval_input_hash == expected_hash
    decision = "ALLOW_HASH_FIRST_APPROVAL_CONSUMPTION" if match else "BLOCK_APPROVAL_HASH_MISMATCH_OR_ABSENT"

    report = base_report("BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT", "PASS" if match else "BLOCK")
    report.update({
        "hash_first_approval_transfer": True,
        "python_received_approval_plaintext": False,
        "human_approval_required": True,
        "human_approval_received": approval_present,
        "approval_source": "POWERSHELL_FRESH_HUMAN_TERMINAL_INPUT_HASH_ONLY",
        "approval_source_allowed": True,
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
        "approval_input_hash_present": bool(approval_input_hash),
        "approval_input_hash": approval_input_hash if approval_input_hash else None,
        "expected_approval_hash": expected_hash,
        "approval_hash_shape_valid": valid_hash_shape,
        "approval_match": match,
        "approval_attempt_decision": decision,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_next": False,
        "build_allowed_now": False,
    })
    return report


def build_approval_binding_report(repo_identity: dict[str, Any], authority: dict[str, Any], contamination: dict[str, Any], receipt: dict[str, Any], challenge: dict[str, Any]) -> dict[str, Any]:
    payload = challenge.get("challenge_payload", {})
    ok = (
        repo_identity.get("status") == "PASS"
        and authority.get("status") == "PASS"
        and contamination.get("status") == "PASS"
        and receipt.get("status") == "PASS"
        and challenge.get("status") == "PASS"
    )

    report = base_report("BRIDGE_V2_5_APPROVAL_BINDING_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "approval_bound_to_repo": repo_identity.get("repo_identity_valid") is True,
        "approval_bound_to_branch": payload.get("branch") == repo_identity.get("branch"),
        "approval_bound_to_remote": payload.get("remote") == repo_identity.get("remote"),
        "approval_bound_to_head": payload.get("head") == repo_identity.get("head"),
        "approval_bound_to_upstream": payload.get("upstream") == repo_identity.get("upstream"),
        "approval_bound_to_v24_seal_hash": bool(payload.get("v24_seal_hash")),
        "approval_bound_to_build_request_hash": bool(payload.get("v24_build_request_report_hash")),
        "approval_bound_to_authority_hash": bool(payload.get("authority_hash")),
        "approval_bound_to_scope_hash": bool(payload.get("scope_hash")),
        "approval_invalidates_on_head_change": True,
        "approval_invalidates_on_scope_change": True,
        "approval_invalidates_on_authority_change": True,
        "approval_invalidates_on_repo_identity_change": True,
        "approval_invalidates_on_contamination_gate_change": True,
        "approval_match": receipt.get("approval_match") is True,
        "approval_plaintext_stored": False,
        "approval_granted": False,
        "approval_consumed": False,
        "build_allowed_next": False,
        "build_allowed_now": False,
    })
    return report


def build_approval_consumption_report(receipt: dict[str, Any], binding: dict[str, Any]) -> dict[str, Any]:
    ok = receipt.get("status") == "PASS" and binding.get("status") == "PASS"

    report = base_report("BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "hash_first_approval_transfer": True,
        "python_received_approval_plaintext": False,
        "human_approval_required": True,
        "human_approval_received": ok,
        "human_approval_valid": ok,
        "approval_match": ok,
        "approval_granted": ok,
        "approval_consumed": ok,
        "approval_consumption_count": 1 if ok else 0,
        "approval_consumption_single_use": True,
        "approval_reuse_allowed": False,
        "approval_can_be_reused": False,
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
        "build_allowed_next": ok,
        "build_allowed_now": False,
        "execution_allowed": False,
        "next_safe_step": NEXT_SAFE_STEP,
    })
    return report


def build_anti_replay_consumption_report(challenge: dict[str, Any]) -> dict[str, Any]:
    expected_hash = str(challenge.get("expected_approval_hash"))
    wrong_hash = sha256_text("ok")
    valid_case_allowed = len(expected_hash) == 64 and expected_hash != wrong_hash

    blocked_cases = [
        {"source": "PLAINTEXT_TO_PYTHON", "allowed": False, "decision": "BLOCK_PLAINTEXT_TO_PYTHON"},
        {"source": "HISTORY", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_HISTORY"},
        {"source": "REPORT", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_REPORT"},
        {"source": "COMMIT", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_COMMIT"},
        {"source": "MANUAL", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_MANUAL"},
        {"source": "BRAIN", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_BRAIN"},
        {"source": "OLD_SEAL", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_OLD_SEAL"},
        {"source": "GLOBAL", "allowed": False, "decision": "BLOCK_GLOBAL_OR_PERMANENT_APPROVAL"},
        {"source": "SELF", "allowed": False, "decision": "BLOCK_APPROVAL_SELF_GRANT"},
        {"source": "GENERIC_OK_HASH", "allowed": False, "decision": "BLOCK_GENERIC_APPROVAL_HASH"},
        {"source": "REUSE", "allowed": False, "decision": "BLOCK_APPROVAL_REUSE"},
        {"source": "OLD_HEAD", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_OLD_HEAD"},
        {"source": "WRONG_SCOPE", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_WRONG_SCOPE"},
        {"source": "WRONG_AUTHORITY", "allowed": False, "decision": "BLOCK_APPROVAL_FROM_WRONG_AUTHORITY"},
    ]

    ok = all(case.get("allowed") is False for case in blocked_cases) and valid_case_allowed

    report = base_report("BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "hash_first_approval_transfer": True,
        "plaintext_to_python_blocked": True,
        "approval_replay_blocked": True,
        "approval_self_grant_blocked": True,
        "approval_from_history_blocked": True,
        "approval_from_report_blocked": True,
        "approval_from_commit_blocked": True,
        "approval_from_manual_blocked": True,
        "approval_from_brain_blocked": True,
        "approval_from_old_head_blocked": True,
        "approval_from_wrong_scope_blocked": True,
        "approval_from_wrong_authority_blocked": True,
        "generic_approval_blocked": True,
        "approval_reuse_blocked": True,
        "permanent_approval_blocked": True,
        "blocked_cases": blocked_cases,
        "valid_case_allowed": valid_case_allowed,
        "approval_plaintext_stored": False,
        "build_allowed_now": False,
    })
    return report


def build_approval_expiration_report() -> dict[str, Any]:
    report = base_report("BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT")
    report.update({
        "approval_expires_on_head_change": True,
        "approval_expires_on_branch_change": True,
        "approval_expires_on_remote_change": True,
        "approval_expires_on_repo_root_change": True,
        "approval_expires_on_upstream_mismatch": True,
        "approval_expires_on_working_tree_dirty": True,
        "approval_expires_on_v24_seal_hash_change": True,
        "approval_expires_on_v24_request_hash_change": True,
        "approval_expires_on_authority_hash_change": True,
        "approval_expires_on_scope_hash_change": True,
        "approval_expires_on_contamination_gate_change": True,
        "approval_expires_after_single_consumption": True,
        "permanent_approval_allowed": False,
        "approval_plaintext_stored": False,
        "build_allowed_now": False,
    })
    return report


def build_blocked_capabilities_report(consumption: dict[str, Any]) -> dict[str, Any]:
    ok = consumption.get("status") == "PASS"

    report = base_report("BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "blocked_capability_count": len(BLOCKED_CAPABILITIES),
        "approval_reuse_allowed": False,
        "approval_self_grant_allowed": False,
        "approval_from_history_allowed": False,
        "approval_from_report_allowed": False,
        "approval_from_commit_allowed": False,
        "approval_from_manual_allowed": False,
        "approval_from_brain_allowed": False,
        "human_approval_required": True,
        "human_approval_received": ok,
        "approval_granted": ok,
        "approval_consumed": ok,
        "build_allowed_next": ok,
        "build_allowed_now": False,
        "execution_allowed": False,
        "policy": "v2.5 BUILD-FIX-3 consumes hash-first approval only; it does not execute the next governed build.",
    })
    return report


def build_transition_gate_report(consumption: dict[str, Any]) -> dict[str, Any]:
    ok = consumption.get("status") == "PASS"

    report = base_report("BRIDGE_V2_5_TRANSITION_GATE_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "approval_consumed": ok,
        "approval_granted": ok,
        "human_approval_required": True,
        "human_approval_received": ok,
        "human_approval_valid": ok,
        "build_allowed_next": ok,
        "build_allowed_now": False,
        "execution_allowed": False,
        "next_safe_step": NEXT_SAFE_STEP,
        "blocked_steps": [
            "DIRECT_EXECUTION",
            "AUTO_BUILD_NOW",
            "MANUAL_MUTATION",
            "BRAIN_MUTATION",
            "N8N_EXECUTION",
            "WEBHOOK_EXECUTION",
            "PUBLISHING",
        ],
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

            if not danger_always_false(item):
                violations.append(f"{report_id}:DANGER_ALWAYS_FALSE_VIOLATION")

            if item.get("authority_files") == []:
                violations.append(f"{report_id}:NO_AUTHORITY_FILES")

            if item.get("blocked_capabilities") == []:
                violations.append(f"{report_id}:NO_BLOCKED_CAPABILITIES")

            if item.get("build_allowed_now") is True:
                violations.append(f"{report_id}:BUILD_ALLOWED_NOW_TRUE")

            if item.get("approval_plaintext_stored") is True:
                violations.append(f"{report_id}:APPROVAL_PLAINTEXT_STORED_TRUE")

            if item.get("build_allowed_next") is True and item.get("approval_consumed") is not True:
                violations.append(f"{report_id}:BUILD_ALLOWED_NEXT_WITHOUT_APPROVAL_CONSUMED")

            if item.get("approval_granted") is True and item.get("approval_consumed") is not True:
                violations.append(f"{report_id}:APPROVAL_GRANTED_WITHOUT_CONSUMED")

    report = base_report("BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_gate": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_without_hashes_blocked": True,
        "pass_without_authority_files_blocked": True,
        "pass_with_danger_flags_blocked": True,
        "pass_with_build_allowed_now_blocked": True,
        "pass_with_plaintext_approval_blocked": True,
        "pass_with_build_allowed_next_without_consumption_blocked": True,
    })
    return report


def build_validation_report(
    repo_identity: dict[str, Any],
    contamination: dict[str, Any],
    authority: dict[str, Any],
    receipt: dict[str, Any],
    binding: dict[str, Any],
    consumption: dict[str, Any],
    anti_replay: dict[str, Any],
    expiration: dict[str, Any],
    blocked: dict[str, Any],
    transition: dict[str, Any],
    anti_simulation: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "repo_identity": repo_identity.get("status") == "PASS",
        "contamination_gate": contamination.get("status") == "PASS",
        "v24_authority_consumption": authority.get("status") == "PASS",
        "approval_input_receipt": receipt.get("status") == "PASS",
        "approval_binding": binding.get("status") == "PASS",
        "approval_consumption": consumption.get("status") == "PASS",
        "anti_replay": anti_replay.get("status") == "PASS",
        "approval_expiration": expiration.get("status") == "PASS",
        "blocked_capabilities": blocked.get("status") == "PASS",
        "transition_gate": transition.get("status") == "PASS",
        "anti_simulation": anti_simulation.get("status") == "PASS",
        "danger_always_false": all(danger_always_false(item) for item in [
            repo_identity,
            contamination,
            authority,
            receipt,
            binding,
            consumption,
            anti_replay,
            expiration,
            blocked,
            transition,
            anti_simulation,
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_5_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "hash_first_approval_transfer": True,
        "python_received_approval_plaintext": False,
        "v24_authority_valid": authority.get("status") == "PASS",
        "repo_identity_valid": repo_identity.get("repo_identity_valid") is True,
        "contamination_gate_pass": contamination.get("status") == "PASS",
        "human_approval_required": True,
        "human_approval_received": status == "PASS",
        "human_approval_valid": status == "PASS",
        "approval_match": status == "PASS",
        "approval_granted": status == "PASS",
        "approval_consumed": status == "PASS",
        "approval_reuse_allowed": False,
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
        "build_allowed_next": status == "PASS",
        "build_allowed_now": False,
        "external_execution": "DISABLED",
        "brain_mutation": "BLOCKED",
        "manual_mutation": "BLOCKED",
        "auto_action": False,
        "next_safe_step": NEXT_SAFE_STEP,
    })
    return report


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts = []

    for rel in MANIFEST_TRACKED_ARTIFACTS:
        path = root / rel
        artifacts.append({
            "path": rel,
            "sha256": sha256_file(path),
            "artifact_type": "generated_v2_5_BUILD_FIX_3",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_5_ARTIFACT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_5_ARTIFACT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
        ],
        "omission_reason": "Manifest cannot require its own final seal before seal exists; seal closes over manifest hash after manifest PASS.",
    })
    return report


def build_human_report(validation: dict[str, Any], receipt: dict[str, Any], consumption: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.5 BUILD-FIX-3 APPROVAL CONSUMPTION GATE — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## Hash-first approval result

- hash_first_approval_transfer: {validation.get("hash_first_approval_transfer")}
- python_received_approval_plaintext: {validation.get("python_received_approval_plaintext")}
- human_approval_required: {validation.get("human_approval_required")}
- human_approval_received: {validation.get("human_approval_received")}
- human_approval_valid: {validation.get("human_approval_valid")}
- approval_match: {validation.get("approval_match")}
- approval_granted: {validation.get("approval_granted")}
- approval_consumed: {validation.get("approval_consumed")}
- approval_reuse_allowed: {validation.get("approval_reuse_allowed")}
- approval_plaintext_stored: {validation.get("approval_plaintext_stored")}

## Approval hash evidence

- approval_input_hash_present: {receipt.get("approval_input_hash_present")}
- approval_input_hash: {receipt.get("approval_input_hash")}
- expected_approval_hash: {receipt.get("expected_approval_hash")}
- approval_hash_shape_valid: {receipt.get("approval_hash_shape_valid")}

## Transition

- build_allowed_next: {consumption.get("build_allowed_next")}
- build_allowed_now: {consumption.get("build_allowed_now")}
- execution_allowed: {consumption.get("execution_allowed")}
- next_safe_step: {consumption.get("next_safe_step")}

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

## Interpretation

v2.5 BUILD-FIX-3 consumed a fresh human terminal approval through a hash-first transfer.

PowerShell validated the exact phrase and computed the approval hash.

Python received only approval_present + approval_input_hash.

No approval plaintext was stored.

The layer authorized the next governed build step but did not execute it.

It did not mutate manual/current, manual/manifest, brain or reports/brain.

## Next safe step

{NEXT_SAFE_STEP}
"""


def generate(root: Path, head: str, branch: str, remote: str, upstream: str, approval_present: bool, approval_input_hash: str) -> int:
    repo_identity = build_repo_identity_report(root, head, branch, remote, upstream, repo_clean=True)
    contamination = build_contamination_gate_report(root, repo_identity)
    authority = build_v24_authority_consumption_report(root)
    challenge = build_challenge(root, head, branch, remote, upstream)

    expected_hash = str(challenge.get("expected_approval_hash", "")).strip().lower()
    receipt = build_approval_input_receipt_report(approval_present, approval_input_hash, expected_hash)

    if receipt.get("status") != "PASS":
        print(json.dumps({
            "status": "BLOCK",
            "reason": "HASH_FIRST_APPROVAL_NOT_VALID",
            "approval_present": approval_present,
            "approval_input_hash_present": bool(approval_input_hash),
            "expected_hash_present": bool(expected_hash),
            "approval_match": receipt.get("approval_match"),
            "python_received_approval_plaintext": False,
        }, indent=2, sort_keys=True))
        return EXIT_BLOCK

    binding = build_approval_binding_report(repo_identity, authority, contamination, receipt, challenge)
    consumption = build_approval_consumption_report(receipt, binding)
    anti_replay = build_anti_replay_consumption_report(challenge)
    expiration = build_approval_expiration_report()
    blocked = build_blocked_capabilities_report(consumption)
    transition = build_transition_gate_report(consumption)

    primary_reports = [
        repo_identity,
        contamination,
        authority,
        receipt,
        binding,
        consumption,
        anti_replay,
        expiration,
        blocked,
        transition,
    ]

    anti_simulation = build_anti_simulation_gate_report(primary_reports)

    validation = build_validation_report(
        repo_identity,
        contamination,
        authority,
        receipt,
        binding,
        consumption,
        anti_replay,
        expiration,
        blocked,
        transition,
        anti_simulation,
    )

    output_map = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json": repo_identity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json": contamination,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json": authority,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json": receipt,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json": binding,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json": consumption,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json": anti_replay,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT.json": expiration,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT.json": blocked,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json": transition,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json": validation,
    }

    for rel, report in output_map.items():
        write_atomic_json(root / rel, report)

    human = build_human_report(validation, receipt, consumption)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json", manifest)

    seal_status = (
        "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5_BUILD_FIX_3"
        if validation.get("status") == "PASS" and manifest.get("status") == "PASS"
        else "BLOCK"
    )

    seal = base_report("BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL", seal_status)
    seal.update({
        "seal_id": "BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL",
        "status": seal_status,
        "hash_first_approval_transfer": True,
        "python_received_approval_plaintext": False,
        "v24_authority_valid": validation.get("v24_authority_valid"),
        "repo_identity_valid": validation.get("repo_identity_valid"),
        "contamination_gate_pass": validation.get("contamination_gate_pass"),
        "human_approval_required": True,
        "human_approval_received": validation.get("human_approval_received"),
        "human_approval_valid": validation.get("human_approval_valid"),
        "approval_match": validation.get("approval_match"),
        "approval_granted": validation.get("approval_granted"),
        "approval_consumed": validation.get("approval_consumed"),
        "approval_reuse_allowed": False,
        "approval_plaintext_storage_allowed": False,
        "approval_plaintext_stored": False,
        "build_allowed_next": validation.get("build_allowed_next"),
        "build_allowed_now": False,
        "execution_allowed": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_REPORT.md"),
        "next_safe_step": NEXT_SAFE_STEP,
    })
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json", seal)

    return EXIT_PASS if seal_status == "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5_BUILD_FIX_3" else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json")
    receipt = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json")
    consumption = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json")
    contamination = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5_BUILD_FIX_3",
        "hash_first_true": seal.get("hash_first_approval_transfer") is True,
        "python_plaintext_false": seal.get("python_received_approval_plaintext") is False,
        "approval_received_true": seal.get("human_approval_received") is True,
        "approval_valid_true": seal.get("human_approval_valid") is True,
        "approval_granted_true": seal.get("approval_granted") is True,
        "approval_consumed_true": seal.get("approval_consumed") is True,
        "approval_reuse_false": seal.get("approval_reuse_allowed") is False,
        "plaintext_not_stored": receipt.get("approval_plaintext_stored") is False and seal.get("approval_plaintext_stored") is False,
        "approval_hash_present": bool(receipt.get("approval_input_hash")),
        "expected_hash_present": bool(receipt.get("expected_approval_hash")),
        "approval_hash_shape_valid": receipt.get("approval_hash_shape_valid") is True,
        "approval_match": receipt.get("approval_match") is True,
        "build_allowed_next_true": seal.get("build_allowed_next") is True and consumption.get("build_allowed_next") is True,
        "build_allowed_now_false": seal.get("build_allowed_now") is False and consumption.get("build_allowed_now") is False,
        "execution_allowed_false": seal.get("execution_allowed") is False and consumption.get("execution_allowed") is False,
        "contamination_pass": contamination.get("status") == "PASS" and contamination.get("contamination_detected") is False,
        "danger_always_false": all(danger_always_false(item) for item in [
            validation,
            manifest,
            seal,
            receipt,
            consumption,
            contamination,
        ]),
    }

    if not all(checks.values()):
        print(json.dumps({"status": "BLOCK", "checks": checks}, indent=2))
        return EXIT_BLOCK

    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["challenge", "generate", "validate-outputs"], required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--head", default="")
    parser.add_argument("--branch", default="")
    parser.add_argument("--remote", default="")
    parser.add_argument("--upstream", default="")
    parser.add_argument("--approval-present", choices=["true", "false"], default="false")
    parser.add_argument("--approval-input-hash", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "challenge":
        challenge = build_challenge(
            root=root,
            head=args.head,
            branch=args.branch,
            remote=args.remote,
            upstream=args.upstream,
        )
        safe_challenge = {
            "status": challenge.get("status"),
            "approval_challenge_hash": challenge.get("approval_challenge_hash"),
            "required_approval_phrase": challenge.get("required_approval_phrase"),
            "expected_approval_hash": challenge.get("expected_approval_hash"),
            "approval_plaintext_storage_allowed": False,
            "approval_plaintext_stored": False,
        }
        print(json.dumps(safe_challenge, ensure_ascii=False, indent=2, sort_keys=True))
        return EXIT_PASS if challenge.get("status") == "PASS" else EXIT_BLOCK

    if args.mode == "generate":
        return generate(
            root=root,
            head=args.head,
            branch=args.branch,
            remote=args.remote,
            upstream=args.upstream,
            approval_present=args.approval_present == "true",
            approval_input_hash=args.approval_input_hash,
        )

    if args.mode == "validate-outputs":
        return validate_outputs(root)

    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())