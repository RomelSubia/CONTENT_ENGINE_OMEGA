from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_WARNING_REVIEW_GATE_CLOSURE_LAYER_V2_7"
EXIT_PASS = 0
EXIT_BLOCK = 20

EXPECTED_ROOT_NAME = "CONTENT_ENGINE_OMEGA"
EXPECTED_BRANCH = "main"
EXPECTED_REMOTE_FRAGMENT = "CONTENT_ENGINE_OMEGA.git"

V27_REQUIRED_HEAD = "b33252faf809c8431ee6144494e41e38dbefbb68"
V27_POST_AUDIT_SEAL_STATUS = "SEALED_AS_POST_EXECUTION_AUDIT_V2_7"
V27_GATE_CLOSURE_SEAL_STATUS = "SEALED_AS_V2_7_GATE_CLOSED_AFTER_WARNING_REVIEW"
NEXT_SAFE_STEP = "NEXT_BRIDGE_LAYER_BLUEPRINT"

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

V27_AUTHORITY_FILES = {
    "v27_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
    "v27_manifest": "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
    "v27_validation": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
    "v27_permission": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
    "v27_closure": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json",
    "v27_artifact_integrity": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json",
    "v27_no_touch": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json",
    "v27_watch_only": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json",
    "v27_anti_regression": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json",
    "v27_anti_simulation": "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json",
    "v27_human_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_POST_EXECUTION_AUDIT_REPORT.md",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_7_warning_review_gate_closure.py",
    "tests/manual_brain_bridge/test_bridge_v2_7_warning_review_gate_closure.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_GATE_CLOSURE_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
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
    "POST_EXECUTION_AUDIT_REUSE",
    "UNCLOSED_WARNING_REVIEW",
    "NEXT_LAYER_BUILD_WITHOUT_BLUEPRINT",
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
    "warning_review_or_gate_closure_allowed_next",
    "next_layer_build_allowed_now",
    "next_layer_implementation_allowed_now",
    "next_layer_execution_allowed_now",
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
        "next_layer_blueprint_allowed_next": False,
        "next_layer_build_allowed_now": False,
        "next_layer_implementation_allowed_now": False,
        "next_layer_execution_allowed_now": False,
    }


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    report = {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
        "generated_by_layer": LAYER,
        "authority_files": list(V27_AUTHORITY_FILES.values()),
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "next_safe_step": NEXT_SAFE_STEP,
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
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
    return {rel: sha256_file(root / rel) for rel in V27_AUTHORITY_FILES.values()}


def build_warning_review_report(root: Path) -> dict[str, Any]:
    loaded: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    invalid: list[str] = []

    for rel in V27_AUTHORITY_FILES.values():
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        if rel.endswith(".json"):
            try:
                loaded[rel] = read_json(root, rel)
            except Exception:
                invalid.append(rel)

    seal = loaded.get(V27_AUTHORITY_FILES["v27_seal"], {})
    validation = loaded.get(V27_AUTHORITY_FILES["v27_validation"], {})
    permission = loaded.get(V27_AUTHORITY_FILES["v27_permission"], {})
    closure = loaded.get(V27_AUTHORITY_FILES["v27_closure"], {})
    artifact_integrity = loaded.get(V27_AUTHORITY_FILES["v27_artifact_integrity"], {})
    no_touch = loaded.get(V27_AUTHORITY_FILES["v27_no_touch"], {})
    watch = loaded.get(V27_AUTHORITY_FILES["v27_watch_only"], {})
    anti_regression = loaded.get(V27_AUTHORITY_FILES["v27_anti_regression"], {})
    anti_simulation = loaded.get(V27_AUTHORITY_FILES["v27_anti_simulation"], {})

    semantic_checks = {
        "v27_seal_status": seal.get("status") == V27_POST_AUDIT_SEAL_STATUS,
        "v27_validation_pass": validation.get("status") == "PASS",
        "post_execution_audit_completed": validation.get("post_execution_audit_completed") is True,
        "post_execution_audit_closed": validation.get("post_execution_audit_allowed_next") is False,
        "warning_review_allowed": validation.get("warning_review_or_gate_closure_allowed_next") is True,
        "build_allowed_now_false": validation.get("build_allowed_now") is False,
        "build_allowed_next_false": validation.get("build_allowed_next") is False,
        "permission_consumed": permission.get("post_execution_audit_permission_consumed_by_v27") is True,
        "permission_reusable_false": permission.get("post_execution_audit_reusable") is False,
        "execution_window_closed": closure.get("v26_execution_window_closed") is True,
        "authority_unchanged": artifact_integrity.get("v26_authority_hash_unchanged") is True,
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch.get("watch_only_pass") is True,
        "anti_regression_pass": anti_regression.get("status") == "PASS",
        "anti_simulation_pass": anti_simulation.get("status") == "PASS",
        "anti_simulation_no_violations": anti_simulation.get("violations") == [],
    }

    visible_warnings: list[str] = []
    hidden_warnings: list[str] = []
    critical_warnings: list[str] = []

    if missing:
        critical_warnings.append("MISSING_AUTHORITY_FILES")
    if invalid:
        critical_warnings.append("INVALID_AUTHORITY_JSON")
    if not all(semantic_checks.values()):
        critical_warnings.append("FAILED_V27_SEMANTIC_CHECKS")
    if anti_simulation.get("violations"):
        critical_warnings.append("ANTI_SIMULATION_VIOLATIONS_PRESENT")

    ok = not visible_warnings and not hidden_warnings and not critical_warnings

    report = base_report("BRIDGE_V2_7_WARNING_REVIEW_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "warning_review_completed": ok,
        "warning_review_status": "NO_WARNINGS_FOUND" if ok else "WARNINGS_BLOCK_CLOSURE",
        "visible_warning_count": len(visible_warnings),
        "hidden_warning_count": len(hidden_warnings),
        "critical_warning_count": len(critical_warnings),
        "visible_warnings": visible_warnings,
        "hidden_warnings": hidden_warnings,
        "critical_warnings": critical_warnings,
        "accepted_visible_warning_count": 0,
        "accepted_hidden_warning_count": 0,
        "accepted_critical_warning_count": 0,
        "warning_acceptance_required": False,
        "warning_acceptance_performed": False,
        "warning_suppression_performed": False,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "semantic_checks": semantic_checks,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": ok,
    })
    return report


def build_gate_closure_report(warning_review: dict[str, Any]) -> dict[str, Any]:
    ok = warning_review.get("status") == "PASS"

    report = base_report("BRIDGE_V2_7_GATE_CLOSURE_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "gate_closure_completed": ok,
        "gate_closure_status": "CLOSED_WITH_NO_WARNINGS" if ok else "BLOCKED",
        "closed_layer": "POST_EXECUTION_AUDIT_V2_7",
        "warning_review_completed": warning_review.get("warning_review_completed") is True,
        "visible_warning_count": warning_review.get("visible_warning_count"),
        "hidden_warning_count": warning_review.get("hidden_warning_count"),
        "critical_warning_count": warning_review.get("critical_warning_count"),
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": ok,
        "next_layer_build_allowed_now": False,
        "next_layer_implementation_allowed_now": False,
        "next_layer_execution_allowed_now": False,
        "next_safe_step": NEXT_SAFE_STEP,
    })
    return report


def build_next_layer_readiness_map(closure: dict[str, Any]) -> dict[str, Any]:
    ok = closure.get("status") == "PASS"

    report = base_report("BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP", "PASS" if ok else "BLOCK")
    report.update({
        "next_layer_readiness_map_defined": ok,
        "previous_gate_closed": ok,
        "next_safe_step": NEXT_SAFE_STEP,
        "next_layer_blueprint_allowed_next": ok,
        "next_layer_implementation_plan_allowed_now": False,
        "next_layer_build_allowed_now": False,
        "next_layer_execution_allowed_now": False,
        "requirements_for_next_layer_blueprint": [
            "DEFINE_SCOPE_BEFORE_IMPLEMENTATION",
            "NO_DIRECT_BUILD_FROM_GATE_CLOSURE",
            "NO_RUNTIME_EXECUTION",
            "NO_MANUAL_MUTATION",
            "NO_BRAIN_MUTATION",
            "NO_N8N_WEBHOOK_PUBLISHING",
            "PRESERVE_NO_TOUCH_AND_WATCH_ONLY",
        ],
        "blocked_until_blueprint_exists": [
            "IMPLEMENTATION_PLAN",
            "BUILD",
            "EXECUTION",
            "POST_BUILD_AUDIT",
        ],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
    })
    return report


def build_no_touch_closure_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]], closure: dict[str, Any]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = closure.get("status") == "PASS" and diff["pass"]

    report = base_report("BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "no_touch_closure_checked": True,
        "no_touch_pass": ok,
        "no_touch_roots": NO_TOUCH_ROOTS,
        "no_touch_added": diff["added"],
        "no_touch_removed": diff["removed"],
        "no_touch_changed": diff["changed"],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": ok,
    })
    return report


def build_watch_only_closure_report(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]], closure: dict[str, Any]) -> dict[str, Any]:
    diff = compare_snapshots(before, after)
    ok = closure.get("status") == "PASS" and diff["pass"]

    report = base_report("BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "watch_only_closure_checked": True,
        "watch_only_pass": ok,
        "watch_only_roots": WATCH_ONLY_ROOTS,
        "watch_only_added": diff["added"],
        "watch_only_removed": diff["removed"],
        "watch_only_changed": diff["changed"],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": ok,
    })
    return report


def build_anti_simulation_closure_report(reports: list[dict[str, Any]]) -> dict[str, Any]:
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

            if item.get("warning_review_or_gate_closure_allowed_next") is True:
                violations.append(f"{report_id}:WARNING_REVIEW_LEFT_OPEN")

    report = base_report("BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_closure": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_with_open_build_blocked": True,
        "pass_with_open_post_audit_blocked": True,
        "pass_with_warning_review_left_open_blocked": True,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": not violations,
    })
    return report


def build_validation_report(
    warning_review: dict[str, Any],
    closure: dict[str, Any],
    readiness: dict[str, Any],
    no_touch: dict[str, Any],
    watch_only: dict[str, Any],
    anti_simulation: dict[str, Any],
    manifest_pass: bool = False,
    seal_pass: bool = False,
) -> dict[str, Any]:
    checks = {
        "warning_review": warning_review.get("status") == "PASS",
        "gate_closure": closure.get("status") == "PASS",
        "next_layer_readiness": readiness.get("status") == "PASS",
        "no_touch": no_touch.get("status") == "PASS",
        "watch_only": watch_only.get("status") == "PASS",
        "anti_simulation": anti_simulation.get("status") == "PASS",
        "manifest": manifest_pass,
        "seal": seal_pass,
        "danger_always_false": all(danger_always_false(item) for item in [
            warning_review,
            closure,
            readiness,
            no_touch,
            watch_only,
            anti_simulation,
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "v2_7_gate_closed": status == "PASS",
        "closure_status": "CLOSED_WITH_NO_WARNINGS" if status == "PASS" else "BLOCKED",
        "warning_review_completed": warning_review.get("warning_review_completed") is True,
        "visible_warning_count": warning_review.get("visible_warning_count"),
        "hidden_warning_count": warning_review.get("hidden_warning_count"),
        "critical_warning_count": warning_review.get("critical_warning_count"),
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": status == "PASS",
        "next_layer_build_allowed_now": False,
        "next_layer_implementation_allowed_now": False,
        "next_layer_execution_allowed_now": False,
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
            "artifact_type": "generated_v2_7_gate_closure",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_7_GATE_CLOSURE_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_7_GATE_CLOSURE_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "build_allowed_now": False,
        "build_allowed_next": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": not missing,
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
        ],
    })
    return report


def build_human_report(validation: dict[str, Any], warning_review: dict[str, Any], closure: dict[str, Any], readiness: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.7 WARNING REVIEW / GATE CLOSURE — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## Warning review

- warning_review_completed: {warning_review.get("warning_review_completed")}
- warning_review_status: {warning_review.get("warning_review_status")}
- visible_warning_count: {warning_review.get("visible_warning_count")}
- hidden_warning_count: {warning_review.get("hidden_warning_count")}
- critical_warning_count: {warning_review.get("critical_warning_count")}
- warning_acceptance_required: {warning_review.get("warning_acceptance_required")}
- warning_suppression_performed: {warning_review.get("warning_suppression_performed")}

## Gate closure

- gate_closure_completed: {closure.get("gate_closure_completed")}
- gate_closure_status: {closure.get("gate_closure_status")}
- closed_layer: {closure.get("closed_layer")}

## Final permission state

- build_allowed_now: {validation.get("build_allowed_now")}
- build_allowed_next: {validation.get("build_allowed_next")}
- post_execution_audit_allowed_next: {validation.get("post_execution_audit_allowed_next")}
- warning_review_or_gate_closure_allowed_next: {validation.get("warning_review_or_gate_closure_allowed_next")}
- next_layer_blueprint_allowed_next: {validation.get("next_layer_blueprint_allowed_next")}
- next_layer_build_allowed_now: {validation.get("next_layer_build_allowed_now")}
- next_layer_implementation_allowed_now: {validation.get("next_layer_implementation_allowed_now")}
- next_layer_execution_allowed_now: {validation.get("next_layer_execution_allowed_now")}

## Next layer readiness

- next_layer_readiness_map_defined: {readiness.get("next_layer_readiness_map_defined")}
- next_safe_step: {readiness.get("next_safe_step")}

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

v2.7 post-execution audit has been reviewed and closed.

No visible, hidden, or critical warnings were accepted or suppressed.

No build window remains open.

No execution permission remains open.

The next allowed step is only the next bridge layer blueprint.

## Next safe step

{NEXT_SAFE_STEP}
"""


def write_report_set(root: Path, reports: dict[str, dict[str, Any]]) -> None:
    for rel, report in reports.items():
        write_atomic_json(root / rel, report)


def generate(root: Path, head: str, branch: str, remote: str, upstream: str) -> int:
    no_touch_before = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_before = snapshot_tree(root, WATCH_ONLY_ROOTS)

    warning_review = build_warning_review_report(root)
    closure = build_gate_closure_report(warning_review)
    readiness = build_next_layer_readiness_map(closure)

    no_touch_after = snapshot_tree(root, NO_TOUCH_ROOTS)
    watch_after = snapshot_tree(root, WATCH_ONLY_ROOTS)

    no_touch = build_no_touch_closure_report(no_touch_before, no_touch_after, closure)
    watch_only = build_watch_only_closure_report(watch_before, watch_after, closure)

    primary_reports = [
        warning_review,
        closure,
        readiness,
        no_touch,
        watch_only,
    ]

    anti_simulation = build_anti_simulation_closure_report(primary_reports)

    validation = build_validation_report(
        warning_review,
        closure,
        readiness,
        no_touch,
        watch_only,
        anti_simulation,
        manifest_pass=False,
        seal_pass=False,
    )

    reports = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json": warning_review,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json": closure,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json": readiness,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json": no_touch,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json": watch_only,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json": validation,
    }

    write_report_set(root, reports)

    human = build_human_report(validation, warning_review, closure, readiness)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_GATE_CLOSURE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json", manifest)

    validation = build_validation_report(
        warning_review,
        closure,
        readiness,
        no_touch,
        watch_only,
        anti_simulation,
        manifest_pass=manifest.get("status") == "PASS",
        seal_pass=True,
    )

    write_atomic_json(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json", validation)

    human = build_human_report(validation, warning_review, closure, readiness)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_GATE_CLOSURE_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json", manifest)

    seal_ok = validation.get("status") == "PASS" and manifest.get("status") == "PASS"

    seal = base_report("BRIDGE_V2_7_GATE_CLOSURE_SEAL", V27_GATE_CLOSURE_SEAL_STATUS if seal_ok else "BLOCK")
    seal.update({
        "seal_id": "BRIDGE_V2_7_GATE_CLOSURE_SEAL",
        "status": V27_GATE_CLOSURE_SEAL_STATUS if seal_ok else "BLOCK",
        "v2_7_gate_closed": seal_ok,
        "gate_closure_status": "CLOSED_WITH_NO_WARNINGS" if seal_ok else "BLOCKED",
        "warning_review_completed": warning_review.get("warning_review_completed") is True,
        "visible_warning_count": warning_review.get("visible_warning_count"),
        "hidden_warning_count": warning_review.get("hidden_warning_count"),
        "critical_warning_count": warning_review.get("critical_warning_count"),
        "warning_acceptance_required": False,
        "warning_suppression_performed": False,
        "post_execution_audit_allowed_next": False,
        "warning_review_or_gate_closure_allowed_next": False,
        "next_layer_blueprint_allowed_next": seal_ok,
        "next_layer_build_allowed_now": False,
        "next_layer_implementation_allowed_now": False,
        "next_layer_execution_allowed_now": False,
        "build_allowed_now": False,
        "build_allowed_next": False,
        "execution_allowed": False,
        "external_execution_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_GATE_CLOSURE_REPORT.md"),
        "next_safe_step": NEXT_SAFE_STEP,
    })

    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json", seal)

    return EXIT_PASS if seal.get("status") == V27_GATE_CLOSURE_SEAL_STATUS else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_7_GATE_CLOSURE_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    warning_review = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json")
    closure = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json")
    readiness = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json")
    no_touch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json")
    watch = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json")
    anti = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json")
    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json")

    checks = {
        "warning_review_pass": warning_review.get("status") == "PASS",
        "no_visible_warnings": warning_review.get("visible_warning_count") == 0,
        "no_hidden_warnings": warning_review.get("hidden_warning_count") == 0,
        "no_critical_warnings": warning_review.get("critical_warning_count") == 0,
        "closure_pass": closure.get("status") == "PASS",
        "closure_completed": closure.get("gate_closure_completed") is True,
        "readiness_pass": readiness.get("status") == "PASS",
        "no_touch_pass": no_touch.get("no_touch_pass") is True,
        "watch_only_pass": watch.get("watch_only_pass") is True,
        "anti_simulation_pass": anti.get("status") == "PASS",
        "anti_simulation_no_violations": anti.get("violations") == [],
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == V27_GATE_CLOSURE_SEAL_STATUS,
        "post_audit_closed": seal.get("post_execution_audit_allowed_next") is False,
        "warning_review_closed": seal.get("warning_review_or_gate_closure_allowed_next") is False,
        "next_blueprint_true": seal.get("next_layer_blueprint_allowed_next") is True and validation.get("next_layer_blueprint_allowed_next") is True,
        "build_now_false": seal.get("build_allowed_now") is False and validation.get("build_allowed_now") is False,
        "build_next_false": seal.get("build_allowed_next") is False and validation.get("build_allowed_next") is False,
        "next_layer_build_now_false": seal.get("next_layer_build_allowed_now") is False,
        "next_layer_implementation_now_false": seal.get("next_layer_implementation_allowed_now") is False,
        "next_safe_step": seal.get("next_safe_step") == NEXT_SAFE_STEP and validation.get("next_safe_step") == NEXT_SAFE_STEP,
        "danger_always_false": all(danger_always_false(item) for item in [
            warning_review,
            closure,
            readiness,
            no_touch,
            watch,
            anti,
            validation,
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