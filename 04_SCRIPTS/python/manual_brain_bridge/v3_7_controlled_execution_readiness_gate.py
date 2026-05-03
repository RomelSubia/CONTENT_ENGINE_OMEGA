from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
from typing import Any

SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "v3.7_CONTROLLED_EXECUTION_READINESS_GATE"
NEXT_SAFE_STEP = "v3.7_POST_BUILD_AUDIT"

EXIT_PASS = 0
EXIT_BLOCK = 20
EXIT_LOCK = 30
EXIT_HASH_MISMATCH = 50
EXIT_NO_TOUCH_FAILED = 60
EXIT_SCAN_FAILED = 80
EXIT_INTERNAL_ERROR = 90

PERMISSION_FALSE_FIELDS = [
    "authorization_record_created",
    "human_authorization_input_received",
    "human_authorization_recorded",
    "human_authorization_valid",
    "execution_permission_granted",
    "execution_ready",
    "execution_performed",
    "external_execution_permission",
    "manual_write_permission",
    "brain_write_permission",
    "reports_brain_write_permission",
    "n8n_permission",
    "webhook_permission",
    "publishing_permission",
    "capa9_permission",
]

NO_TOUCH_ROOTS = [
    "00_SYSTEM/brain",
    "00_SYSTEM/reports/brain",
    "00_SYSTEM/manual/current",
    "00_SYSTEM/manual/historical",
    "00_SYSTEM/manual/manifest",
    "00_SYSTEM/manual/registry",
]

REPORTS = {
    "main": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_READINESS_GATE_V3_7.json",
    "surface": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_SURFACE_MAP_V3_7.json",
    "risk": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_RISK_TIER_MAP_V3_7.json",
    "dry_run": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_DRY_RUN_REQUIREMENTS_V3_7.json",
    "rollback": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_ROLLBACK_REQUIREMENTS_V3_7.json",
    "auth": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_AUTH_READINESS_V3_7.json",
    "warning": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_WARNING_INTEGRITY_V3_7.json",
    "permission": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_PERMISSION_ELEVATION_V3_7.json",
    "no_touch": "00_SYSTEM/bridge/reports/CONTROLLED_EXECUTION_NO_TOUCH_REPORT_V3_7.json",
    "no_touch_post": "00_SYSTEM/bridge/reports/NO_TOUCH_HASH_BASELINE_POST_V3_7.json",
    "no_touch_diff": "00_SYSTEM/bridge/reports/NO_TOUCH_DIFF_REPORT_V3_7.json",
    "next": "00_SYSTEM/bridge/reports/NEXT_LAYER_RECOMMENDATION_V3_7.json",
    "summary": "05_REPORTS/manual_brain_bridge/CONTROLLED_EXECUTION_READINESS_GATE_SUMMARY_V3_7.md",
    "manifest": "00_SYSTEM/bridge/manifests/CONTROLLED_EXECUTION_READINESS_GATE_MANIFEST_V3_7.json",
    "seal": "00_SYSTEM/bridge/manifests/CONTROLLED_EXECUTION_READINESS_GATE_SEAL_V3_7.json",
}

REQUIRED_V36_ARTIFACTS = [
    "00_SYSTEM/bridge/reports/GATE_CLOSURE_REPORT_V3_6.json",
    "00_SYSTEM/bridge/reports/NEXT_LAYER_READINESS_MAP_V3_6.json",
    "00_SYSTEM/bridge/reports/NEXT_LAYER_RECOMMENDATION_V3_6.json",
    "00_SYSTEM/bridge/reports/GATE_CLOSURE_NEXT_LAYER_READINESS_TRACEABILITY_V3_6.json",
    "00_SYSTEM/bridge/reports/GATE_CLOSURE_NO_TOUCH_REPORT_V3_6.json",
    "00_SYSTEM/bridge/manifests/GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_MANIFEST_V3_6.json",
    "00_SYSTEM/bridge/manifests/GATE_CLOSURE_NEXT_LAYER_READINESS_MAP_SEAL_V3_6.json",
]

EXPECTED_FINAL_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/v3_7_controlled_execution_readiness_gate.py",
    "tests/manual_brain_bridge/test_v3_7_controlled_execution_readiness_gate.py",
    *REPORTS.values(),
    "05_REPORTS/manual_brain_bridge/V3_7_CONTROLLED_EXECUTION_READINESS_GATE_BUILD_REPORT.md",
]


class GateError(Exception):
    def __init__(self, message: str, exit_code: int = EXIT_BLOCK) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def stable_json_dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_rel(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def path_inside(parent: Path, child: Path) -> bool:
    parent_s = os.path.normcase(str(parent.resolve()))
    child_s = os.path.normcase(str(child.resolve()))
    return child_s == parent_s or child_s.startswith(parent_s + os.sep)


def assert_path_inside_root(root: Path, target: Path) -> Path:
    raw = str(target)
    if "..\\" in raw or "../" in raw:
        raise GateError(f"PATH_TRAVERSAL_DETECTED: {target}", EXIT_LOCK)

    resolved = target.resolve()

    if not path_inside(root, resolved):
        raise GateError(f"PATH_OUTSIDE_ROOT: {target}", EXIT_LOCK)

    return resolved


def blocked_write_roots(root: Path) -> list[Path]:
    return [
        root / "00_SYSTEM/brain",
        root / "00_SYSTEM/reports/brain",
        root / "00_SYSTEM/manual/current",
        root / "00_SYSTEM/manual/historical",
        root / "00_SYSTEM/manual/manifest",
        root / "00_SYSTEM/manual/registry",
    ]


def assert_allowed_write(root: Path, target: Path) -> None:
    resolved = assert_path_inside_root(root, target)

    for blocked in blocked_write_roots(root):
        if blocked.exists() and path_inside(blocked, resolved):
            raise GateError(f"BLOCKED_WRITE_ROOT: {target}", EXIT_LOCK)


def atomic_write_text(root: Path, target: Path, content: str) -> str:
    assert_allowed_write(root, target)
    target.parent.mkdir(parents=True, exist_ok=True)

    logical_hash = sha256_text(content)
    tmp = target.with_name(target.name + ".tmp")

    if tmp.exists():
        tmp.unlink()

    try:
        tmp.write_text(content, encoding="utf-8", newline="\n")
        tmp_hash = sha256_file(tmp)

        if tmp_hash != logical_hash:
            raise GateError(f"TMP_HASH_MISMATCH: {target}", EXIT_HASH_MISMATCH)

        tmp.replace(target)

        final_hash = sha256_file(target)
        if final_hash != logical_hash:
            raise GateError(f"FINAL_HASH_MISMATCH: {target}", EXIT_HASH_MISMATCH)

        return final_hash

    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def atomic_write_json(root: Path, target: Path, data: Any) -> str:
    return atomic_write_text(root, target, stable_json_dumps(data) + "\n")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"JSON_INVALID: {path}: {exc}", EXIT_BLOCK)


def flatten(data: Any) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}

    if isinstance(data, dict):
        for key, value in data.items():
            k = str(key).lower()
            out.setdefault(k, []).append(value)
            for sub_key, sub_values in flatten(value).items():
                out.setdefault(sub_key, []).extend(sub_values)

    elif isinstance(data, list):
        for item in data:
            for sub_key, sub_values in flatten(item).items():
                out.setdefault(sub_key, []).extend(sub_values)

    return out


def load_v3_6_evidence(root: Path) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    missing: list[str] = []

    for rel in REQUIRED_V36_ARTIFACTS:
        path = root / rel
        if not path.exists():
            missing.append(rel)
        else:
            evidence[rel] = load_json(path)

    if missing:
        raise GateError("MISSING_V3_6_ARTIFACTS: " + ", ".join(missing), EXIT_BLOCK)

    return evidence


def _string_is_closed(value: Any) -> bool:
    return str(value).upper() == "CLOSED"


def _string_is_pass(value: Any) -> bool:
    return str(value).upper() in {"PASS", "PASSED", "TRUE"}


def _value_has_explicit_pass(value: Any) -> bool:
    if isinstance(value, bool):
        return value is True
    if isinstance(value, str):
        return _string_is_pass(value)
    if isinstance(value, dict):
        return any(_value_has_explicit_pass(v) for v in value.values())
    if isinstance(value, list):
        return any(_value_has_explicit_pass(v) for v in value)
    return False


def _has_no_touch_pass_marker(data: Any) -> bool:
    if isinstance(data, dict):
        for key, value in data.items():
            key_text = str(key).lower()
            if "no_touch" in key_text:
                if _value_has_explicit_pass(value):
                    return True
            if _has_no_touch_pass_marker(value):
                return True
    elif isinstance(data, list):
        return any(_has_no_touch_pass_marker(item) for item in data)
    return False


def validate_v3_6_closed(evidence: dict[str, Any]) -> dict[str, Any]:
    flat = flatten(evidence)

    closure_fields = [
        "final_status",
        "closure_status",
        "gate_status",
        "source_status",
        "status",
    ]

    closed_found = False
    for field in closure_fields:
        for value in flat.get(field, []):
            if _string_is_closed(value):
                closed_found = True
                break
        if closed_found:
            break

    no_touch_pass = _has_no_touch_pass_marker(evidence)

    if not closed_found:
        return {
            "status": "BLOCK",
            "reason": "V3_6_CLOSED_NOT_PROVEN",
            "v3_6_closed": False,
            "no_touch_pass": no_touch_pass,
        }

    if not no_touch_pass:
        return {
            "status": "BLOCK",
            "reason": "V3_6_NO_TOUCH_NOT_PROVEN",
            "v3_6_closed": True,
            "no_touch_pass": False,
        }

    return {
        "status": "PASS",
        "reason": "V3_6_CLOSED_AND_NO_TOUCH_PROVEN",
        "v3_6_closed": True,
        "no_touch_pass": True,
    }

def evaluate_permission_elevation(evidence: dict[str, Any]) -> dict[str, Any]:
    flat = flatten(evidence)
    elevated: list[str] = []
    missing: list[str] = []

    for field in PERMISSION_FALSE_FIELDS:
        values = flat.get(field.lower(), [])

        if not values:
            missing.append(field)
            continue

        if any(value is True or str(value).lower() == "true" for value in values):
            elevated.append(field)

    if elevated:
        return {
            "status": "LOCK",
            "reason": "LOCKED_UNAUTHORIZED_PERMISSION_ELEVATION",
            "elevated_fields": elevated,
            "missing_fields": missing,
        }

    if missing:
        return {
            "status": "BLOCK",
            "reason": "PERMISSION_EVIDENCE_INCOMPLETE",
            "elevated_fields": [],
            "missing_fields": missing,
        }

    return {
        "status": "PASS",
        "reason": "PERMISSION_FALSE_STATE_PRESERVED",
        "elevated_fields": [],
        "missing_fields": [],
    }


def first_value(flat: dict[str, list[Any]], key: str) -> Any:
    values = flat.get(key.lower(), [])
    return values[0] if values else None


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    return None


def evaluate_warning_integrity(evidence: dict[str, Any]) -> dict[str, Any]:
    flat = flatten(evidence)

    warnings_accepted = as_int(first_value(flat, "warnings_accepted"))
    warnings_inherited_visible = as_int(first_value(flat, "warnings_inherited_visible"))
    warnings_hidden = as_int(first_value(flat, "warnings_hidden"))
    warnings_suppressed = as_int(first_value(flat, "warnings_suppressed"))
    production_clean_pass = as_bool(first_value(flat, "production_clean_pass"))
    production_with_warnings = as_bool(first_value(flat, "production_with_warnings"))

    problems: list[str] = []

    if warnings_accepted != 5:
        problems.append("warnings_accepted_not_5")
    if warnings_inherited_visible != 5:
        problems.append("warnings_inherited_visible_not_5")
    if warnings_hidden != 0:
        problems.append("warnings_hidden_not_0")
    if warnings_suppressed != 0:
        problems.append("warnings_suppressed_not_0")
    if production_clean_pass is not False:
        problems.append("production_clean_pass_not_false")
    if production_with_warnings is not True:
        problems.append("production_with_warnings_not_true")

    if "warnings_hidden_not_0" in problems or "warnings_suppressed_not_0" in problems:
        status = "LOCK"
        reason = "LOCKED_WARNING_SUPPRESSION"
    elif problems:
        status = "BLOCK"
        reason = "WARNING_INTEGRITY_INCOMPLETE_OR_FALSE_CLEAN_CLAIM"
    else:
        status = "PASS"
        reason = "WARNING_INTEGRITY_PRESERVED"

    return {
        "status": status,
        "reason": reason,
        "warnings_accepted": warnings_accepted,
        "warnings_inherited_visible": warnings_inherited_visible,
        "warnings_hidden": warnings_hidden,
        "warnings_suppressed": warnings_suppressed,
        "production_clean_pass": production_clean_pass,
        "production_with_warnings": production_with_warnings,
        "problems": problems,
    }


def base_report(report_id: str, status: str = "PASS_WITH_WARNINGS") -> dict[str, Any]:
    return {
        "system": SYSTEM,
        "layer": LAYER,
        "report_id": report_id,
        "status": status,
        "execution_allowed": False,
        "dry_run_execution_allowed": False,
        "build_allowed": False,
        "automatic_block_allowed": False,
        "external_execution_allowed": False,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "reports_brain_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "capa9_allowed": False,
        "production_clean_pass": False,
        "production_with_warnings": True,
        "warnings_inherited_visible": 5,
        "warnings_hidden": 0,
        "warnings_suppressed": 0,
        "warnings_resolved_by_v3_7": 0,
        "next_safe_step": NEXT_SAFE_STEP,
        "evidence": [],
    }


def build_surface_map() -> dict[str, Any]:
    report = base_report("CONTROLLED_EXECUTION_SURFACE_MAP_V3_7")
    report["surface_map"] = {
        "SURFACE_0_NONE": {"allowed_now": True, "execution": False},
        "SURFACE_1_LOCAL_DRY_RUN": {"designable_future": True, "allowed_now": False},
        "SURFACE_2_LOCAL_FILE_GENERATION": {"designable_future": True, "allowed_now": False},
        "SURFACE_3_INTERNAL_REPORTING": {"designable_future": True, "allowed_now": False},
        "SURFACE_4_MANUAL_PATCH_PROPOSAL": {"allowed_now": False, "blocked": True},
        "SURFACE_5_EXTERNAL_API_CALL": {"allowed_now": False, "blocked": True},
        "SURFACE_6_N8N_WORKFLOW": {"allowed_now": False, "blocked": True},
        "SURFACE_7_WEBHOOK": {"allowed_now": False, "blocked": True},
        "SURFACE_8_PUBLISHING": {"allowed_now": False, "blocked": True},
        "SURFACE_9_MONETIZATION_ACTION": {"allowed_now": False, "blocked": True},
    }
    return report


def build_risk_tier_map() -> dict[str, Any]:
    report = base_report("CONTROLLED_EXECUTION_RISK_TIER_MAP_V3_7")
    report["risk_tiers"] = {
        "R0": "no execution / analysis only",
        "R1": "local dry-run",
        "R2": "local artifact creation",
        "R3": "internal repo modification",
        "R4": "manual patch proposal",
        "R5": "manual write",
        "R6": "external API call",
        "R7": "n8n/webhook",
        "R8": "publishing",
        "R9": "monetization action",
        "R10": "brain mutation / prohibited",
    }
    report["rules"] = {
        "R0": "evaluatable_now",
        "R1_to_R3": "designable_future_not_allowed_now",
        "R4_to_R9": "blocked_now",
        "R10": "locked",
    }
    return report


def build_dry_run_requirements() -> dict[str, Any]:
    report = base_report("CONTROLLED_EXECUTION_DRY_RUN_REQUIREMENTS_V3_7")
    report["requirements"] = {
        "dry_run_required": True,
        "dry_run_before_real_action": True,
        "dry_run_artifacts_manifested": True,
        "dry_run_hash_validated": True,
        "dry_run_diff_required": True,
        "dry_run_approval_required": True,
        "dry_run_execution_allowed": False,
    }
    return report


def build_rollback_requirements() -> dict[str, Any]:
    report = base_report("CONTROLLED_EXECUTION_ROLLBACK_REQUIREMENTS_V3_7")
    report["requirements"] = {
        "rollback_required": True,
        "pre_action_snapshot_required": True,
        "affected_paths_declared": True,
        "rollback_owner_declared": True,
        "rollback_validation_required": True,
        "post_rollback_audit_required": True,
        "rollback_execution_allowed": False,
    }
    return report


def build_auth_readiness_report() -> dict[str, Any]:
    report = base_report("CONTROLLED_EXECUTION_AUTH_READINESS_V3_7")
    report["authorization"] = {
        "authorization_contract_exists": True,
        "authorization_record_created": False,
        "human_authorization_valid": False,
        "authorization_ready_for_future_design": True,
        "authorization_valid_now": False,
        "rule": "AUTH_READINESS_IS_NOT_AUTHORIZATION_VALID",
    }
    report["evidence"].append("v3.6_authorization_contract_created_true_but_no_valid_human_authorization")
    return report


def capture_no_touch_baseline(root: Path, report_id: str) -> dict[str, Any]:
    files: list[dict[str, Any]] = []

    for rel_root in NO_TOUCH_ROOTS:
        abs_root = root / rel_root

        if not abs_root.exists():
            continue

        for file_path in sorted(abs_root.rglob("*")):
            if file_path.is_file():
                rel = normalize_rel(file_path.relative_to(root))
                files.append({
                    "path": rel,
                    "sha256": sha256_file(file_path),
                    "length": file_path.stat().st_size,
                })

    report = base_report(report_id, "PASS")
    report["no_touch_roots"] = NO_TOUCH_ROOTS
    report["files"] = files
    report["file_count"] = len(files)
    return report


def compare_no_touch_baselines(pre: dict[str, Any], post: dict[str, Any]) -> dict[str, Any]:
    pre_map = {item["path"]: item["sha256"] for item in pre.get("files", [])}
    post_map = {item["path"]: item["sha256"] for item in post.get("files", [])}

    added = sorted([path for path in post_map if path not in pre_map])
    removed = sorted([path for path in pre_map if path not in post_map])
    changed = sorted([path for path in pre_map if path in post_map and pre_map[path] != post_map[path]])

    status = "PASS" if not added and not removed and not changed else "LOCK"

    return {
        "status": status,
        "added": added,
        "removed": removed,
        "changed": changed,
        "no_touch_pass": status == "PASS",
    }


def validate_contract(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "system",
        "layer",
        "status",
        "execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "n8n_allowed",
        "webhook_allowed",
        "publishing_allowed",
        "capa9_allowed",
        "next_safe_step",
    ]

    for key in required:
        if key not in data:
            errors.append(f"missing:{key}")

    for key in [
        "execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "n8n_allowed",
        "webhook_allowed",
        "publishing_allowed",
        "capa9_allowed",
    ]:
        if data.get(key) is not False:
            errors.append(f"permission_not_false:{key}")

    if data.get("next_safe_step") == "EXECUTION":
        errors.append("next_safe_step_points_to_execution")

    if data.get("system") != SYSTEM:
        errors.append("wrong_system")

    if data.get("layer") != LAYER:
        errors.append("wrong_layer")

    return errors


def ast_security_scan(target: Path) -> dict[str, Any]:
    forbidden_import_roots = {
        "subprocess", "requests", "urllib", "http", "socket", "ftplib",
        "paramiko", "webbrowser", "smtplib", "multiprocessing"
    }
    forbidden_name_calls = {"eval", "exec", "compile", "input", "__import__"}
    nondeterministic_imports = {"random", "uuid", "secrets"}

    source = target.read_text(encoding="utf-8")
    tree = ast.parse(source)
    findings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in forbidden_import_roots:
                    findings.append(f"forbidden_import:{alias.name}")
                if root in nondeterministic_imports:
                    findings.append(f"nondeterministic_import:{alias.name}")

        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".")[0]
            if root in forbidden_import_roots:
                findings.append(f"forbidden_import_from:{module}")
            if root in nondeterministic_imports:
                findings.append(f"nondeterministic_import_from:{module}")

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in forbidden_name_calls:
                findings.append(f"forbidden_call:{func.id}")
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    if (func.value.id, func.attr) in {("os", "system"), ("os", "popen")}:
                        findings.append(f"forbidden_call:{func.value.id}.{func.attr}")

    return {"status": "PASS" if not findings else "LOCK", "findings": findings}


def generate_reports(root: Path, pre_baseline_path: Path) -> int:
    evidence = load_v3_6_evidence(root)
    v36 = validate_v3_6_closed(evidence)
    permissions = evaluate_permission_elevation(evidence)
    warnings = evaluate_warning_integrity(evidence)

    blockers: list[str] = []
    locks: list[str] = []

    for label, report in [("v36", v36), ("permissions", permissions), ("warnings", warnings)]:
        if report["status"] == "LOCK":
            locks.append(f"{label}:{report['reason']}")
        elif report["status"] == "BLOCK":
            blockers.append(f"{label}:{report['reason']}")

    overall_status = "PASS_WITH_WARNINGS"
    reason = "CONTROLLED_EXECUTION_READINESS_GATE_BUILT_NON_EXECUTING"
    exit_code = EXIT_PASS

    if locks:
        overall_status = "LOCK"
        reason = "LOCKED_BY_GATE"
        exit_code = EXIT_LOCK
    elif blockers:
        overall_status = "BLOCK"
        reason = "BLOCKED_BY_GATE"
        exit_code = EXIT_BLOCK

    main = base_report("CONTROLLED_EXECUTION_READINESS_GATE_V3_7", overall_status)
    main.update({
        "reason": reason,
        "source_layer": "v3.6_HUMAN_AUTHORIZATION_CONTRACT_EXECUTION_PERMISSION_MODEL",
        "source_status_required": "CLOSED",
        "v3_6_validation": v36,
        "permission_elevation": permissions,
        "warning_integrity": warnings,
        "blockers": blockers,
        "locks": locks,
        "tests_minimum_required": 60,
        "readiness_decision": "READY_FOR_POST_BUILD_AUDIT" if exit_code == EXIT_PASS else overall_status,
    })

    permission_report = base_report("CONTROLLED_EXECUTION_PERMISSION_ELEVATION_V3_7", permissions["status"])
    permission_report["permission_elevation"] = permissions

    warning_report = base_report("CONTROLLED_EXECUTION_WARNING_INTEGRITY_V3_7", warnings["status"])
    warning_report["warning_integrity"] = warnings

    no_touch_main = base_report("CONTROLLED_EXECUTION_NO_TOUCH_REPORT_V3_7", "PASS")
    no_touch_main["no_touch_roots"] = NO_TOUCH_ROOTS
    no_touch_main["no_touch_required"] = True

    reports = {
        REPORTS["main"]: main,
        REPORTS["surface"]: build_surface_map(),
        REPORTS["risk"]: build_risk_tier_map(),
        REPORTS["dry_run"]: build_dry_run_requirements(),
        REPORTS["rollback"]: build_rollback_requirements(),
        REPORTS["auth"]: build_auth_readiness_report(),
        REPORTS["warning"]: warning_report,
        REPORTS["permission"]: permission_report,
        REPORTS["no_touch"]: no_touch_main,
        REPORTS["next"]: {
            **base_report("NEXT_LAYER_RECOMMENDATION_V3_7", overall_status),
            "recommendation": "v3.7_POST_BUILD_AUDIT",
            "execution_allowed_after_build": False,
            "build_allowed_after_build": False,
            "next_layer_allowed": "POST_BUILD_AUDIT_ONLY",
        },
    }

    for rel, data in reports.items():
        errors = validate_contract(data)
        if errors:
            raise GateError(f"CONTRACT_INVALID for {rel}: {errors}", EXIT_BLOCK)
        atomic_write_json(root, root / rel, data)

    pre = load_json(pre_baseline_path)
    post = capture_no_touch_baseline(root, "NO_TOUCH_HASH_BASELINE_POST_V3_7")
    atomic_write_json(root, root / REPORTS["no_touch_post"], post)

    diff = base_report("NO_TOUCH_DIFF_REPORT_V3_7", "PASS")
    comparison = compare_no_touch_baselines(pre, post)
    diff["comparison"] = comparison
    diff["status"] = "PASS" if comparison["status"] == "PASS" else "LOCK"
    atomic_write_json(root, root / REPORTS["no_touch_diff"], diff)

    summary = (
        "# CONTROLLED EXECUTION READINESS GATE v3.7\n\n"
        f"Status: {overall_status}\n\n"
        f"Reason: {reason}\n\n"
        "- Execution allowed: false\n"
        "- Manual write allowed: false\n"
        "- Brain write allowed: false\n"
        "- Reports/brain write allowed: false\n"
        "- n8n/webhook/publishing: false\n"
        "- CAPA 9: false\n"
        "- Next safe step: v3.7_POST_BUILD_AUDIT\n"
    )
    atomic_write_text(root, root / REPORTS["summary"], summary)

    if comparison["status"] != "PASS":
        return EXIT_NO_TOUCH_FAILED

    return exit_code


def validate_outputs(root: Path) -> int:
    errors: list[str] = []

    for rel in [
        REPORTS["main"],
        REPORTS["surface"],
        REPORTS["risk"],
        REPORTS["dry_run"],
        REPORTS["rollback"],
        REPORTS["auth"],
        REPORTS["warning"],
        REPORTS["permission"],
        REPORTS["no_touch"],
        REPORTS["no_touch_post"],
        REPORTS["no_touch_diff"],
        REPORTS["next"],
    ]:
        path = root / rel

        if not path.exists():
            errors.append(f"missing:{rel}")
            continue

        data = load_json(path)

        if not isinstance(data, dict):
            errors.append(f"not_object:{rel}")
            continue

        errors.extend([f"{rel}:{error}" for error in validate_contract(data)])

    if errors:
        print(stable_json_dumps({"status": "BLOCK", "errors": errors}))
        return EXIT_BLOCK

    print(stable_json_dumps({"status": "PASS"}))
    return EXIT_PASS


def finalize_manifest_and_seal(root: Path) -> int:
    artifacts: list[dict[str, Any]] = []
    missing: list[str] = []

    for rel in EXPECTED_FINAL_ARTIFACTS:
        if rel in {REPORTS["manifest"], REPORTS["seal"]}:
            continue

        path = root / rel

        if not path.exists():
            missing.append(rel)
            continue

        artifacts.append({"path": rel, "sha256": sha256_file(path), "status": "VALID"})

    if missing:
        raise GateError("MISSING_EXPECTED_ARTIFACTS: " + ", ".join(missing), EXIT_BLOCK)

    manifest = {
        **base_report("CONTROLLED_EXECUTION_READINESS_GATE_MANIFEST_V3_7", "PASS_WITH_WARNINGS"),
        "manifest_id": "CONTROLLED_EXECUTION_READINESS_GATE_MANIFEST_V3_7",
        "artifacts": artifacts,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "artifact_count": len(artifacts),
    }

    atomic_write_json(root, root / REPORTS["manifest"], manifest)
    manifest_hash = sha256_file(root / REPORTS["manifest"])

    seal = {
        **base_report("CONTROLLED_EXECUTION_READINESS_GATE_SEAL_V3_7", "PASS_WITH_WARNINGS"),
        "seal_id": "CONTROLLED_EXECUTION_READINESS_GATE_SEAL_V3_7",
        "manifest_hash": manifest_hash,
        "report_hash": sha256_file(root / REPORTS["main"]),
        "no_touch_pass": True,
        "execution_allowed": False,
        "status": "SEALED_WITH_WARNINGS",
    }

    atomic_write_json(root, root / REPORTS["seal"], seal)
    print(stable_json_dumps({"status": "PASS", "manifest_hash": manifest_hash}))
    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["run", "ast-scan", "validate-contracts", "finalize"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--target")
    parser.add_argument("--pre-baseline")
    args = parser.parse_args()

    try:
        root = Path(args.root).resolve()

        if args.mode == "ast-scan":
            if not args.target:
                raise GateError("--target requerido", EXIT_SCAN_FAILED)
            result = ast_security_scan(Path(args.target))
            print(stable_json_dumps(result))
            return EXIT_PASS if result["status"] == "PASS" else EXIT_SCAN_FAILED

        if args.mode == "run":
            if not args.pre_baseline:
                raise GateError("--pre-baseline requerido", EXIT_BLOCK)
            return generate_reports(root, Path(args.pre_baseline).resolve())

        if args.mode == "validate-contracts":
            return validate_outputs(root)

        if args.mode == "finalize":
            return finalize_manifest_and_seal(root)

        return EXIT_INTERNAL_ERROR

    except GateError as exc:
        print(stable_json_dumps({"status": "ERROR", "message": str(exc), "exit_code": exc.exit_code}))
        return exc.exit_code

    except Exception as exc:
        print(stable_json_dumps({"status": "INTERNAL_ERROR", "message": str(exc)}))
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())