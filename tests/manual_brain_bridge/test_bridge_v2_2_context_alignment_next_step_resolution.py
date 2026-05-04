from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_2_context_alignment_next_step_resolution.py"

spec = importlib.util.spec_from_file_location("bridge_v2_2", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_2_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_STALE_EVIDENCE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_2_context_alignment_is_pass_and_runtime_warning_clean():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["bridge_v1_closed_clean_current"] is True
    assert report["runtime_warning_closed_clean"] is True
    assert report["current_readiness_status"] == "PASS"
    assert report["runtime_manual_review_required"] is False


def test_v2_2_current_readiness_is_authority():
    readiness = j("00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json")
    context = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json")
    assert readiness["status"] == "PASS"
    assert context["current_readiness_status"] == readiness["status"]
    assert readiness["runtime_manual_review_required"] is False


def test_v2_2_timeline_marks_old_warning_closure_as_superseded():
    timeline = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_EVIDENCE_TIMELINE_REPORT.json")
    superseded = [
        item for item in timeline["evidence"]
        if item.get("classification") == "SUPERSEDED_BY_RUNTIME_WARNING_CLOSURE"
    ]
    assert superseded
    assert all(item["blocking"] is False for item in superseded)


def test_v2_2_stale_warning_not_current():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_STALE_EVIDENCE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["stale_warning_classification"] in {"SUPERSEDED_NOT_CURRENT", "NOT_BLOCKING"}
    assert report["blocking"] is False


def test_v2_2_next_step_resolution_does_not_enable_execution():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["execution_allowed"] is False
    assert report["brain_write_allowed"] is False
    assert report["manual_write_allowed"] is False
    assert report["capa9_allowed"] is False


def test_v2_2_blocked_next_steps_include_external_runtime_and_capa9():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json")
    blocked = set(report["blocked_next_steps"])
    assert "CAPA9" in blocked
    assert "N8N_EXECUTION" in blocked
    assert "WEBHOOK_EXECUTION" in blocked
    assert "PUBLISHING" in blocked
    assert "BRAIN_WRITE" in blocked
    assert "MANUAL_WRITE" in blocked


def test_v2_2_validation_report_is_pass_and_safe():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["external_execution"] == "DISABLED"
    assert report["brain_mutation"] == "BLOCKED"
    assert report["manual_mutation"] == "BLOCKED"
    assert report["auto_action"] is False


def test_v2_2_manifest_contains_all_generated_artifacts_with_hashes():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_2_manifest_does_not_claim_historical_v1_artifacts_as_generated():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json")
    generated = {item["path"] for item in manifest["artifacts"]}
    assert "00_SYSTEM/bridge/reports/BRIDGE_V1_GATE_CLOSURE_REPORT.json" not in generated
    assert "00_SYSTEM/bridge/manifests/BRIDGE_FOUNDATION_SEAL_V1.json" not in generated


def test_v2_2_seal_is_context_alignment_seal():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json")
    assert seal["status"] == "SEALED_AS_CONTEXT_ALIGNMENT_V2_2"
    assert seal["bridge_v1_foundation_clean"] is True
    assert seal["runtime_warning_closed_clean"] is True
    assert seal["runtime_manual_review_required"] is False


def test_v2_2_classify_stale_warning_supersedes_old_warning():
    result = bridge.classify_stale_warning(
        historical_gate_status="CLOSED_WITH_ACCEPTED_WARNINGS",
        historical_warning=True,
        current_readiness_status="PASS",
        current_runtime_review_required=False,
        runtime_warning_closed=True,
    )
    assert result == "SUPERSEDED_NOT_CURRENT"


def test_v2_2_resolve_blocks_capa9():
    result = bridge.resolve_request_intent("crear CAPA 9")
    assert result["allowed"] is False
    assert result["decision"] == "LOCK_CAPA9_REQUEST"


def test_v2_2_resolve_blocks_n8n_webhook_publishing():
    for text in ["activar n8n", "ejecutar webhook", "publicar contenido"]:
        result = bridge.resolve_request_intent(text)
        assert result["allowed"] is False
        assert result["decision"] == "BLOCK_UNAUTHORIZED_EXECUTION"


def test_v2_2_resolve_blocks_replay_of_closed_layer():
    result = bridge.resolve_request_intent("BRIDGE v1 BUILD-FIX-4")
    assert result["allowed"] is False
    assert result["decision"] == "BLOCK_REPLAY_OF_CLOSED_LAYER"


def test_v2_2_resolve_allows_current_controlled_build_path():
    result = bridge.resolve_request_intent("BLOQUE AUTOMÁTICO v2.2 context alignment")
    assert result["allowed"] is True
    assert result["decision"] == "ALLOW_BUILD_BLOCK"


def test_v2_2_current_state_analyzer_fails_closed_when_required_reports_missing(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    state = bridge.analyze_current_state(root)
    assert state["status"] == "BLOCK"
    assert state["current_state_valid"] is False
    assert state["missing"]


def test_v2_2_danger_flags_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_CONTEXT_ALIGNMENT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_NEXT_STEP_RESOLUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_BLOCKED_NEXT_STEPS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_2_VALIDATION_REPORT.json",
    ]:
        assert bridge.danger_flags_false(j(rel)) is True

def test_v2_2_manifest_omits_self_referential_manifest_and_seal():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json")
    omitted = set(manifest["omitted_self_referential_artifacts"])
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_ARTIFACT_MANIFEST.json" in omitted
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL.json" in omitted
    assert manifest["status"] == "PASS"
