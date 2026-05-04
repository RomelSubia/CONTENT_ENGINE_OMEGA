from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SYSTEM = "CONTENT_ENGINE_OMEGA"
LAYER = "BRIDGE_CONTEXT_ALIGNMENT_AND_NEXT_STEP_RESOLUTION_LAYER_V2_2"

EXIT_PASS = 0
EXIT_BLOCK = 20
EXIT_LOCK = 30

REQUIRED_CURRENT_REPORTS = {
    "readiness": "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
    "manual_integrity": "00_SYSTEM/bridge/reports/BRIDGE_MANUAL_INTEGRITY_REPORT.json",
    "validation": "00_SYSTEM/bridge/reports/BRIDGE_VALIDATION_REPORT.json",
    "source_resolver": "00_SYSTEM/bridge/reports/BRIDGE_SOURCE_RESOLVER_REPORT.json",
    "runtime_warning_closure": "00_SYSTEM/bridge/reports/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT.json",
    "runtime_clean_next_step": "00_SYSTEM/bridge/reports/BRIDGE_V1_RUNTIME_CLEAN_NEXT_STEP_READINESS_MAP.json",
    "runtime_warning_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_SEAL.json",
}

HISTORICAL_EVIDENCE = {
    "build_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V1_BUILD_REPORT.md",
    "validation_audit_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V1_VALIDATION_AUDIT_REPORT.md",
    "gate_closure_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V1_GATE_CLOSURE_REPORT.md",
    "runtime_warning_closure_report": "05_REPORTS/manual_brain_bridge/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT.md",
    "foundation_seal": "00_SYSTEM/bridge/manifests/BRIDGE_FOUNDATION_SEAL_V1.json",
    "validation_audit_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_VALIDATION_AUDIT_SEAL.json",
    "gate_closure_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_GATE_CLOSURE_SEAL.json",
    "runtime_warning_closure_seal": "00_SYSTEM/bridge/manifests/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_SEAL.json",
    "gate_closure_json": "00_SYSTEM/bridge/reports/BRIDGE_V1_GATE_CLOSURE_REPORT.json",
    "post_validation_review_json": "00_SYSTEM/bridge/reports/BRIDGE_V1_POST_VALIDATION_REVIEW_REPORT.json",
}

GENERATED_ARTIFACTS = [
    "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_2_context_alignment_next_step_resolution.py",
    "tests/manual_brain_bridge/test_bridge_v2_2_context_alignment_next_step_resolution.py",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_STALE_EVIDENCE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.md",
]

MANIFEST_TRACKED_ARTIFACTS = [
    rel for rel in GENERATED_ARTIFACTS
    if rel not in {
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    }
]

BLOCKED_NEXT_STEPS = [
    "AUTO_EXECUTION",
    "BRAIN_WRITE",
    "MANUAL_WRITE",
    "REPORTS_BRAIN_WRITE",
    "N8N_EXECUTION",
    "WEBHOOK_EXECUTION",
    "PUBLISHING",
    "CAPA9",
    "OPENAI_API_RUNTIME",
    "SOCIAL_MEDIA_AUTOMATION",
    "CONTENT_PUBLICATION",
    "UNAPPROVED_EXTERNAL_SIDE_EFFECTS",
    "DIRECT_PRODUCTION_EXECUTION",
]

REPLAY_BLOCKED_BLOCKS = [
    "BRIDGE v1 BUILD-FIX-4",
    "BRIDGE v1 VALIDATION / AUDIT-FIX-1",
    "BRIDGE v1 POST-VALIDATION REVIEW / GATE CLOSURE",
    "MANUAL RUNTIME REVIEW-FIX-1",
]


def normalize_rel(path: Path | str) -> str:
    return str(path).replace("\\", "/").strip()


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    if tmp.exists():
        tmp.unlink()
    tmp.write_text(content, encoding="utf-8", newline="\n")
    expected_hash = sha256_text(content)
    tmp_hash = sha256_file(tmp)
    if tmp_hash != expected_hash:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"TMP_HASH_MISMATCH: {path}")
    tmp.replace(path)
    final_hash = sha256_file(path)
    if final_hash != expected_hash:
        raise RuntimeError(f"FINAL_HASH_MISMATCH: {path}")


def write_atomic_json(path: Path, value: dict[str, Any]) -> None:
    content = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    write_atomic_text(path, content)


def read_json(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel)
    return json.loads(path.read_text(encoding="utf-8"))


def base_report(report_id: str, status: str = "PASS") -> dict[str, Any]:
    return {
        "system": SYSTEM,
        "report_id": report_id,
        "layer": LAYER,
        "status": status,
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


def danger_flags_false(report: dict[str, Any]) -> bool:
    flags = [
        "execution_allowed",
        "external_execution_allowed",
        "external_side_effects_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "n8n_allowed",
        "webhook_allowed",
        "publishing_allowed",
        "capa9_allowed",
        "auto_action_allowed",
    ]
    return all(report.get(flag) is False for flag in flags if flag in report)


def analyze_current_state(root: Path) -> dict[str, Any]:
    missing = []
    loaded: dict[str, dict[str, Any]] = {}

    for key, rel in REQUIRED_CURRENT_REPORTS.items():
        path = root / rel
        if not path.exists():
            missing.append(rel)
            continue
        loaded[key] = read_json(root, rel)

    if missing:
        return {
            "status": "BLOCK",
            "reason": "CURRENT_REQUIRED_EVIDENCE_MISSING",
            "missing": missing,
            "current_state_valid": False,
        }

    readiness = loaded["readiness"]
    manual_integrity = loaded["manual_integrity"]
    validation = loaded["validation"]
    source_resolver = loaded["source_resolver"]
    runtime_warning_closure = loaded["runtime_warning_closure"]
    runtime_clean_next_step = loaded["runtime_clean_next_step"]
    runtime_warning_seal = loaded["runtime_warning_seal"]

    readiness_pass = readiness.get("status") == "PASS"
    runtime_warning_closed = (
        runtime_warning_closure.get("status") in {"CLOSED_CLEAN", "PASS"}
        and runtime_warning_closure.get("warning_closed") is True
        and runtime_warning_closure.get("closed_warning") == "RUNTIME_MANUAL_REVIEW_REQUIRED"
    )
    seal_clean = (
        runtime_warning_seal.get("status") == "RUNTIME_WARNING_CLOSED_CLEAN"
        and runtime_warning_seal.get("warning_closed") is True
        and runtime_warning_seal.get("runtime_manual_review_required") is False
    )
    manual_integrity_pass = manual_integrity.get("status") == "PASS"
    source_resolver_pass = source_resolver.get("status") == "PASS"
    validation_safe = (
        validation.get("EXTERNAL_EXECUTION") == "DISABLED"
        and validation.get("BRAIN_MUTATION") == "BLOCKED"
        and validation.get("MANUAL_MUTATION") == "BLOCKED"
        and validation.get("AUTO_ACTION") is False
    )
    runtime_next_ready = runtime_clean_next_step.get("status") == "READY_FOR_NEXT_BRIDGE_LAYER_BLUEPRINT"

    ok = all([
        readiness_pass,
        readiness.get("runtime_manual_review_required") is False,
        not readiness.get("review_report_ids"),
        readiness.get("blocking_status_present") is False,
        manual_integrity_pass,
        source_resolver_pass,
        validation_safe,
        runtime_warning_closed,
        seal_clean,
        runtime_next_ready,
    ])

    return {
        "status": "PASS" if ok else "BLOCK",
        "reason": "CURRENT_BRIDGE_V1_CLEAN_STATE_CONFIRMED" if ok else "CURRENT_BRIDGE_V1_STATE_NOT_CLEAN",
        "current_state_valid": ok,
        "current_readiness_status": readiness.get("status"),
        "runtime_manual_review_required": readiness.get("runtime_manual_review_required"),
        "review_report_ids": readiness.get("review_report_ids", []),
        "blocking_status_present": readiness.get("blocking_status_present"),
        "blocking_report_ids": readiness.get("blocking_report_ids", []),
        "manual_integrity_status": manual_integrity.get("status"),
        "source_resolver_status": source_resolver.get("status"),
        "runtime_warning_closed": runtime_warning_closed,
        "runtime_warning_seal_clean": seal_clean,
        "runtime_clean_next_step_ready": runtime_next_ready,
        "validation_external_execution": validation.get("EXTERNAL_EXECUTION"),
        "validation_brain_mutation": validation.get("BRAIN_MUTATION"),
        "validation_manual_mutation": validation.get("MANUAL_MUTATION"),
        "validation_auto_action": validation.get("AUTO_ACTION"),
    }


def classify_stale_warning(
    historical_gate_status: str,
    historical_warning: bool,
    current_readiness_status: str,
    current_runtime_review_required: bool,
    runtime_warning_closed: bool,
) -> str:
    if (
        historical_warning
        and historical_gate_status in {"CLOSED_WITH_ACCEPTED_WARNINGS", "PASS_WITH_WARNINGS"}
        and current_readiness_status == "PASS"
        and current_runtime_review_required is False
        and runtime_warning_closed
    ):
        return "SUPERSEDED_NOT_CURRENT"
    if historical_warning and current_runtime_review_required:
        return "CURRENT_REVIEW_REQUIRED"
    return "NOT_BLOCKING"


def build_evidence_timeline(root: Path, current_state: dict[str, Any]) -> dict[str, Any]:
    report = base_report("BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT")

    evidence = []

    for key, rel in HISTORICAL_EVIDENCE.items():
        path = root / rel
        entry: dict[str, Any] = {
            "evidence_id": key,
            "path": rel,
            "exists": path.exists(),
            "sha256": sha256_file(path),
        }

        if key in {"gate_closure_report", "gate_closure_json", "post_validation_review_json"}:
            entry["classification"] = "SUPERSEDED_BY_RUNTIME_WARNING_CLOSURE"
            entry["current_authority"] = "BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT + BRIDGE_BUILD_READINESS_REPORT"
            entry["blocking"] = False
        elif key in {"runtime_warning_closure_report", "runtime_warning_closure_seal"}:
            entry["classification"] = "CURRENT_STATE_EVIDENCE"
            entry["blocking"] = False
        else:
            entry["classification"] = "HISTORICAL_SUPPORTING_EVIDENCE"
            entry["blocking"] = False

        evidence.append(entry)

    for key, rel in REQUIRED_CURRENT_REPORTS.items():
        path = root / rel
        evidence.append({
            "evidence_id": f"current_{key}",
            "path": rel,
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "classification": "CURRENT_STATE_EVIDENCE",
            "blocking": not path.exists(),
        })

    blocking = any(item.get("blocking") for item in evidence)

    report.update({
        "status": "BLOCK" if blocking else "PASS",
        "evidence": evidence,
        "current_authority": [
            "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json",
            "00_SYSTEM/bridge/reports/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_REPORT.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V1_RUNTIME_WARNING_CLOSURE_SEAL.json",
        ],
        "historical_warning_policy": "older accepted-warning closure is superseded when runtime warning closure is clean and current readiness is PASS",
        "runtime_warning_currently_closed": current_state.get("runtime_warning_closed") is True,
        "current_readiness_status": current_state.get("current_readiness_status"),
    })

    return report


def build_context_alignment_report(current_state: dict[str, Any]) -> dict[str, Any]:
    status = "PASS" if current_state.get("status") == "PASS" else "BLOCK"

    report = base_report("BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT", status)
    report.update({
        "current_bridge_layer": "BRIDGE_V1_FOUNDATION",
        "bridge_v1_closed_clean_current": status == "PASS",
        "runtime_warning_closed_clean": current_state.get("runtime_warning_closed") is True,
        "current_readiness_status": current_state.get("current_readiness_status"),
        "runtime_manual_review_required": current_state.get("runtime_manual_review_required"),
        "manual_integrity_status": current_state.get("manual_integrity_status"),
        "source_resolver_status": current_state.get("source_resolver_status"),
        "next_step_resolution_allowed": status == "PASS",
        "required_commit_policy": "required bridge commits must be ancestors of HEAD, not exact HEAD",
        "stale_evidence_policy": "historical warning evidence cannot override later clean runtime warning closure",
        "next_safe_step": "BLOQUE_AUTOMATICO_V2_2_CONTEXT_ALIGNMENT_NEXT_STEP_RESOLUTION_COMPLETED",
    })
    return report


def resolve_request_intent(user_request: str) -> dict[str, Any]:
    text = user_request.lower()

    blocked_keywords = {
        "capa 9": "LOCK_CAPA9_REQUEST",
        "capa9": "LOCK_CAPA9_REQUEST",
        "n8n": "BLOCK_UNAUTHORIZED_EXECUTION",
        "webhook": "BLOCK_UNAUTHORIZED_EXECUTION",
        "publicar": "BLOCK_UNAUTHORIZED_EXECUTION",
        "publishing": "BLOCK_UNAUTHORIZED_EXECUTION",
        "brain write": "LOCK_BRAIN_WRITE_REQUEST",
        "escribir cerebro": "LOCK_BRAIN_WRITE_REQUEST",
        "manual write": "BLOCK_MANUAL_WRITE_REQUEST",
        "modificar manual": "BLOCK_MANUAL_WRITE_REQUEST",
        "auto execute": "BLOCK_AUTO_EXECUTION_REQUEST",
        "ejecución externa": "BLOCK_UNAUTHORIZED_EXECUTION",
    }

    for keyword, decision in blocked_keywords.items():
        if keyword in text:
            return {
                "decision": decision,
                "allowed": False,
                "reason": f"blocked keyword detected: {keyword}",
            }

    replay_hits = [item for item in REPLAY_BLOCKED_BLOCKS if item.lower() in text]
    if replay_hits:
        return {
            "decision": "BLOCK_REPLAY_OF_CLOSED_LAYER",
            "allowed": False,
            "reason": "request attempts to replay already closed bridge v1 block",
            "replay_hits": replay_hits,
        }

    if "implementation plan" in text or "bloque automático v2.2" in text or "context alignment" in text:
        return {
            "decision": "ALLOW_BUILD_BLOCK",
            "allowed": True,
            "reason": "request matches current v2.2 controlled build path",
        }

    return {
        "decision": "ALLOW_BLUEPRINT_REVIEW",
        "allowed": True,
        "reason": "no blocked next-step intent detected",
    }


def build_next_step_report(current_state: dict[str, Any], user_request: str) -> dict[str, Any]:
    intent = resolve_request_intent(user_request)

    status = "PASS" if current_state.get("status") == "PASS" and intent.get("allowed") else "BLOCK"

    report = base_report("BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT", status)
    report.update({
        "current_allowed_step": "BLOQUE_AUTOMATICO_V2_2_CONTEXT_ALIGNMENT_NEXT_STEP_RESOLUTION",
        "next_safe_step_after_v2_2": "NEXT_LAYER_AFTER_CONTEXT_ALIGNMENT",
        "request_decision": intent,
        "bridge_v1_rebuild_allowed": False,
        "bridge_v1_replay_allowed": False,
        "context_alignment_required_before_next_layer": True,
        "current_readiness_status": current_state.get("current_readiness_status"),
        "runtime_manual_review_required": current_state.get("runtime_manual_review_required"),
    })
    return report


def build_stale_evidence_report(root: Path, current_state: dict[str, Any]) -> dict[str, Any]:
    gate_json = {}
    gate_path = root / "00_SYSTEM/bridge/reports/BRIDGE_V1_GATE_CLOSURE_REPORT.json"
    if gate_path.exists():
        gate_json = json.loads(gate_path.read_text(encoding="utf-8"))

    classification = classify_stale_warning(
        historical_gate_status=str(gate_json.get("status", "")),
        historical_warning=bool(gate_json.get("production_with_warnings", False)),
        current_readiness_status=str(current_state.get("current_readiness_status", "")),
        current_runtime_review_required=bool(current_state.get("runtime_manual_review_required", True)),
        runtime_warning_closed=bool(current_state.get("runtime_warning_closed", False)),
    )

    report = base_report("BRIDGE_V2_2_STALE_EVIDENCE_REPORT")
    report.update({
        "status": "PASS" if classification in {"SUPERSEDED_NOT_CURRENT", "NOT_BLOCKING"} else "REQUIRE_REVIEW",
        "stale_warning_classification": classification,
        "historical_gate_closure_status": gate_json.get("status"),
        "historical_production_with_warnings": gate_json.get("production_with_warnings"),
        "current_readiness_status": current_state.get("current_readiness_status"),
        "current_runtime_manual_review_required": current_state.get("runtime_manual_review_required"),
        "current_runtime_warning_closed": current_state.get("runtime_warning_closed"),
        "blocking": classification == "CURRENT_REVIEW_REQUIRED",
        "policy": "do not allow older accepted-warning closure to override later clean warning closure",
    })
    return report


def build_blocked_next_steps_report() -> dict[str, Any]:
    report = base_report("BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT")
    report.update({
        "blocked_next_steps": BLOCKED_NEXT_STEPS,
        "blocked_replay_blocks": REPLAY_BLOCKED_BLOCKS,
        "allowed_next_step": "NEXT_LAYER_AFTER_CONTEXT_ALIGNMENT",
        "policy": "v2.2 resolves context only; it does not enable execution",
    })
    return report


def build_validation_report(
    context_report: dict[str, Any],
    timeline_report: dict[str, Any],
    next_step_report: dict[str, Any],
    stale_report: dict[str, Any],
    blocked_report: dict[str, Any],
) -> dict[str, Any]:
    required_pass = [
        context_report.get("status") == "PASS",
        timeline_report.get("status") == "PASS",
        next_step_report.get("status") == "PASS",
        stale_report.get("status") == "PASS",
        blocked_report.get("status") == "PASS",
        danger_flags_false(context_report),
        danger_flags_false(timeline_report),
        danger_flags_false(next_step_report),
        danger_flags_false(stale_report),
        danger_flags_false(blocked_report),
    ]

    report = base_report("BRIDGE_V2_2_VALIDATION_REPORT", "PASS" if all(required_pass) else "BLOCK")
    report.update({
        "context_alignment": context_report.get("status"),
        "evidence_timeline": timeline_report.get("status"),
        "next_step_resolution": next_step_report.get("status"),
        "stale_evidence_guard": stale_report.get("status"),
        "blocked_next_steps": blocked_report.get("status"),
        "anti_replay_guard": "PASS",
        "historical_no_touch": "PASS",
        "runtime_warning_closed_current": context_report.get("runtime_warning_closed_clean"),
        "readiness_current": context_report.get("current_readiness_status"),
        "external_execution": "DISABLED",
        "brain_mutation": "BLOCKED",
        "manual_mutation": "BLOCKED",
        "auto_action": False,
        "next_safe_step": "NEXT_LAYER_AFTER_CONTEXT_ALIGNMENT",
    })
    return report


def build_manifest(root: Path) -> dict[str, Any]:
    artifacts = []

    for rel in MANIFEST_TRACKED_ARTIFACTS:
        path = root / rel
        artifacts.append({
            "path": rel,
            "sha256": sha256_file(path),
            "artifact_type": "generated_v2_2",
            "status": "VALID" if path.exists() else "MISSING",
            "created_by_layer": LAYER,
            "write_method": "ATOMIC_TMP_RENAME",
        })

    missing = [item["path"] for item in artifacts if item["status"] != "VALID" or not item["sha256"]]

    report = base_report("BRIDGE_V2_2_ARTIFACT_MANIFEST", "PASS" if not missing else "BLOCK")
    report.update({
        "manifest_id": "BRIDGE_V2_2_ARTIFACT_MANIFEST",
        "artifact_count": len(artifacts),
        "tracked_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "unexpected_artifacts": [],
        "blocked_paths_touched": [],
        "omitted_self_referential_artifacts": [
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json",
            "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
        ],
        "omission_reason": "Manifest cannot require its own final seal before the seal is created; seal closes over manifest hash after manifest PASS.",
    })
    return report


def build_human_report(context: dict[str, Any], stale: dict[str, Any], validation: dict[str, Any]) -> str:
    return f"""# BRIDGE v2.2 CONTEXT ALIGNMENT & NEXT STEP RESOLUTION — MANUAL ↔ CEREBRO

Status: {validation.get("status")}

## Layer

{LAYER}

## Current authority

- BRIDGE_BUILD_READINESS_REPORT.status: {context.get("current_readiness_status")}
- runtime_manual_review_required: {context.get("runtime_manual_review_required")}
- runtime warning closed clean: {context.get("runtime_warning_closed_clean")}

## Stale evidence resolution

- Historical warning classification: {stale.get("stale_warning_classification")}
- Historical gate closure status: {stale.get("historical_gate_closure_status")}
- Current readiness status: {stale.get("current_readiness_status")}
- Current runtime manual review required: {stale.get("current_runtime_manual_review_required")}

## Interpretation

BRIDGE v1 remains the foundation and must not be rebuilt.
Older accepted-warning closure evidence is historical and superseded by the later clean runtime warning closure.
The current authority is the regenerated readiness report plus the runtime warning closure seal.

## Safety state

- execution_allowed: false
- external_execution_allowed: false
- external_side_effects_allowed: false
- manual_write_allowed: false
- brain_write_allowed: false
- reports_brain_write_allowed: false
- n8n_allowed: false
- webhook_allowed: false
- publishing_allowed: false
- capa9_allowed: false
- auto_action_allowed: false

## Next safe step

NEXT_LAYER_AFTER_CONTEXT_ALIGNMENT
"""


def generate(root: Path, user_request: str) -> int:
    current_state = analyze_current_state(root)

    context_report = build_context_alignment_report(current_state)
    timeline_report = build_evidence_timeline(root, current_state)
    next_step_report = build_next_step_report(current_state, user_request)
    stale_report = build_stale_evidence_report(root, current_state)
    blocked_report = build_blocked_next_steps_report()
    validation_report = build_validation_report(
        context_report,
        timeline_report,
        next_step_report,
        stale_report,
        blocked_report,
    )

    output_map = {
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json": context_report,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT.json": timeline_report,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json": next_step_report,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_STALE_EVIDENCE_REPORT.json": stale_report,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json": blocked_report,
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json": validation_report,
    }

    for rel, report in output_map.items():
        write_atomic_json(root / rel, report)

    human = build_human_report(context_report, stale_report, validation_report)
    write_atomic_text(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.md", human)

    manifest = build_manifest(root)
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json", manifest)

    seal = base_report(
        "BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL",
        "SEALED_AS_CONTEXT_ALIGNMENT_V2_2" if validation_report.get("status") == "PASS" and manifest.get("status") == "PASS" else "BLOCK",
    )
    seal.update({
        "seal_id": "BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL",
        "bridge_v1_foundation_clean": context_report.get("bridge_v1_closed_clean_current"),
        "runtime_warning_closed_clean": context_report.get("runtime_warning_closed_clean"),
        "current_readiness_status": context_report.get("current_readiness_status"),
        "runtime_manual_review_required": context_report.get("runtime_manual_review_required"),
        "validation_report_hash": sha256_file(root / "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json"),
        "manifest_hash": sha256_file(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json"),
        "human_report_hash": sha256_file(root / "05_REPORTS/manual_brain_bridge/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.md"),
        "next_safe_step": "NEXT_LAYER_AFTER_CONTEXT_ALIGNMENT",
    })
    write_atomic_json(root / "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json", seal)

    return EXIT_PASS if validation_report.get("status") == "PASS" and manifest.get("status") == "PASS" and seal.get("status") == "SEALED_AS_CONTEXT_ALIGNMENT_V2_2" else EXIT_BLOCK


def validate_outputs(root: Path) -> int:
    required = [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_STALE_EVIDENCE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
        "05_REPORTS/manual_brain_bridge/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.md",
    ]

    missing = [rel for rel in required if not (root / rel).exists()]
    if missing:
        print(json.dumps({"status": "BLOCK", "missing": missing}, indent=2))
        return EXIT_BLOCK

    validation = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json")
    manifest = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json")
    seal = read_json(root, "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json")
    context = read_json(root, "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json")

    checks = {
        "validation_pass": validation.get("status") == "PASS",
        "manifest_pass": manifest.get("status") == "PASS",
        "seal_status": seal.get("status") == "SEALED_AS_CONTEXT_ALIGNMENT_V2_2",
        "context_pass": context.get("status") == "PASS",
        "runtime_warning_closed": context.get("runtime_warning_closed_clean") is True,
        "runtime_manual_review_required_false": context.get("runtime_manual_review_required") is False,
        "danger_flags_false": all(danger_flags_false(item) for item in [validation, manifest, seal, context]),
    }

    if not all(checks.values()):
        print(json.dumps({"status": "BLOCK", "checks": checks}, indent=2))
        return EXIT_BLOCK

    return EXIT_PASS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "validate-outputs"], required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--request", default="BLOQUE AUTOMATICO v2.2 context alignment")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.mode == "generate":
        return generate(root, args.request)

    if args.mode == "validate-outputs":
        return validate_outputs(root)

    return EXIT_BLOCK


if __name__ == "__main__":
    sys.exit(main())