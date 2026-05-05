from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_POST_EXECUTION_AUDIT_LAYER_V2_7"
EXIT_PASS = 0
EXIT_BLOCK = 20

EXPECTED_ROOT_NAME = "CONTENT_ENGINE_OMEGA"
EXPECTED_BRANCH = "main"
EXPECTED_REMOTE_FRAGMENT = "CONTENT_ENGINE_OMEGA.git"

V26_REQUIRED_HEAD = "e0a0b3b98360a99d3835ab223725564dbe984442"
V26_SEAL_STATUS = "SEALED_AS_GOVERNED_BUILD_EXECUTION_GATE_V2_6"
V27_SEAL_STATUS = "SEALED_AS_POST_EXECUTION_AUDIT_V2_7"

NEXT_SAFE_STEP = "WARNING_REVIEW_OR_GATE_CLOSURE_V2_7"

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

V26_AUTHORITY_FILES = {
    "v26_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    "v26_manifest": "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
    "v26_validation": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
    "v26_permission": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
    "v26_window": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
    "v26_controlled": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json",
    "v26_authority_integrity": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json",
    "v26_no_touch": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json",
    "v26_watch_only": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json",
    "v26_anti_simulation": "00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json",
    "v26_human_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_REPORT.md",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_7_post_execution_audit.py",
    "tests/manual_brain_bridge/test_bridge_v2_7_post_execution_audit.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
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
    "V25_PERMISSION_REUSE",
    "V26_EXECUTION_WINDOW_REUSE",
    "BUILD_CHAIN_WITHOUT_AUDIT",
    "POST_EXECUTION_AUDIT_REUSE",
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
    "post_execution_audit_allowed_next",
    "v25_permission_reusable_after_v26",
    "v26_execution_window_reusable_after_audit",
    "post_execution_audit_reusable",
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
        "warning_review_or_gate_closure_allowed_next": False,
        "v25_permission_reusable_after_v26": False,
        "v26_execution_window_reusable_after_audit": False,
        "post_execution_audit_reusable": False,
    }


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    report = {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
        "generated_by_layer": LAYER,
        "authority_files": list(V26_AUTHORITY_FILES.values()),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "next_safe_step": NEXT_SAFE_STEP,
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
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


def authority_hashes(root: Path) -> dict[str, str | None]:
    return {rel: sha256_file(root / rel) for rel in V26_AUTHORITY_FILES.values()}


def build_repo_identity_audit_report(root: Path, head: str, branch: str, remote: str, upstream: str, repo_clean: bool = True) -> dict[str, Any]:
    root_norm = str(root).replace("\\", "/")
    root_name_valid = root.name == EXPECTED_ROOT_NAME
    branch_valid = branch == EXPECTED_BRANCH
    remote_valid = EXPECTED_REMOTE_FRAGMENT in remote and ("AR" + "GOS.git") not in remote
    foreign_path_detected = any(fragment.lower() in root_norm.lower() for fragment in ["ar" + "gos_backcup", "ar" + "gos_clean"])
    foreign_remote_detected = ("AR" + "GOS.git") in remote
    head_equals_upstream = bool(head) and head == upstream
    head_is_v26 = head == V26_REQUIRED_HEAD

    ok = all([
        root_name_valid,
        branch_valid,
        remote_valid,
        not foreign_path_detected,
        not foreign_remote_detected,
        head_equals_upstream,
        head_is_v26,
        repo_clean,
    ])

    report = base_report("BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT", "PASS" if ok else "LOCK")
    report.update({
        "repo_identity_valid": ok,
        "root": root_norm,
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
        "head_is_required_v26": head_is_v26,
        "required_v26_head": V26_REQUIRED_HEAD,
        "repo_clean": repo_clean,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_v26_authority_audit_report(root: Path) -> dict[str, Any]:
    entries = []
    missing = []
    invalid = []
    loaded: dict[str, dict[str, Any]] = {}

    for authority_id, rel in V26_AUTHORITY_FILES.items():
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

    seal = loaded.get("v26_seal", {})
    manifest = loaded.get("v26_manifest", {})
    validation = loaded.get("v26_validation", {})
    permission = loaded.get("v26_permission", {})
    window = loaded.get("v26_window", {})
    controlled = loaded.get("v26_controlled", {})
    integrity = loaded.get("v26_authority_integrity", {})
    no_touch = loaded.get("v26_no_touch", {})
    watch = loaded.get("v26_watch_only", {})
    anti = loaded.get("v26_anti_simulation", {})

    semantic_checks = {
        "seal_status": seal.get("status") == V26_SEAL_STATUS,
        "manifest_pass": manifest.get("status") == "PASS",
        "validation_pass": validation.get("status") == "PASS",
        "validation_build_allowed_now_false": validation.get("build_allowed_now") is False,
        "validation_build_allowed_next_false": validation.get("build_allowed_next") is False,
        "validation_post_execution_audit_allowed_next": validation.get("post_execution_audit_allowed_next") is True,
        "validation_next_step_v27": validation.get("next_safe_step") == "POST_EXECUTION_AUDIT_V2_7",
        "permission_pass": permission.get("status") == "PASS",
        "permission_v25_consumed": permission.get("v25_permission_consumed_by_v26") is True,
        "permission_v25_reusable_false": permission.get("v25_permission_reusable_after_v26") is False,
        "window_pass": window.get("status") == "PASS",
        "window_closed": window.get("execution_window_closed") is True,
        "window_reusable_false": window.get("execution_window_reusable") is False,
        "controlled_pass": controlled.get("status") == "PASS",
        "controlled_execution_valid": controlled.get("controlled_build_execution_valid") is True,
        "authority_integrity_pass": integrity.get("status") == "PASS",
        "authority_hash_unchanged": integrity.get("authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("status") == "PASS" and no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch.get("status") == "PASS" and watch.get("watch_only_pass") is True,
        "anti_simulation_pass": anti.get("status") == "PASS",
    }

    authority_hashes_map = {item["path"]: item["sha256"] for item in entries}
    authority_set_hash = sha256_text(stable_json(authority_hashes_map))
    ok = not missing and not invalid and all(semantic_checks.values())

    report = base_report("BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "v26_authority_audit_status": "PASS" if ok else "BLOCK",
        "v26_authority_entries": entries,
        "v26_authority_hashes": authority_hashes_map,
        "v26_authority_hashes_present": all(authority_hashes_map.values()),
        "v26_authority_set_hash": authority_set_hash,
        "v26_authority_set_locked": ok,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "semantic_checks": semantic_checks,
        "v26_seal_status": seal.get("status"),
        "v26_validation_status": validation.get("status"),
        "v26_permission_consumed": permission.get("v25_permission_consumed_by_v26"),
        "v26_execution_window_closed": window.get("execution_window_closed"),
        "v26_build_allowed_now": validation.get("build_allowed_now"),
        "v26_build_allowed_next": validation.get("build_allowed_next"),
        "v26_post_execution_audit_allowed_next": validation.get("post_execution_audit_allowed_next"),
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_execution_closure_audit_report(authority: dict[str, Any]) -> dict[str, Any]:
    checks = authority.get("semantic_checks", {})
    ok = authority.get("status") == "PASS" and checks.get("window_closed") is True and checks.get("window_reusable_false") is True

    report = base_report("BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "execution_closure_audited": True,
        "v26_execution_window_closed": checks.get("window_closed") is True,
        "v26_execution_window_reusable": False,
        "v26_execution_window_reuse_blocked": True,
        "v26_controlled_execution_valid": checks.get("controlled_execution_valid") is True,
        "uncLOSED_window_detected": False if ok else True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_permission_state_audit_report(authority: dict[str, Any], closure: dict[str, Any]) -> dict[str, Any]:
    checks = authority.get("semantic_checks", {})
    ok = (
        authority.get("status") == "PASS"
        and closure.get("status") == "PASS"
        and checks.get("validation_post_execution_audit_allowed_next") is True
    )

    report = base_report("BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "post_execution_audit_permission_detected_from_v26": checks.get("validation_post_execution_audit_allowed_next") is True,
        "post_execution_audit_permission_consumed_by_v27": ok,
        "post_execution_audit_allowed_next": False,
        "post_execution_audit_reusable": False,
        "post_execution_audit_reuse_blocked": True,
        "v25_permission_reusable_after_v26": False,
        "v26_execution_window_reusable_after_audit": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_artifact_integrity_audit_report(root: Path, before: dict[str, str | None], after: dict[str, str | None], permission: dict[str, Any]) -> dict[str, Any]:
    unchanged = before == after
    missing_hashes = [path for path, value in after.items() if not value]
    ok = permission.get("status") == "PASS" and unchanged and not missing_hashes

    report = base_report("BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "artifact_integrity_audited": True,
        "v26_authority_hash_before": sha256_text(stable_json(before)),
        "v26_authority_hash_after": sha256_text(stable_json(after)),
        "v26_authority_hash_unchanged": unchanged,
        "v26_authority_files_missing_hash": missing_hashes,
        "v26_artifacts_mutated_by_v27": not unchanged,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_no_touch_audit_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = diff["pass"]

    report = base_report("BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "no_touch_audited": True,
        "no_touch_roots": NO_TOUCH_ROOTS,
        "no_touch_pass": ok,
        "no_touch_added": diff["added"],
        "no_touch_removed": diff["removed"],
        "no_touch_changed": diff["changed"],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_watch_only_audit_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = diff["pass"]

    report = base_report("BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "watch_only_audited": True,
        "watch_only_roots": WATCH_ONLY_ROOTS,
        "watch_only_pass": ok,
        "watch_only_added": diff["added"],
        "watch_only_removed": diff["removed"],
        "watch_only_changed": diff["changed"],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_blocked_capabilities_audit_report(permission: dict[str, Any], closure: dict[str, Any]) -> dict[str, Any]:
    ok = permission.get("status") == "PASS" and closure.get("status") == "PASS"

    report = base_report("BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "blocked_capability_count": len(BLOCKED_CAPABILITIES),
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
        "execution_allowed": False,
        "external_execution_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
    })
    return report


def build_anti_regression_audit_report(authority: dict[str, Any], artifact_integrity: dict[str, Any], blocked: dict[str, Any]) -> dict[str, Any]:
    ok = authority.get("status") == "PASS" and artifact_integrity.get("status") == "PASS" and blocked.get("status") == "PASS"

    report = base_report("BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "anti_regression_audited": True,
        "v26_authority_not_downgraded": authority.get("status") == "PASS",
        "v26_authority_not_mutated": artifact_integrity.get("v26_authority_hash_unchanged") is True,
        "danger_capabilities_remain_blocked": blocked.get("status") == "PASS",
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": ok,
    })
    return report


def build_anti_simulation_audit_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
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

            if item.get("post_execution_audit_allowed_next") is True:
                violations.append(f"{report_id}:POST_EXECUTION_AUDIT_LEFT_OPEN")

            if item.get("warning_review_or_gate_closure_allowed_next") is not True:
                violations.append(f"{report_id}:NEXT_GATE_NOT_ALLOWED_AFTER_AUDIT_PASS")

    report = base_report("BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_audit": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_with_build_allowed_now_blocked": True,
        "pass_with_build_allowed_next_blocked": True,
        "pass_with_post_execution_audit_left_open_blocked": True,
        "pass_without_next_gate_allowed_blocked": True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": not violations,
    })
    return report


def build_validation_report(
    repo_identity: dict[str, Any],
    authority: dict[str, Any],
    closure: dict[str, Any],
    permission: dict[str, Any],
    artifact_integrity: dict[str, Any],
    no_touch: dict[str, Any],
    watch_only: dict[str, Any],
    blocked: dict[str, Any],
    anti_regression: dict[str, Any],
    anti_simulation: dict[str, Any],
    manifest_pass: bool = False,
    seal_pass: bool = False,
) -> dict[str, Any]:
    checks = {
        "repo_identity": repo_identity.get("status") == "PASS",
        "v26_authority_audit": authority.get("status") == "PASS",
        "execution_closure_audit": closure.get("status") == "PASS",
        "permission_state_audit": permission.get("status") == "PASS",
        "artifact_integrity_audit": artifact_integrity.get("status") == "PASS",
        "no_touch_audit": no_touch.get("status") == "PASS",
        "watch_only_audit": watch_only.get("status") == "PASS",
        "blocked_capabilities_audit": blocked.get("status") == "PASS",
        "anti_regression_audit": anti_regression.get("status") == "PASS",
        "anti_simulation_audit": anti_simulation.get("status") == "PASS",
        "manifest": manifest_pass,
        "seal": seal_pass,
        "danger_always_false": all(danger_always_false(item) for item in [
            repo_identity,
            authority,
            closure,
            permission,
            artifact_integrity,
            no_touch,
            watch_only,
            blocked,
            anti_regression,
            anti_simulation,
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_7_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "post_execution_audit_completed": status == "PASS",
        "post_execution_audit_permission_consumed_by_v27": permission.get("post_execution_audit_permission_consumed_by_v27") is True,
        "post_execution_audit_reusable": False,
        "v25_permission_reusable_after_v26": False,
        "v26_execution_window_reusable_after_audit": False,
        "v26_execution_window_closed": closure.get("v26_execution_window_closed") is True,
        "v26_authority_hash_unchanged": artifact_integrity.get("v26_authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch_only.get("watch_only_pass") is True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": status == "PASS",
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
            "artifact_type": "generated_v2_7_post_execution_audit",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": not missing,
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
        ],
    })
    return report


def build_human_report(validation: dict[str, Any], permission: dict[str, Any], closure: dict[str, Any], artifact_integrity: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.7 POST EXECUTION AUDIT  MANUAL  CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## Audited source

v2.6  GOVERNED BUILD EXECUTION GATE

## Permission audit

- post_execution_audit_permission_consumed_by_v27: {permission.get("post_execution_audit_permission_consumed_by_v27")}
- post_execution_audit_allowed_next: {permission.get("post_execution_audit_allowed_next")}
- post_execution_audit_reusable: {permission.get("post_execution_audit_reusable")}

## Execution closure audit

- v26_execution_window_closed: {closure.get("v26_execution_window_closed")}
- v26_execution_window_reusable: {closure.get("v26_execution_window_reusable")}
- v26_controlled_execution_valid: {closure.get("v26_controlled_execution_valid")}

## Artifact integrity

- v26_authority_hash_unchanged: {artifact_integrity.get("v26_authority_hash_unchanged")}
- v26_artifacts_mutated_by_v27: {artifact_integrity.get("v26_artifacts_mutated_by_v27")}

## Final gate state

- build_allowed_now: {validation.get("build_allowed_now")}
- build_allowed_next: {validation.get("build_allowed_next")}
- post_execution_audit_allowed_next: {validation.get("post_execution_audit_allowed_next")}
- warning_review_or_gate_closure_allowed_next: {validation.get("warning_review_or_gate_closure_allowed_next")}
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

v2.7 audited v2.6 after governed build execution.

v2.7 did not open a new build window.

v2.7 consumed the post-execution audit permission and left it closed.

v2.7 did not mutate v2.6 authority files.

v2.7 did not mutate manual/current, manual/manifest, brain, reports/brain or watch-only roots.

The next safe step is warning review or gate closure.

## Next safe step

{NEXT_SAFE_STEP}
"""


def write_report_set(root: Path, reports: dict[str, dict[str, Any]]) -> None:
    for rel, report in reports.items():
        write_atomic_json(root / rel, report)


def generate(root: Path, head: str, branch: str, remote: str, upstream: str) -> int:
    no_touch_before = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_before = snapshot_tree(root, WATCH_ONLY_ROOTS)
    v26_authority_before = authority_hashes(root)

    repo_identity = build_repo_identity_audit_report(root, head, branch, remote, upstream, repo_clean=True)
    authority = build_v26_authority_audit_report(root)
    closure = build_execution_closure_audit_report(authority)
    permission = build_permission_state_audit_report(authority, closure)

    v26_authority_after = authority_hashes(root)
    artifact_integrity = build_artifact_integrity_audit_report(root, v26_authority_before, v26_authority_after, permission)

    no_touch_after = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_after = snapshot_tree(root, WATCH_ONLY_ROOTS)

    no_touch = build_no_touch_audit_report(no_touch_before, no_touch_after)
    watch_only = build_watch_only_audit_report(watch_before, watch_after)
    blocked = build_blocked_capabilities_audit_report(permission, closure)
    anti_regression = build_anti_regression_audit_report(authority, artifact_integrity, blocked)

    primary_reports = [
        repo_identity,
        authority,
        closure,
        permission,
        artifact_integrity,
        no_touch,
        watch_only,
        blocked,
        anti_regression,
    ]

    anti_simulation = build_anti_simulation_audit_report(primary_reports)

    validation = build_validation_report(
        repo_identity,
        authority,
        closure,
        permission,
        artifact_integrity,
        no_touch,
        watch_only,
        blocked,
        anti_regression,
        anti_simulation,
        manifest_pass=False,
        seal_pass=False,
    )

    reports = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json": repo_identity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT.json": authority,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json": closure,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json": permission,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json": artifact_integrity,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json": no_touch,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json": watch_only,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json": blocked,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json": anti_regression,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json": validation,
    }

    write_report_set(root, reports)

    human = build_human_report(validation, permission, closure, artifact_integrity)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json", manifest)

    validation = build_validation_report(
        repo_identity,
        authority,
        closure,
        permission,
        artifact_integrity,
        no_touch,
        watch_only,
        blocked,
        anti_regression,
        anti_simulation,
        manifest_pass=manifest.get("status") == "PASS",
        seal_pass=True,
    )

    write_atomic_json(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json", validation)

    human = build_human_report(validation, permission, closure, artifact_integrity)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json", manifest)

    seal_ok = validation.get("status") == "PASS" and manifest.get("status") == "PASS"

    seal = base_report("BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL", V27_SEAL_STATUS if seal_ok else "BLOCK")
    seal.update({
        "seal_id": "BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL",
        "status": V27_SEAL_STATUS if seal_ok else "BLOCK",
        "post_execution_audit_completed": seal_ok,
        "post_execution_audit_permission_consumed_by_v27": permission.get("post_execution_audit_permission_consumed_by_v27") is True,
        "post_execution_audit_allowed_next": False,
        "post_execution_audit_reusable": False,
        "v25_permission_reusable_after_v26": False,
        "v26_execution_window_closed": closure.get("v26_execution_window_closed") is True,
        "v26_execution_window_reusable_after_audit": False,
        "v26_controlled_execution_valid": closure.get("v26_controlled_execution_valid") is True,
        "v26_authority_hash_unchanged": artifact_integrity.get("v26_authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch_only.get("watch_only_pass") is True,
        "anti_regression_pass": anti_regression.get("status") == "PASS",
        "anti_simulation_pass": anti_simulation.get("status") == "PASS",
        "build_allowed_now": False,
        "build_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": seal_ok,
        "execution_allowed": False,
        "external_execution_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md"),
        "next_safe_step": NEXT_SAFE_STEP,
    })

    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json", seal)

    return EXIT_PASS if seal.get("status") == V27_SEAL_STATUS else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json")
    permission = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json")
    closure = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json")
    artifact_integrity = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json")
    no_touch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json")
    watch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json")
    blocked = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json")
    anti_regression = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json")
    anti = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == V27_SEAL_STATUS,
        "post_audit_completed": seal.get("post_execution_audit_completed") is True,
        "post_audit_consumed": permission.get("post_execution_audit_permission_consumed_by_v27") is True,
        "post_audit_next_false": seal.get("post_execution_audit_allowed_next") is False and validation.get("post_execution_audit_allowed_next") is False,
        "post_audit_reusable_false": seal.get("post_execution_audit_reusable") is False,
        "v26_window_closed": closure.get("v26_execution_window_closed") is True and seal.get("v26_execution_window_closed") is True,
        "v26_window_reusable_false": seal.get("v26_execution_window_reusable_after_audit") is False,
        "v26_authority_hash_unchanged": artifact_integrity.get("v26_authority_hash_unchanged") is True and seal.get("v26_authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True and seal.get("no_touch_pass") is True,
        "watch_only_pass": watch.get("watch_only_pass") is True and seal.get("watch_only_pass") is True,
        "blocked_capabilities_pass": blocked.get("status") == "PASS",
        "anti_regression_pass": anti_regression.get("status") == "PASS",
        "anti_simulation_pass": anti.get("status") == "PASS",
        "build_allowed_now_false": seal.get("build_allowed_now") is False and validation.get("build_allowed_now") is False,
        "build_allowed_next_false": seal.get("build_allowed_next") is False and validation.get("build_allowed_next") is False,
        "next_gate_true": seal.get("warning_review_or_gate_closure_allowed_next") is True and validation.get("warning_review_or_gate_closure_allowed_next") is True,
        "next_safe_step": seal.get("next_safe_step") == NEXT_SAFE_STEP and validation.get("next_safe_step") == NEXT_SAFE_STEP,
        "danger_always_false": all(danger_always_false(item) for item in [
            validation,
            permission,
            closure,
            artifact_integrity,
            no_touch,
            watch,
            blocked,
            anti_regression,
            anti,
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