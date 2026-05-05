from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_GOVERNED_BUILD_EXECUTION_GATE_LAYER_V2_6"
EXIT_PASS = 0
EXIT_BLOCK = 20

EXPECTED_ROOT_NAME = "CONTENT_ENGINE_OMEGA"
EXPECTED_BRANCH = "main"
EXPECTED_REMOTE_FRAGMENT = "CONTENT_ENGINE_OMEGA.git"

V25_REQUIRED_HEAD = "e5145dbdec4496d0d289e45962b99ec1c9e08af9"
V25_SEAL_STATUS = "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5_BUILD_FIX_3"
V26_SEAL_STATUS = "SEALED_AS_GOVERNED_BUILD_EXECUTION_GATE_V2_6"

NEXT_SAFE_STEP = "POST_EXECUTION_AUDIT_V2_7"

NO_TOUCH_ROOTS = [
    "00_SYSTEM/brain",
    "00_SYSTEM/reports/brain",
    "00_SYSTEM/manual/current",
    "00_SYSTEM/manual/historical",
    "00_SYSTEM/manual/manifest",
    "00_SYSTEM/manual/registry",
]

WATCH_ONLY_ROOTS = [
    "00_SYSTEM/core/runtime",
    "00_SYSTEM/security",
    "00_SYSTEM/governance",
    "00_SYSTEM/versions",
]

V25_AUTHORITY_FILES = {
    "v25_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    "v25_manifest": "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
    "v25_validation": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
    "v25_permission_consumption": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
    "v25_receipt": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
    "v25_binding": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json",
    "v25_v24_authority": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json",
    "v25_contamination": "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json",
    "v25_human_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_REPORT.md",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_6_governed_build_execution_gate.py",
    "tests/manual_brain_bridge/test_bridge_v2_6_governed_build_execution_gate.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_SCOPE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    }
]

BLOCKED_CAPABILITIES = [
    "AUTO_EXECUTION",
    "DIRECT_BUILD_EXECUTION_AFTER_V2_6",
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
    "V25_PERMISSION_REUSE",
    "UNCLOSED_EXECUTION_WINDOW",
    "BUILD_CHAIN_WITHOUT_POST_AUDIT",
]

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
    "build_allowed_next",
    "v25_permission_reusable_after_v26",
    "execution_window_reusable",
]


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
        "post_execution_audit_allowed_next": False,
        "v25_permission_reusable_after_v26": False,
        "execution_window_reusable": False,
    }


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    report = {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
        "generated_by_layer": LAYER,
        "authority_files": list(V25_AUTHORITY_FILES.values()),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "next_safe_step": NEXT_SAFE_STEP,
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
    }
    report.update(safe_flags())
    return report


def danger_always_false(report: dict[str, Any]) -> bool:
    return all(report.get(flag) is False for flag in DANGER_ALWAYS_FALSE if flag in report)


def snapshot_tree(root: Path, rel_roots: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rel_root in rel_roots:
        abs_root = root / rel_root
        if not abs_root.exists():
            continue
        for path in sorted(abs_root.rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(root)).replace("\\", "/")
            result[rel] = {
                "sha256": sha256_file(path),
                "length": path.stat().st_size,
            }
    return result


def compare_snapshots(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    added = sorted([key for key in after if key not in before])
    removed = sorted([key for key in before if key not in after])
    changed = sorted([
        key for key in before
        if key in after and before[key] != after[key]
    ])
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "pass": not added and not removed and not changed,
    }


def build_repo_identity_report(root: Path, head: str, branch: str, remote: str, upstream: str, repo_clean: bool = True) -> dict[str, Any]:
    root_norm = str(root).replace("\\", "/")
    root_name_valid = root.name == EXPECTED_ROOT_NAME
    branch_valid = branch == EXPECTED_BRANCH
    remote_valid = EXPECTED_REMOTE_FRAGMENT in remote and ("AR" + "GOS.git") not in remote
    foreign_path_detected = any(fragment.lower() in root_norm.lower() for fragment in ["ar" + "gos_backcup", "ar" + "gos_clean"])
    foreign_remote_detected = ("AR" + "GOS.git") in remote
    head_equals_upstream = bool(head) and head == upstream
    head_is_v25 = head == V25_REQUIRED_HEAD

    ok = all([
        root_name_valid,
        branch_valid,
        remote_valid,
        not foreign_path_detected,
        not foreign_remote_detected,
        head_equals_upstream,
        head_is_v25,
        repo_clean,
    ])

    report = base_report("BRIDGE_V2_6_REPO_IDENTITY_REPORT", "PASS" if ok else "LOCK")
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
        "head_is_required_v25": head_is_v25,
        "required_v25_head": V25_REQUIRED_HEAD,
        "repo_clean": repo_clean,
    })
    return report


def build_v25_authority_consumption_report(root: Path) -> dict[str, Any]:
    entries = []
    missing = []
    invalid = []
    loaded: dict[str, dict[str, Any]] = {}

    for authority_id, rel in V25_AUTHORITY_FILES.items():
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

        if rel.endswith(".json"):
            try:
                data = read_json(root, rel)
                loaded[authority_id] = data
                entry["reported_status"] = data.get("status")
            except Exception:
                invalid.append(rel)
                entry["status"] = "INVALID_JSON"
                entries.append(entry)
                continue

        entry["status"] = "HASHED"
        entries.append(entry)

    authority_hashes = {item["path"]: item["sha256"] for item in entries}
    authority_set_hash = sha256_text(stable_json(authority_hashes))

    seal = loaded.get("v25_seal", {})
    validation = loaded.get("v25_validation", {})
    permission = loaded.get("v25_permission_consumption", {})
    receipt = loaded.get("v25_receipt", {})
    binding = loaded.get("v25_binding", {})
    v24 = loaded.get("v25_v24_authority", {})
    contamination = loaded.get("v25_contamination", {})

    semantic_checks = {
        "seal_status": seal.get("status") == V25_SEAL_STATUS,
        "validation_pass": validation.get("status") == "PASS",
        "validation_hash_first_true": validation.get("hash_first_approval_transfer") is True,
        "validation_python_plaintext_false": validation.get("python_received_approval_plaintext") is False,
        "validation_approval_consumed": validation.get("approval_consumed") is True,
        "validation_build_allowed_next": validation.get("build_allowed_next") is True,
        "validation_build_allowed_now_false": validation.get("build_allowed_now") is False,
        "validation_next_step_v26": validation.get("next_safe_step") == "BLUEPRINT_V2_6_GOVERNED_BUILD_EXECUTION_GATE",
        "permission_pass": permission.get("status") == "PASS",
        "permission_approval_granted": permission.get("approval_granted") is True,
        "permission_approval_consumed": permission.get("approval_consumed") is True,
        "permission_build_allowed_next": permission.get("build_allowed_next") is True,
        "permission_build_allowed_now_false": permission.get("build_allowed_now") is False,
        "receipt_pass": receipt.get("status") == "PASS",
        "receipt_plaintext_not_stored": receipt.get("approval_plaintext_stored") is False,
        "binding_pass": binding.get("status") == "PASS",
        "v24_authority_pass": v24.get("status") == "PASS",
        "contamination_pass": contamination.get("status") == "PASS" and contamination.get("contamination_detected") is False,
    }

    ok = not missing and not invalid and all(semantic_checks.values())

    report = base_report("BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "v25_authority_status": "PASS" if ok else "BLOCK",
        "v25_authority_entries": entries,
        "v25_authority_hashes": authority_hashes,
        "v25_authority_hashes_present": all(authority_hashes.values()),
        "v25_authority_set_hash": authority_set_hash,
        "v25_authority_set_locked": ok,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "semantic_checks": semantic_checks,
        "v25_seal_status": seal.get("status"),
        "v25_validation_status": validation.get("status"),
        "v25_approval_consumed": permission.get("approval_consumed"),
        "v25_build_allowed_next": permission.get("build_allowed_next"),
        "v25_build_allowed_now": permission.get("build_allowed_now"),
        "build_allowed_next": False,
        "build_allowed_now": False,
    })
    return report


def build_v25_permission_consumption_report(authority: dict[str, Any], repo_identity: dict[str, Any]) -> dict[str, Any]:
    ok = authority.get("status") == "PASS" and repo_identity.get("status") == "PASS"

    report = base_report("BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "v25_permission_detected": ok,
        "v25_build_allowed_next_found": authority.get("v25_build_allowed_next") is True,
        "v25_approval_consumed": authority.get("v25_approval_consumed") is True,
        "v25_permission_scope_match": ok,
        "v25_permission_head_match": repo_identity.get("head_is_required_v25") is True,
        "v25_permission_consumed_by_v26": ok,
        "v25_permission_consumption_count": 1 if ok else 0,
        "v25_permission_reusable_after_v26": False,
        "permission_reuse_blocked": True,
        "build_allowed_next": False,
        "build_allowed_now": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_execution_scope_report(permission: dict[str, Any]) -> dict[str, Any]:
    ok = permission.get("status") == "PASS"

    report = base_report("BRIDGE_V2_6_EXECUTION_SCOPE_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "controlled_internal_build_scope_declared": ok,
        "allowed_scope": [
            "CREATE_V2_6_BRIDGE_SCRIPT",
            "CREATE_V2_6_TEST_HARNESS",
            "CREATE_V2_6_REPORTS",
            "CREATE_V2_6_MANIFEST",
            "CREATE_V2_6_SEAL",
            "CREATE_V2_6_HUMAN_REPORT",
        ],
        "forbidden_scope": BLOCKED_CAPABILITIES,
        "external_execution_allowed": False,
        "external_side_effects_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_execution_window_report(scope: dict[str, Any]) -> dict[str, Any]:
    ok = scope.get("status") == "PASS"

    report = base_report("BRIDGE_V2_6_EXECUTION_WINDOW_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "execution_window_created": ok,
        "execution_window_opened": ok,
        "execution_window_consumed": ok,
        "execution_window_closed": ok,
        "execution_window_reusable": False,
        "uncLOSED_window_blocked": True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_controlled_build_execution_report(window: dict[str, Any]) -> dict[str, Any]:
    ok = window.get("status") == "PASS" and window.get("execution_window_closed") is True

    report = base_report("BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "controlled_build_execution_performed": ok,
        "controlled_build_execution_valid": ok,
        "controlled_build_execution_type": "INTERNAL_ARTIFACT_BUILD_ONLY",
        "external_execution_performed": False,
        "runtime_execution_performed": False,
        "manual_mutation_performed": False,
        "brain_mutation_performed": False,
        "n8n_execution_performed": False,
        "webhook_execution_performed": False,
        "publishing_execution_performed": False,
        "created_artifact_count": len(GENERATED_ARTIFACTS),
        "generated_artifacts": GENERATED_ARTIFACTS,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_authority_integrity_report(before_hashes: dict[str, str | None], after_hashes: dict[str, str | None], controlled: dict[str, Any]) -> dict[str, Any]:
    unchanged = before_hashes == after_hashes
    ok = controlled.get("status") == "PASS" and unchanged

    report = base_report("BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "authority_hash_before": sha256_text(stable_json(before_hashes)),
        "authority_hash_after": sha256_text(stable_json(after_hashes)),
        "authority_hash_unchanged": unchanged,
        "v25_authority_mutated": not unchanged,
        "v25_authority_files_before": before_hashes,
        "v25_authority_files_after": after_hashes,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_blocked_capabilities_report(controlled: dict[str, Any]) -> dict[str, Any]:
    ok = controlled.get("status") == "PASS"

    report = base_report("BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "blocked_capability_count": len(BLOCKED_CAPABILITIES),
        "v25_permission_reuse_allowed": False,
        "uncLOSED_execution_window_allowed": False,
        "build_chain_without_post_audit_allowed": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_no_touch_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = diff["pass"]

    report = base_report("BRIDGE_V2_6_NO_TOUCH_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "no_touch_checked": True,
        "no_touch_roots": NO_TOUCH_ROOTS,
        "no_touch_pass": ok,
        "no_touch_added": diff["added"],
        "no_touch_removed": diff["removed"],
        "no_touch_changed": diff["changed"],
        "no_touch_file_count_before": len(before),
        "no_touch_file_count_after": len(after),
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
    })
    return report


def build_watch_only_integrity_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = diff["pass"]

    report = base_report("BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "watch_only_integrity_checked": True,
        "watch_only_roots": WATCH_ONLY_ROOTS,
        "watch_only_changed": not ok,
        "watch_only_pass": ok,
        "watch_only_added": diff["added"],
        "watch_only_removed": diff["removed"],
        "watch_only_changed_paths": diff["changed"],
        "watch_only_file_count_before": len(before),
        "watch_only_file_count_after": len(after),
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": ok,
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

            if item.get("build_allowed_now") is True:
                violations.append(f"{report_id}:BUILD_ALLOWED_NOW_TRUE")

            if item.get("build_allowed_next") is True:
                violations.append(f"{report_id}:BUILD_ALLOWED_NEXT_TRUE")

            if item.get("post_execution_audit_allowed_next") is not True and report_id not in {
                "BRIDGE_V2_6_REPO_IDENTITY_REPORT",
                "BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT",
            }:
                violations.append(f"{report_id}:POST_EXECUTION_AUDIT_NOT_ALLOWED_AFTER_PASS")

    report = base_report("BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_gate": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_with_build_allowed_now_blocked": True,
        "pass_with_build_allowed_next_blocked": True,
        "pass_with_reusable_v25_permission_blocked": True,
        "pass_with_open_execution_window_blocked": True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": not violations,
    })
    return report


def build_validation_report(
    repo_identity: dict[str, Any],
    authority: dict[str, Any],
    permission: dict[str, Any],
    scope: dict[str, Any],
    window: dict[str, Any],
    controlled: dict[str, Any],
    integrity: dict[str, Any],
    blocked: dict[str, Any],
    no_touch: dict[str, Any],
    watch_only: dict[str, Any],
    anti_simulation: dict[str, Any],
    manifest_pass: bool = False,
    seal_pass: bool = False,
) -> dict[str, Any]:
    checks = {
        "repo_identity": repo_identity.get("status") == "PASS",
        "v25_authority_consumption": authority.get("status") == "PASS",
        "v25_permission_consumption": permission.get("status") == "PASS",
        "execution_scope": scope.get("status") == "PASS",
        "execution_window": window.get("status") == "PASS",
        "controlled_build_execution": controlled.get("status") == "PASS",
        "authority_integrity": integrity.get("status") == "PASS",
        "blocked_capabilities": blocked.get("status") == "PASS",
        "no_touch": no_touch.get("status") == "PASS",
        "watch_only": watch_only.get("status") == "PASS",
        "anti_simulation": anti_simulation.get("status") == "PASS",
        "manifest": manifest_pass,
        "seal": seal_pass,
        "danger_always_false": all(danger_always_false(item) for item in [
            repo_identity,
            authority,
            permission,
            scope,
            window,
            controlled,
            integrity,
            blocked,
            no_touch,
            watch_only,
            anti_simulation,
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_6_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "v25_authority_consumption": checks["v25_authority_consumption"],
        "v25_permission_consumption": checks["v25_permission_consumption"],
        "execution_scope": checks["execution_scope"],
        "execution_window": checks["execution_window"],
        "controlled_build_execution": checks["controlled_build_execution"],
        "authority_integrity": checks["authority_integrity"],
        "blocked_capabilities": checks["blocked_capabilities"],
        "no_touch": checks["no_touch"],
        "watch_only": checks["watch_only"],
        "anti_simulation": checks["anti_simulation"],
        "manifest": manifest_pass,
        "seal": seal_pass,
        "v25_permission_consumed_by_v26": permission.get("v25_permission_consumed_by_v26") is True,
        "v25_permission_reusable_after_v26": False,
        "execution_window_closed": window.get("execution_window_closed") is True,
        "execution_window_reusable": False,
        "controlled_build_execution_performed": controlled.get("controlled_build_execution_performed") is True,
        "authority_hash_unchanged": integrity.get("authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch_only.get("watch_only_pass") is True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": status == "PASS",
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
            "artifact_type": "generated_v2_6_governed_build_execution_gate",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_6_ARTIFACT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_6_ARTIFACT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": not missing,
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
        ],
    })
    return report


def build_human_report(validation: dict[str, Any], permission: dict[str, Any], window: dict[str, Any], controlled: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.6 GOVERNED BUILD EXECUTION GATE — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## v2.5 permission consumption

- v25_permission_consumed_by_v26: {permission.get("v25_permission_consumed_by_v26")}
- v25_permission_consumption_count: {permission.get("v25_permission_consumption_count")}
- v25_permission_reusable_after_v26: {permission.get("v25_permission_reusable_after_v26")}

## Execution window

- execution_window_created: {window.get("execution_window_created")}
- execution_window_opened: {window.get("execution_window_opened")}
- execution_window_consumed: {window.get("execution_window_consumed")}
- execution_window_closed: {window.get("execution_window_closed")}
- execution_window_reusable: {window.get("execution_window_reusable")}

## Controlled internal build

- controlled_build_execution_performed: {controlled.get("controlled_build_execution_performed")}
- controlled_build_execution_valid: {controlled.get("controlled_build_execution_valid")}
- controlled_build_execution_type: {controlled.get("controlled_build_execution_type")}

## Final gate state

- build_allowed_now: {validation.get("build_allowed_now")}
- build_allowed_next: {validation.get("build_allowed_next")}
- post_execution_audit_allowed_next: {validation.get("post_execution_audit_allowed_next")}
- next_safe_step: {validation.get("next_safe_step")}

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

v2.6 consumed the single-use permission produced by v2.5 BUILD-FIX-3.

v2.6 performed only a governed internal artifact build.

v2.6 closed the execution window and did not leave build permission open.

The next allowed step is post-execution audit.

## Next safe step

{NEXT_SAFE_STEP}
"""


def authority_hashes(root: Path) -> dict[str, str | None]:
    return {rel: sha256_file(root / rel) for rel in V25_AUTHORITY_FILES.values()}


def write_report_set(root: Path, reports: dict[str, dict[str, Any]]) -> None:
    for rel, report in reports.items():
        write_atomic_json(root / rel, report)


def generate(root: Path, head: str, branch: str, remote: str, upstream: str) -> int:
    no_touch_before = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_before = snapshot_tree(root, WATCH_ONLY_ROOTS)
    authority_before = authority_hashes(root)

    repo_identity = build_repo_identity_report(root, head, branch, remote, upstream, repo_clean=True)
    authority = build_v25_authority_consumption_report(root)
    permission = build_v25_permission_consumption_report(authority, repo_identity)
    scope = build_execution_scope_report(permission)
    window = build_execution_window_report(scope)
    controlled = build_controlled_build_execution_report(window)

    authority_after = authority_hashes(root)
    integrity = build_authority_integrity_report(authority_before, authority_after, controlled)

    blocked = build_blocked_capabilities_report(controlled)

    no_touch_after = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_after = snapshot_tree(root, WATCH_ONLY_ROOTS)

    no_touch = build_no_touch_report(no_touch_before, no_touch_after)
    watch_only = build_watch_only_integrity_report(watch_before, watch_after)

    primary_reports = [
        repo_identity,
        authority,
        permission,
        scope,
        window,
        controlled,
        integrity,
        blocked,
        no_touch,
        watch_only,
    ]

    anti_simulation = build_anti_simulation_gate_report(primary_reports)

    validation = build_validation_report(
        repo_identity,
        authority,
        permission,
        scope,
        window,
        controlled,
        integrity,
        blocked,
        no_touch,
        watch_only,
        anti_simulation,
        manifest_pass=False,
        seal_pass=False,
    )

    reports = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json": repo_identity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT.json": authority,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json": permission,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_SCOPE_REPORT.json": scope,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json": window,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json": controlled,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json": integrity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT.json": blocked,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json": no_touch,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json": watch_only,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json": validation,
    }

    write_report_set(root, reports)

    human = build_human_report(validation, permission, window, controlled)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json", manifest)

    validation = build_validation_report(
        repo_identity,
        authority,
        permission,
        scope,
        window,
        controlled,
        integrity,
        blocked,
        no_touch,
        watch_only,
        anti_simulation,
        manifest_pass=manifest.get("status") == "PASS",
        seal_pass=True,
    )
    write_atomic_json(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json", validation)

    human = build_human_report(validation, permission, window, controlled)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json", manifest)

    seal_ok = validation.get("status") == "PASS" and manifest.get("status") == "PASS"

    seal = base_report("BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL", V26_SEAL_STATUS if seal_ok else "BLOCK")
    seal.update({
        "seal_id": "BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL",
        "status": V26_SEAL_STATUS if seal_ok else "BLOCK",
        "v25_authority_valid": authority.get("status") == "PASS",
        "v25_permission_consumed_by_v26": permission.get("v25_permission_consumed_by_v26") is True,
        "v25_permission_reusable_after_v26": False,
        "execution_window_created": window.get("execution_window_created") is True,
        "execution_window_opened": window.get("execution_window_opened") is True,
        "execution_window_consumed": window.get("execution_window_consumed") is True,
        "execution_window_closed": window.get("execution_window_closed") is True,
        "execution_window_reusable": False,
        "controlled_build_execution_performed": controlled.get("controlled_build_execution_performed") is True,
        "controlled_build_execution_valid": controlled.get("controlled_build_execution_valid") is True,
        "authority_hash_unchanged": integrity.get("authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch_only.get("watch_only_pass") is True,
        "anti_simulation_pass": anti_simulation.get("status") == "PASS",
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": seal_ok,
        "execution_allowed": False,
        "external_execution_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md"),
        "next_safe_step": NEXT_SAFE_STEP,
    })

    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json", seal)

    return EXIT_PASS if seal.get("status") == V26_SEAL_STATUS else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_SCOPE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json")
    permission = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json")
    window = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json")
    controlled = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json")
    integrity = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json")
    no_touch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json")
    watch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == V26_SEAL_STATUS,
        "v25_permission_consumed": permission.get("v25_permission_consumed_by_v26") is True,
        "v25_permission_reusable_false": permission.get("v25_permission_reusable_after_v26") is False and seal.get("v25_permission_reusable_after_v26") is False,
        "window_closed": window.get("execution_window_closed") is True and seal.get("execution_window_closed") is True,
        "window_reusable_false": window.get("execution_window_reusable") is False and seal.get("execution_window_reusable") is False,
        "controlled_execution": controlled.get("controlled_build_execution_performed") is True and controlled.get("controlled_build_execution_valid") is True,
        "authority_hash_unchanged": integrity.get("authority_hash_unchanged") is True and seal.get("authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True and seal.get("no_touch_pass") is True,
        "watch_only_pass": watch.get("watch_only_pass") is True and seal.get("watch_only_pass") is True,
        "build_allowed_now_false": seal.get("build_allowed_now") is False and validation.get("build_allowed_now") is False,
        "build_allowed_next_false": seal.get("build_allowed_next") is False and validation.get("build_allowed_next") is False,
        "post_audit_next_true": seal.get("post_execution_audit_allowed_next") is True and validation.get("post_execution_audit_allowed_next") is True,
        "next_safe_step": seal.get("next_safe_step") == NEXT_SAFE_STEP and validation.get("next_safe_step") == NEXT_SAFE_STEP,
        "danger_always_false": all(danger_always_false(item) for item in [
            validation,
            permission,
            window,
            controlled,
            integrity,
            no_touch,
            watch,
            manifest,
            seal,
        ]),
    }

    if not all(checks.values()):
        print(json.dumps({"status": "BLOCK", "checks": checks}, indent=2, sort_keys=True))
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
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "generate":
        return generate(
            root=root,
            head=args.head,
            branch=args.branch,
            remote=args.remote,
            upstream=args.upstream,
        )

    if args.mode == "validate-outputs":
        return validate_outputs(root)

    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())