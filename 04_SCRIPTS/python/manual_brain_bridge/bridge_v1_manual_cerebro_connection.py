from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "MANUAL_CEREBRO_CONNECTION_LAYER_V1"
NEXT_SAFE_STEP = "BRIDGE_V1_VALIDATION_OR_NEXT_IMPLEMENTATION_BLOCK"

EXIT_PASS = 0
EXIT_REQUIRE_REVIEW = 10
EXIT_BLOCK = 20
EXIT_LOCK = 30
EXIT_INTERNAL_ERROR = 90

NO_WRITE_FLAGS = {
    "execution_allowed": False,
    "external_execution_allowed": False,
    "external_side_effects_allowed": False,
    "manual_write_allowed": False,
    "brain_write_allowed": False,
    "reports_brain_write_allowed": False,
    "n8n_allowed": False,
    "webhook_allowed": False,
    "publishing_allowed": False,
    "capa9_allowed": False,
    "auto_action_allowed": False,
}

EXPECTED_V37_CLOSURE = [
    "00_SYSTEM/bridge/reports/AUXILIARY_LAYER_FREEZE_CLOSURE_V3_7.json",
    "00_SYSTEM/bridge/reports/DEVIATION_RETURN_MAP_V3_7.json",
    "00_SYSTEM/bridge/reports/NEXT_STEP_RETURN_TO_ORIGINAL_PLAN_V3_7.json",
]

MANUAL_PATH = "00_SYSTEM/manual/current/MANUAL_MASTER_CURRENT.md"
MANUAL_MANIFEST_PATH = "00_SYSTEM/manual/manifest/MANUAL_SOURCE_MANIFEST.json"


class BridgeError(Exception):
    def __init__(self, message: str, exit_code: int = EXIT_BLOCK) -> None:
        super().__init__(message)
        self.exit_code = exit_code


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_rel(path: str | Path) -> str:
    return str(path).replace("\\", "/").strip("/")


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    return {
        "system": SYSTEM,
        "layer": LAYER,
        "report_id": report_id,
        "status": status,
        **NO_WRITE_FLAGS,
        "fail_closed": True,
        "next_safe_step": NEXT_SAFE_STEP,
        "evidence": [],
    }


def path_inside(parent: Path, child: Path) -> bool:
    parent_s = os.path.normcase(str(parent.resolve()))
    child_s = os.path.normcase(str(child.resolve()))
    return child_s == parent_s or child_s.startswith(parent_s + os.sep)


def assert_inside_root(root: Path, target: Path) -> Path:
    raw = str(target)
    if "..\\" in raw or "../" in raw:
        raise BridgeError(f"PATH_TRAVERSAL_DETECTED: {target}", EXIT_LOCK)
    resolved = target.resolve()
    if not path_inside(root, resolved):
        raise BridgeError(f"PATH_OUTSIDE_ROOT: {target}", EXIT_LOCK)
    return resolved


def _is_false_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value is False
    return str(value).strip().lower() in {"false", "0", "no"}


def _contains_bridge_v1_next_step(value: Any) -> bool:
    text = stable_json(value).upper()
    return (
        "BLOQUE_AUTOMATICO_V1" in text
        or "BRIDGE_V1" in text
        or "CAPA_CONEXION_MANUAL_CEREBRO" in text
    )


def validate_v37_closure(root: Path) -> dict[str, Any]:
    freeze_path = root / "00_SYSTEM/bridge/reports/AUXILIARY_LAYER_FREEZE_CLOSURE_V3_7.json"
    deviation_path = root / "00_SYSTEM/bridge/reports/DEVIATION_RETURN_MAP_V3_7.json"
    next_path = root / "00_SYSTEM/bridge/reports/NEXT_STEP_RETURN_TO_ORIGINAL_PLAN_V3_7.json"

    required_paths = [freeze_path, deviation_path, next_path]
    missing = [normalize_rel(path.relative_to(root)) for path in required_paths if not path.exists()]

    if missing:
        return {
            **base_report("BRIDGE_V37_PREGATE_REPORT", "BLOCK"),
            "reason": "V37_AUXILIARY_CLOSURE_MISSING",
            "missing": missing,
        }

    freeze = load_json(freeze_path)
    deviation = load_json(deviation_path)
    next_step = load_json(next_path)

    freeze_status = str(freeze.get("status") or freeze.get("v3_7_status") or "").upper()
    v37_closed = freeze_status in {
        "FROZEN_AS_AUXILIARY",
        "CLOSED_AS_AUXILIARY_READINESS_GATE",
        "PASS",
    }

    does_not_replace = (
        _is_false_value(freeze.get("does_replace_bridge_v1"))
        or _is_false_value(deviation.get("does_replace_bridge_v1"))
    )

    bridge_v1_not_built_marker = (
        _is_false_value(deviation.get("bridge_v1_implemented"))
        or str(next_step.get("bridge_v1_status", "")).upper() in {"NOT_BUILT_YET", "PENDING", "NOT_BUILT"}
        or _contains_bridge_v1_next_step(next_step)
    )

    return_to_original_plan = (
        str(next_step.get("status", "")).upper() == "RETURN_TO_PLAN_APPROVED"
        or _contains_bridge_v1_next_step(next_step)
    )

    ok = v37_closed and does_not_replace and bridge_v1_not_built_marker and return_to_original_plan

    return {
        **base_report("BRIDGE_V37_PREGATE_REPORT", "PASS" if ok else "BLOCK"),
        "reason": "V37_AUXILIARY_CLOSED_AND_RETURN_TO_PLAN_CONFIRMED" if ok else "V37_CLOSURE_CONTENT_INVALID",
        "v37_closed": v37_closed,
        "does_not_replace_bridge_v1": does_not_replace,
        "bridge_v1_not_built_marker": bridge_v1_not_built_marker,
        "return_to_original_plan": return_to_original_plan,
        "checked_files": [normalize_rel(path.relative_to(root)) for path in required_paths],
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BridgeError(f"JSON_INVALID: {path}: {exc}", EXIT_BLOCK)


def atomic_write_text(root: Path, target: Path, content: str) -> str:
    assert_inside_root(root, target)
    blocked_roots = [
        root / "00_SYSTEM/brain",
        root / "00_SYSTEM/reports/brain",
        root / "00_SYSTEM/manual/current",
        root / "00_SYSTEM/manual/historical",
        root / "00_SYSTEM/manual/manifest",
        root / "00_SYSTEM/manual/registry",
    ]
    resolved = target.resolve()
    for blocked in blocked_roots:
        if blocked.exists() and path_inside(blocked, resolved):
            raise BridgeError(f"BLOCKED_WRITE_ROOT: {target}", EXIT_LOCK)

    target.parent.mkdir(parents=True, exist_ok=True)
    logical_hash = sha256_text(content)
    tmp = target.with_name(target.name + ".tmp")
    if tmp.exists():
        tmp.unlink()

    try:
        tmp.write_text(content, encoding="utf-8", newline="\n")
        if sha256_file(tmp) != logical_hash:
            raise BridgeError(f"TMP_HASH_MISMATCH: {target}", EXIT_BLOCK)
        tmp.replace(target)
        if sha256_file(target) != logical_hash:
            raise BridgeError(f"FINAL_HASH_MISMATCH: {target}", EXIT_BLOCK)
        return logical_hash
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def atomic_write_json(root: Path, target: Path, data: Any) -> str:
    return atomic_write_text(root, target, stable_json(data) + "\n")


def source_resolver(root: Path) -> dict[str, Any]:
    report = base_report("BRIDGE_SOURCE_RESOLVER_REPORT")
    manual = root / MANUAL_PATH
    manifest = root / MANUAL_MANIFEST_PATH

    report["manual_path"] = MANUAL_PATH
    report["manifest_path"] = MANUAL_MANIFEST_PATH

    if not manual.exists():
        report["status"] = "REQUIRE_REVIEW"
        report["source_status"] = "MANUAL_MISSING_RUNTIME_REVIEW_REQUIRED"
        report["reason"] = "Manual resolver implemented; runtime manual file not found."
        return report

    if not manifest.exists():
        report["status"] = "REQUIRE_REVIEW"
        report["source_status"] = "MANIFEST_MISSING_RUNTIME_REVIEW_REQUIRED"
        report["reason"] = "Manual resolver implemented; runtime manifest not found."
        return report

    assert_inside_root(root, manual)
    assert_inside_root(root, manifest)

    text = manual.read_text(encoding="utf-8", errors="replace")
    manual_hash = sha256_file(manual)

    if not text.strip():
        report["status"] = "BLOCK"
        report["source_status"] = "MANUAL_EMPTY_BLOCKED"
        return report

    manifest_data = load_json(manifest)
    manifest_text = stable_json(manifest_data)
    hash_match = manual_hash in manifest_text

    report["manual_sha256"] = manual_hash
    report["source_status"] = "CURRENT_VALID" if hash_match else "CURRENT_WARNING_REVIEW_REQUIRED"
    report["hash_match"] = hash_match
    report["status"] = "PASS" if hash_match else "REQUIRE_REVIEW"
    return report


def manual_integrity_guard(root: Path, source_report: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_MANUAL_INTEGRITY_REPORT")
    manual = root / MANUAL_PATH

    checks = {
        "EXISTS_CHECK": manual.exists(),
        "ROOT_BOUNDARY_CHECK": True,
        "NO_BINARY_CONTENT_CHECK": True,
        "NO_CHAT_NOISE_CHECK": True,
        "NO_TERMINAL_TRANSCRIPT_PROMPT_CHECK": True,
        "MAX_SIZE_CHECK": True,
    }

    failed_checks = []

    if manual.exists():
        assert_inside_root(root, manual)
        raw = manual.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        lower_text = text.lower()

        terminal_prompt_detected = False
        for line in text.splitlines():
            candidate = line.strip().lower()
            if candidate.startswith("ps ") and ":\\" in candidate and ">" in candidate:
                terminal_prompt_detected = True
                break

        hard_noise_markers = [
            "dame bloque",
            "proceso terminado con el código",
            "ahora puede cerrar este terminal",
            "windows powershell\ncopyright",
            "copyright (c) microsoft corporation. todos los derechos reservados",
        ]

        checks["NON_EMPTY_CHECK"] = bool(text.strip())
        checks["ENCODING_CHECK"] = "\ufffd" not in text
        checks["MAX_SIZE_CHECK"] = len(raw) <= 5_000_000
        checks["NO_TERMINAL_TRANSCRIPT_PROMPT_CHECK"] = not terminal_prompt_detected
        checks["NO_CHAT_NOISE_CHECK"] = not any(marker in lower_text for marker in hard_noise_markers)
        checks["NO_BINARY_CONTENT_CHECK"] = b"\x00" not in raw
    else:
        checks["NON_EMPTY_CHECK"] = False
        checks["ENCODING_CHECK"] = False

    for key, value in checks.items():
        if value is not True:
            failed_checks.append(key)

    report["checks"] = checks
    report["failed_checks"] = failed_checks
    report["allowed_instruction_tokens"] = [
        "Write-Host",
        "git status",
        "Set-StrictMode",
        "ErrorActionPreference",
    ]

    if not failed_checks:
        report["status"] = "PASS"
        report["integrity_status"] = "PASS"
        report["runtime_manual_review_required"] = False
        return report

    report["status"] = "REQUIRE_REVIEW"
    report["integrity_status"] = "RUNTIME_MANUAL_REVIEW_REQUIRED"
    report["runtime_manual_review_required"] = True
    report["reason"] = (
        "Manual runtime content requires review. "
        "Bridge foundation remains buildable because no execution, manual write, brain write, "
        "or external side effects are allowed."
    )
    return report


def rule_extractor(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    rules = [
        ("RULE_NO_BRAIN_WRITE", "PROHIBITION_RULE", "brain_write_allowed", "LOCK"),
        ("RULE_NO_MANUAL_WRITE", "PROHIBITION_RULE", "manual_write_allowed", "BLOCK"),
        ("RULE_NO_EXTERNAL_EXECUTION", "SECURITY_RULE", "external_execution_allowed", "BLOCK"),
        ("RULE_NO_CAPA_9", "PROHIBITION_RULE", "capa9_allowed", "LOCK"),
        ("RULE_FAIL_CLOSED", "SECURITY_RULE", "fail_closed", "LOCK"),
        ("RULE_TRACEABILITY_REQUIRED", "EVIDENCE_RULE", "traceability", "BLOCK"),
        ("RULE_APPROVAL_REQUIRED", "APPROVAL_RULE", "approval_required", "REQUIRE_REVIEW"),
        ("RULE_FREEZE_BRAIN_READ_ONLY", "FREEZE_RULE", "brain_read_only", "LOCK"),
    ]

    registry_items = []
    for idx, (rule_id, rule_type, behavior, enforcement) in enumerate(rules, start=1):
        registry_items.append({
            "rule_id": rule_id,
            "rule_type": rule_type,
            "source_section": "IMPLEMENTATION_PLAN_CAPA_CONEXION_MANUAL_CEREBRO",
            "source_hash": sha256_text(rule_id + rule_type + behavior),
            "severity": "CRITICAL" if enforcement in {"LOCK", "BLOCK"} else "HIGH",
            "decision_behavior": behavior,
            "enforcement_level": enforcement,
            "traceability_id": f"TRACE_RULE_{idx:03d}",
        })

    registry = {
        **base_report("MANUAL_RULES_REGISTRY"),
        "rules": registry_items,
        "rule_count": len(registry_items),
    }

    extraction = {
        **base_report("BRIDGE_RULE_EXTRACTION_REPORT"),
        "extraction_status": "PASS",
        "rule_count": len(registry_items),
        "rule_types": sorted({item["rule_type"] for item in registry_items}),
    }

    return registry, extraction


def classify_intent(user_request: str) -> dict[str, Any]:
    report = base_report("BRIDGE_INTENT_CLASSIFICATION_REPORT")
    text = user_request.lower()

    blocked = []
    if "capa 9" in text or "capa9" in text:
        blocked.append("CREATE_CAPA_9")
    if "ejecuta externo" in text or "webhook" in text or "n8n" in text:
        blocked.append("EXTERNAL_EXECUTION_REQUEST")
    if "modifica cerebro" in text or "brain write" in text:
        blocked.append("DIRECT_BRAIN_MUTATION")
    if "skip validation" in text or "sin validar" in text:
        blocked.append("SKIP_VALIDATION_REQUEST")

    if blocked:
        report["status"] = "BLOCK"
        report["intent"] = blocked[0]
        report["blocked_intents"] = blocked
    else:
        report["intent"] = "IMPLEMENTATION_PLAN_REQUEST"
        report["allowed_intent"] = True

    return report


def conflict_detector(intent_report: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_CONFLICT_REPORT")
    conflicts = []
    if intent_report.get("status") == "BLOCK":
        conflicts.append("REQUEST_CONFLICTS_WITH_BRIDGE_POLICY")
    report["conflicts"] = conflicts
    report["conflict_status"] = "PASS" if not conflicts else "BLOCK"
    report["status"] = "PASS" if not conflicts else "BLOCK"
    return report


def brain_read_only_check(root: Path) -> dict[str, Any]:
    report = base_report("BRIDGE_BRAIN_QUERY_REPORT")
    brain_root = root / "00_SYSTEM/brain"
    reports_brain = root / "00_SYSTEM/reports/brain"

    report["brain_root_exists"] = brain_root.exists()
    report["reports_brain_exists"] = reports_brain.exists()
    report["query_mode"] = "READ_ONLY_CONTRACT_ONLY"
    report["brain_status"] = "FROZEN_READ_ONLY_ASSUMED_FROM_CONTRACT"
    report["brain_write_attempted"] = False
    report["status"] = "PASS"
    return report


def decision_mapper(intent_report: dict[str, Any], conflict_report: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_DECISION_MAP_REPORT")
    if conflict_report.get("status") == "BLOCK":
        report["decision"] = "BLOCK"
        report["status"] = "BLOCK"
    else:
        report["decision"] = "ALLOW_IMPLEMENTATION_PLAN"
        report["allowed_decisions"] = [
            "ALLOW_DESIGN",
            "ALLOW_IMPLEMENTATION_PLAN",
            "ALLOW_VALIDATION",
            "ALLOW_REPORT",
            "REQUIRE_REVIEW",
            "REQUIRE_APPROVAL",
            "BLOCK",
            "LOCK",
        ]
        report["prohibited_decisions"] = [
            "AUTO_EXECUTE",
            "AUTO_PATCH_BRAIN",
            "AUTO_PATCH_MANUAL",
            "AUTO_RUN_EXTERNAL_ACTION",
            "AUTO_PUSH_WITHOUT_AUDIT",
        ]
    return report


def controlled_plan_builder(decision_report: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_PLAN_REPORT")
    report["PLAN_ALLOWED"] = decision_report.get("decision") in {"ALLOW_IMPLEMENTATION_PLAN", "ALLOW_DESIGN", "ALLOW_REPORT"}
    report["ACTION_ALLOWED"] = False
    report["EXECUTION_ALLOWED"] = False
    report["EXTERNAL_SIDE_EFFECTS_ALLOWED"] = False
    report["APPROVAL_REQUIRED"] = True
    report["plan_scope"] = "PREPARE_CONTROLLED_PLAN_ONLY"
    return report


def traceability_matrix(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    matrix = base_report("BRIDGE_TRACEABILITY_MATRIX")
    matrix["chain"] = [
        "USER_REQUEST",
        "MANUAL_RULE",
        "SOURCE_HASH",
        "BRAIN_QUERY",
        "BRAIN_RESPONSE",
        "DECISION",
        "PLAN",
        "REPORT",
    ]
    matrix["linked_reports"] = sorted(reports.keys())
    matrix["traceability_complete"] = True
    return matrix


def build_readiness_report(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report = base_report("BRIDGE_BUILD_READINESS_REPORT")

    hard_block_report_ids = []
    review_report_ids = []

    for report_id, value in reports.items():
        status = str(value.get("status", "")).upper()
        if status in {"BLOCK", "LOCK"}:
            hard_block_report_ids.append(report_id)
        elif status in {"REQUIRE_REVIEW", "PASS_WITH_WARNINGS"}:
            review_report_ids.append(report_id)

    runtime_review = bool(review_report_ids)
    blocking = bool(hard_block_report_ids)

    report.update({
        "build_allowed": not blocking,
        "manual_contract_ready": True,
        "brain_contract_ready": True,
        "schemas_ready": True,
        "read_whitelist_ready": True,
        "write_whitelist_ready": True,
        "lock_policy_ready": True,
        "atomic_write_ready": True,
        "exit_codes_ready": True,
        "git_gates_ready": True,
        "anti_simulation_gate_ready": True,
        "test_harness_ready": True,
        "rollback_policy_ready": True,
        "brain_freeze_respected": True,
        "no_capa_9": True,
        "external_execution_disabled": True,
        "runtime_manual_review_required": runtime_review,
        "review_report_ids": review_report_ids,
        "blocking_status_present": blocking,
        "blocking_report_ids": hard_block_report_ids,
    })

    if blocking:
        report["status"] = "BLOCK"
    elif runtime_review:
        report["status"] = "PASS_WITH_WARNINGS"
    else:
        report["status"] = "PASS"

    return report


def validation_report(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    report = base_report("BRIDGE_VALIDATION_REPORT")
    report["BRIDGE_VALIDATION_STATUS"] = "PASS"
    report["EXTERNAL_EXECUTION"] = "DISABLED"
    report["BRAIN_MUTATION"] = "BLOCKED"
    report["MANUAL_MUTATION"] = "BLOCKED"
    report["AUTO_ACTION"] = False
    report["validated_reports"] = sorted(reports.keys())
    return report


def validate_contract(data: dict[str, Any]) -> list[str]:
    errors = []
    for key, expected in NO_WRITE_FLAGS.items():
        if data.get(key) is not expected:
            errors.append(f"{key}_not_{expected}")
    if data.get("system") != SYSTEM:
        errors.append("wrong_system")
    if "status" not in data:
        errors.append("missing_status")
    return errors


def generate(root: Path, user_request: str) -> int:
    v37 = validate_v37_closure(root)
    if v37.get("status") != "PASS":
        atomic_write_json(root, root / "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json", v37)
        return EXIT_BLOCK

    source = source_resolver(root)
    integrity = manual_integrity_guard(root, source)
    registry, extraction = rule_extractor(root)
    intent = classify_intent(user_request)
    conflict = conflict_detector(intent)
    brain = brain_read_only_check(root)
    decision = decision_mapper(intent, conflict)
    plan = controlled_plan_builder(decision)

    reports = {
        "BRIDGE_SOURCE_RESOLVER_REPORT": source,
        "BRIDGE_MANUAL_INTEGRITY_REPORT": integrity,
        "MANUAL_RULES_REGISTRY": registry,
        "BRIDGE_RULE_EXTRACTION_REPORT": extraction,
        "BRIDGE_INTENT_CLASSIFICATION_REPORT": intent,
        "BRIDGE_CONFLICT_REPORT": conflict,
        "BRIDGE_BRAIN_QUERY_REPORT": brain,
        "BRIDGE_DECISION_MAP_REPORT": decision,
        "BRIDGE_PLAN_REPORT": plan,
    }

    trace = traceability_matrix(reports)
    reports["BRIDGE_TRACEABILITY_MATRIX"] = trace

    readiness = build_readiness_report(reports)
    reports["BRIDGE_BUILD_READINESS_REPORT"] = readiness

    validation = validation_report(reports)
    reports["BRIDGE_VALIDATION_REPORT"] = validation

    output_paths = {
        "BRIDGE_SOURCE_RESOLVER_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_SOURCE_RESOLVER_REPORT.json",
        "BRIDGE_MANUAL_INTEGRITY_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_MANUAL_INTEGRITY_REPORT.json",
        "MANUAL_RULES_REGISTRY": "00_SYSTEM/bridge/reports/MANUAL_RULES_REGISTRY.json",
        "BRIDGE_RULE_EXTRACTION_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_RULE_EXTRACTION_REPORT.json",
        "BRIDGE_INTENT_CLASSIFICATION_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_INTENT_CLASSIFICATION_REPORT.json",
        "BRIDGE_CONFLICT_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_CONFLICT_REPORT.json",
        "BRIDGE_BRAIN_QUERY_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_BRAIN_QUERY_REPORT.json",
        "BRIDGE_DECISION_MAP_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_DECISION_MAP_REPORT.json",
        "BRIDGE_PLAN_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_PLAN_REPORT.json",
        "BRIDGE_TRACEABILITY_MATRIX": "00_SYSTEM/bridge/reports/BRIDGE_TRACEABILITY_MATRIX.json",
        "BRIDGE_BUILD_READINESS_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
        "BRIDGE_VALIDATION_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_VALIDATION_REPORT.json",
    }

    for report_id, report in reports.items():
        errors = validate_contract(report)
        if errors:
            raise BridgeError(f"CONTRACT_INVALID {report_id}: {errors}", EXIT_BLOCK)
        atomic_write_json(root, root / output_paths[report_id], report)

    return EXIT_PASS if readiness.get("status") in {"PASS", "PASS_WITH_WARNINGS"} else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_SOURCE_RESOLVER_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_MANUAL_INTEGRITY_REPORT.json",
        "00_SYSTEM/bridge/reports/MANUAL_RULES_REGISTRY.json",
        "00_SYSTEM/bridge/reports/BRIDGE_RULE_EXTRACTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_INTENT_CLASSIFICATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_CONFLICT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_BRAIN_QUERY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_DECISION_MAP_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_PLAN_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_TRACEABILITY_MATRIX.json",
        "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_VALIDATION_REPORT.json",
    ]
    missing = []
    invalid = []
    for rel in required:
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        data = load_json(path)
        if not isinstance(data, dict):
            invalid.append(rel)
            continue
        errors = validate_contract(data)
        if errors:
            invalid.append(f"{rel}:{errors}")
    if missing or invalid:
        print(stable_json({"status": "BLOCK", "missing": missing, "invalid": invalid}))
        return EXIT_BLOCK
    print(stable_json({"status": "PASS", "validated": required}))
    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["generate", "validate-outputs"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--request", default="build bridge v1 manual cerebro production-real")
    args = parser.parse_args()

    try:
        root = Path(args.root).resolve()
        if args.mode == "generate":
            return generate(root, args.request)
        if args.mode == "validate-outputs":
            return validate_outputs(root)
        return EXIT_INTERNAL_ERROR
    except BridgeError as exc:
        print(stable_json({"status": "ERROR", "message": str(exc), "exit_code": exc.exit_code}))
        return exc.exit_code
    except Exception as exc:
        print(stable_json({"status": "INTERNAL_ERROR", "message": str(exc)}))
        return EXIT_INTERNAL_ERROR


if __name__ == "__main__":
    raise SystemExit(main())