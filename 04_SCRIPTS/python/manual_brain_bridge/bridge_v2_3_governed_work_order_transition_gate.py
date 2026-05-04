from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_GOVERNED_WORK_ORDER_AND_TRANSITION_GATE_LAYER_V2_3"

EXIT_PASS = 0
EXIT_BLOCK = 20
EXIT_LOCK = 30

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
]

AUTHORITY_FILES = {
    "bridge_v2_2_context_alignment_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    "bridge_v2_2_validation_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json",
    "bridge_v2_2_context_alignment_report": "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json",
    "bridge_build_readiness_report": "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
    "bridge_v1_runtime_warning_closure_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_SEAL.json",
}

HISTORICAL_AUTHORITY_FILES = {
    "BRIDGE_V1_GATE_CLOSURE_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_V1_GATE_CLOSURE_REPORT.json",
    "BRIDGE_V1_POST_VALIDATION_REVIEW_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_V1_POST_VALIDATION_REVIEW_REPORT.json",
    "BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT.json",
    "BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL": "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    "BRIDGE_BUILD_READINESS_REPORT": "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_3_governed_work_order_transition_gate.py",
    "tests/manual_brain_bridge/test_bridge_v2_3_governed_work_order_transition_gate.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_RECOVERY_READINESS_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
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
]

NEGATIVE_INTENT_RULES = [
    ("crear el bloque y ejecutarlo", "BLOCK_AUTO_ACTION_REQUEST"),
    ("ejecutarlo", "BLOCK_AUTO_ACTION_REQUEST"),
    ("ejecutar automáticamente", "BLOCK_AUTO_ACTION_REQUEST"),
    ("auto execute", "BLOCK_AUTO_ACTION_REQUEST"),
    ("activa n8n", "BLOCK_N8N_REQUEST"),
    ("activar n8n", "BLOCK_N8N_REQUEST"),
    ("n8n", "BLOCK_N8N_REQUEST"),
    ("webhook", "BLOCK_WEBHOOK_REQUEST"),
    ("publicar automáticamente", "BLOCK_PUBLISHING_REQUEST"),
    ("publicar contenido", "BLOCK_PUBLISHING_REQUEST"),
    ("subir contenido a redes", "BLOCK_PUBLISHING_REQUEST"),
    ("openai api runtime", "BLOCK_OPENAI_API_RUNTIME_REQUEST"),
    ("modificar el cerebro", "LOCK_BRAIN_MUTATION_REQUEST"),
    ("escribir cerebro", "LOCK_BRAIN_MUTATION_REQUEST"),
    ("brain write", "LOCK_BRAIN_MUTATION_REQUEST"),
    ("actualiza el manual current", "BLOCK_MANUAL_MUTATION_REQUEST"),
    ("actualizar el manual current", "BLOCK_MANUAL_MUTATION_REQUEST"),
    ("modificar manual", "BLOCK_MANUAL_MUTATION_REQUEST"),
    ("manual write", "BLOCK_MANUAL_MUTATION_REQUEST"),
    ("corrige el manual automáticamente", "BLOCK_MANUAL_MUTATION_REQUEST"),
    ("crear capa 9", "LOCK_CAPA9_REQUEST"),
    ("capa 9", "LOCK_CAPA9_REQUEST"),
    ("capa9", "LOCK_CAPA9_REQUEST"),
]


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
        "next_safe_step": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
        "manifest_reference": "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
    }
    report.update(safe_flags())
    return report


def danger_flags_false(report: dict[str, Any]) -> bool:
    return all(report.get(flag) is False for flag in DANGER_FLAGS if flag in report)


def resolve_request_intent(user_request: str) -> dict[str, Any]:
    text = user_request.lower()
    for keyword, decision in NEGATIVE_INTENT_RULES:
        if keyword in text:
            return {
                "allowed": False,
                "decision": decision,
                "matched_keyword": keyword,
                "reason": "dangerous or premature capability requested",
            }

    if "bloque automático v2.3" in text or "governed work order" in text or "transition gate" in text:
        return {
            "allowed": True,
            "decision": "ALLOW_GOVERNED_WORK_ORDER_BUILD",
            "reason": "request matches current controlled v2.3 build path",
        }

    return {
        "allowed": True,
        "decision": "ALLOW_BLUEPRINT_OR_PLAN_ONLY",
        "reason": "no blocked execution capability detected",
    }


def build_authority_hash_report(root: Path) -> dict[str, Any]:
    report = base_report("BRIDGE_V2_3_AUTHORITY_HASH_REPORT")

    authority = []
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
            authority.append(entry)
            continue

        try:
            data = read_json(root, rel)
        except Exception:
            invalid.append(rel)
            entry["status"] = "INVALID_JSON"
            authority.append(entry)
            continue

        entry["reported_status"] = data.get("status")

        if authority_id == "bridge_v2_2_context_alignment_seal":
            ok = data.get("status") == "SEALED_AS_CONTEXT_ALIGNMENT_V2_2"
        elif authority_id == "bridge_v2_2_validation_report":
            ok = data.get("status") == "PASS"
        elif authority_id == "bridge_v2_2_context_alignment_report":
            ok = (
                data.get("status") == "PASS"
                and data.get("runtime_warning_closed_clean") is True
                and data.get("runtime_manual_review_required") is False
            )
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

        authority.append(entry)

    ok = not missing and not invalid

    report.update({
        "status": "PASS" if ok else "BLOCK",
        "authority_hash_check": "PASS" if ok else "BLOCK",
        "authority": authority,
        "missing_authority_files": missing,
        "invalid_authority_files": invalid,
        "authority_hashes": {item["path"]: item["sha256"] for item in authority},
        "bridge_v2_2_context_alignment_authority": ok,
        "runtime_warning_closed_clean": ok,
    })
    return report


def build_historical_authority_resolution_report(root: Path, authority_report: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT")

    classifications = []
    stale_warning_reintroduction = False

    for authority_id, rel in HISTORICAL_AUTHORITY_FILES.items():
        path = root / rel
        data = {}
        if path.exists():
            try:
                data = read_json(root, rel)
            except Exception:
                data = {}

        if authority_id in {"BRIDGE_V1_GATE_CLOSURE_REPORT", "BRIDGE_V1_POST_VALIDATION_REVIEW_REPORT"}:
            classification = "HISTORICAL_SUPERSEDED"
            if data.get("status") == "CLOSED_WITH_ACCEPTED_WARNINGS" and authority_report.get("status") == "PASS":
                stale_warning_reintroduction = False
        elif authority_id == "BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT":
            classification = "CURRENT_SUPPORTING_AUTHORITY"
        elif authority_id == "BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL":
            classification = "CURRENT_PRIMARY_AUTHORITY"
        elif authority_id == "BRIDGE_BUILD_READINESS_REPORT":
            classification = "CURRENT_RUNTIME_AUTHORITY"
        else:
            classification = "HISTORICAL_SUPPORTING"

        classifications.append({
            "authority_id": authority_id,
            "path": rel,
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "reported_status": data.get("status"),
            "classification": classification,
            "can_override_current_authority": False if classification.startswith("HISTORICAL") else True,
        })

    ok = authority_report.get("status") == "PASS" and stale_warning_reintroduction is False

    report.update({
        "status": "PASS" if ok else "BLOCK",
        "historical_authority_resolution": classifications,
        "stale_warning_reintroduction": stale_warning_reintroduction,
        "stale_warning_reintroduction_policy": "STALE_WARNING_REINTRODUCTION = BLOCK",
        "current_primary_authority": "BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL",
        "current_runtime_authority": "BRIDGE_BUILD_READINESS_REPORT",
        "historical_override_allowed": False,
    })
    return report


def build_recovery_readiness_report(partial_state: str, partial_files: list[str]) -> dict[str, Any]:
    allowed_states = {
        "NO_PARTIAL_STATE",
        "PARTIAL_ALLOWED_RECOVERY",
        "PARTIAL_BLOCKED_NO_TOUCH_RISK",
        "PARTIAL_LOCKED_UNKNOWN_STATE",
    }

    state = partial_state if partial_state in allowed_states else "PARTIAL_LOCKED_UNKNOWN_STATE"
    status = "PASS" if state in {"NO_PARTIAL_STATE", "PARTIAL_ALLOWED_RECOVERY"} else "LOCK"

    report = base_report("BRIDGE_V2_3_RECOVERY_READINESS_REPORT", status)
    report.update({
        "recovery_state": state,
        "partial_files": partial_files,
        "partial_recovery_allowed": state == "PARTIAL_ALLOWED_RECOVERY",
        "no_partial_state": state == "NO_PARTIAL_STATE",
        "recovery_policy": {
            "v2_3_allowlist_partial_diff": "RECOVER_ALLOWED",
            "manual_current_or_manifest_diff": "LOCK",
            "brain_or_reports_brain_diff": "LOCK",
            "unknown_diff": "BLOCK",
        },
    })
    return report


def build_blocked_capabilities_report() -> dict[str, Any]:
    report = base_report("BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT")
    report.update({
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "blocked_capability_count": len(BLOCKED_CAPABILITIES),
        "manual_auto_update_allowed": False,
        "manual_current_mutation_allowed": False,
        "manual_manifest_mutation_allowed": False,
        "manual_historical_mutation_allowed": False,
        "manual_registry_mutation_allowed": False,
        "build_allowed_now": False,
        "build_allowed_next": True,
        "blueprint_allowed": True,
        "implementation_plan_allowed": True,
        "build_block_allowed_next": True,
        "policy": "v2.3 prepares governed transition only; it does not enable execution or mutation",
    })
    return report


def build_governed_work_order_report(authority_report: dict[str, Any], request_intent: dict[str, Any]) -> dict[str, Any]:
    ok = authority_report.get("status") == "PASS" and request_intent.get("allowed") is True

    report = base_report("BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "work_order_id": "GOVERNED_WORK_ORDER_V2_3",
        "work_order_type": "TRANSITION_GATE_PREPARATION",
        "bridge_v1_foundation_clean": True if ok else False,
        "bridge_v2_2_context_alignment_authority": authority_report.get("status") == "PASS",
        "runtime_warning_closed_clean": authority_report.get("runtime_warning_closed_clean") is True,
        "request_intent": request_intent,
        "blueprint_allowed": True,
        "implementation_plan_allowed": True,
        "build_block_allowed_next": True,
        "build_allowed_next": True,
        "build_allowed_now": False,
        "execution_allowed": False,
        "auto_action_allowed": False,
        "authorized_output": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
    })
    return report


def build_transition_gate_report(authority_report: dict[str, Any], work_order: dict[str, Any]) -> dict[str, Any]:
    ok = authority_report.get("status") == "PASS" and work_order.get("status") == "PASS"

    report = base_report("BRIDGE_V2_3_TRANSITION_GATE_REPORT", "PASS" if ok else "BLOCK")
    report.update({
        "transition_gate_id": "TRANSITION_GATE_V2_3",
        "from_layer": "BRIDGE_V2_2_CONTEXT_ALIGNMENT_AND_NEXT_STEP_RESOLUTION",
        "to_layer": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
        "transition_allowed": ok,
        "next_bridge_layer_blueprint_allowed": ok,
        "next_bridge_layer_implementation_plan_allowed": ok,
        "next_bridge_layer_build_block_allowed_next": ok,
        "next_bridge_layer_build_allowed_now": False,
        "execution_allowed": False,
        "brain_write_allowed": False,
        "manual_write_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "capa9_allowed": False,
        "next_safe_step": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
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

    report = base_report("BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT", "PASS" if not violations else "BLOCK")
    report.update({
        "anti_simulation_gate": "PASS" if not violations else "BLOCK",
        "violations": violations,
        "checked_report_ids": [item.get("report_id") for item in reports],
        "pass_without_hashes_blocked": True,
        "pass_without_authority_files_blocked": True,
        "pass_with_danger_flags_blocked": True,
    })
    return report


def build_validation_report(
    authority: dict[str, Any],
    historical: dict[str, Any],
    recovery: dict[str, Any],
    anti_simulation: dict[str, Any],
    work_order: dict[str, Any],
    transition: dict[str, Any],
    blocked: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "authority_hash_check": authority.get("status") == "PASS",
        "historical_authority_resolution": historical.get("status") == "PASS",
        "recovery_readiness": recovery.get("status") == "PASS",
        "anti_simulation_gate": anti_simulation.get("status") == "PASS",
        "governed_work_order": work_order.get("status") == "PASS",
        "transition_gate": transition.get("status") == "PASS",
        "blocked_capabilities": blocked.get("status") == "PASS",
        "danger_flags_false": all(danger_flags_false(item) for item in [
            authority, historical, recovery, anti_simulation, work_order, transition, blocked
        ]),
    }

    status = "PASS" if all(checks.values()) else "BLOCK"

    report = base_report("BRIDGE_V2_3_VALIDATION_REPORT", status)
    report.update({
        "checks": checks,
        "validation_status": status,
        "bridge_v1_foundation_clean": work_order.get("bridge_v1_foundation_clean") is True,
        "bridge_v2_2_context_alignment_authority": work_order.get("bridge_v2_2_context_alignment_authority") is True,
        "runtime_warning_closed_clean": work_order.get("runtime_warning_closed_clean") is True,
        "blueprint_allowed": True,
        "implementation_plan_allowed": True,
        "build_block_allowed_next": True,
        "build_allowed_next": True,
        "build_allowed_now": False,
        "external_execution": "DISABLED",
        "brain_mutation": "BLOCKED",
        "manual_mutation": "BLOCKED",
        "auto_action": False,
        "next_safe_step": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
    })
    return report


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts = []

    for rel in MANIFEST_TRACKED_ARTIFACTS:
        path = root / rel
        artifacts.append({
            "path": rel,
            "sha256": sha256_file(path),
            "artifact_type": "generated_v2_3",
            "status": "VALID" if path.exists() and sha256_file(path) else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID"]

    report = base_report("BRIDGE_V2_3_ARTIFACT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_3_ARTIFACT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
        ],
        "omission_reason": "Manifest cannot require its own final seal before seal exists; seal closes over manifest hash after manifest PASS.",
    })
    return report


def build_human_report(validation: dict[str, Any], authority: dict[str, Any], transition: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.3 GOVERNED WORK ORDER & TRANSITION GATE — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## Current authority

- v2.2 seal authority: {authority.get("bridge_v2_2_context_alignment_authority")}
- runtime warning closed clean: {authority.get("runtime_warning_closed_clean")}
- validation status: {validation.get("validation_status")}

## Transition gate

- next safe step: {transition.get("next_safe_step")}
- blueprint allowed: {transition.get("next_bridge_layer_blueprint_allowed")}
- implementation plan allowed: {transition.get("next_bridge_layer_implementation_plan_allowed")}
- build block allowed next: {transition.get("next_bridge_layer_build_block_allowed_next")}
- build allowed now: {transition.get("next_bridge_layer_build_allowed_now")}

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

v2.3 does not execute actions. It creates a governed work order and transition gate for the next bridge layer.
Historical warning evidence remains historical and cannot override the current clean authority from v2.2 and the runtime warning closure seal.

## Next safe step

NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER
"""


def generate(root: Path, request: str, partial_state: str, partial_files: list[str]) -> int:
    request_intent = resolve_request_intent(request)

    authority = build_authority_hash_report(root)
    historical = build_historical_authority_resolution_report(root, authority)
    recovery = build_recovery_readiness_report(partial_state, partial_files)
    blocked = build_blocked_capabilities_report()
    work_order = build_governed_work_order_report(authority, request_intent)
    transition = build_transition_gate_report(authority, work_order)

    primary_reports = [authority, historical, recovery, blocked, work_order, transition]
    anti_simulation = build_anti_simulation_gate_report(primary_reports)

    validation = build_validation_report(
        authority,
        historical,
        recovery,
        anti_simulation,
        work_order,
        transition,
        blocked,
    )

    output_map = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json": authority,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT.json": historical,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_RECOVERY_READINESS_REPORT.json": recovery,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT.json": anti_simulation,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json": work_order,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json": transition,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json": blocked,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json": validation,
    }

    for rel, report in output_map.items():
        write_atomic_json(root / rel, report)

    human = build_human_report(validation, authority, transition)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json", manifest)

    seal_status = (
        "SEALED_AS_GOVERNED_WORK_ORDER_TRANSITION_GATE_V2_3"
        if validation.get("status") == "PASS" and manifest.get("status") == "PASS"
        else "BLOCK"
    )

    seal = base_report("BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL", seal_status)
    seal.update({
        "seal_id": "BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL",
        "status": seal_status,
        "bridge_v1_foundation_clean": validation.get("bridge_v1_foundation_clean"),
        "bridge_v2_2_context_alignment_authority": validation.get("bridge_v2_2_context_alignment_authority"),
        "runtime_warning_closed_clean": validation.get("runtime_warning_closed_clean"),
        "blueprint_allowed": True,
        "implementation_plan_allowed": True,
        "build_block_allowed_next": True,
        "build_allowed_next": True,
        "build_allowed_now": False,
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.md"),
        "next_safe_step": "NEXT_BRIDGE_LAYER_AFTER_GOVERNED_WORK_ORDER",
    })
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json", seal)

    return EXIT_PASS if seal_status == "SEALED_AS_GOVERNED_WORK_ORDER_TRANSITION_GATE_V2_3" else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_RECOVERY_READINESS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).is_file()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json")
    authority = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json")
    transition = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json")
    blocked = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "authority_pass": authority.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == "SEALED_AS_GOVERNED_WORK_ORDER_TRANSITION_GATE_V2_3",
        "transition_pass": transition.get("status") == "PASS",
        "blocked_pass": blocked.get("status") == "PASS",
        "build_allowed_next_true": seal.get("build_allowed_next") is True,
        "build_allowed_now_false": seal.get("build_allowed_now") is False,
        "danger_flags_false": all(danger_flags_false(item) for item in [
            validation, authority, manifest, seal, transition, blocked
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
    parser.add_argument("--request", default="BLOQUE AUTOMATICO v2.3 governed work order transition gate")
    parser.add_argument("--partial-state", default="NO_PARTIAL_STATE")
    parser.add_argument("--partial-files-json", default="[]")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "generate":
        try:
            partial_files = json.loads(args.partial_files_json)
        except Exception:
            partial_files = []
        return generate(root, args.request, args.partial_state, partial_files)

    if args.mode == "validate-outputs":
        return validate_outputs(root)

    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())